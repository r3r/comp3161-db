__author__ = 'RiteshReddy'
import __setup_path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text
import datetime, uuid
from functools import wraps
from flask import abort

urls = {"branch1": "mysql://root:root@localhost/compustore_branch1",
        "branch2": "mysql://root:root@localhost/compustore_branch2",
        "branch3": "mysql://root:root@localhost/compustore_branch3",
        "online": "mysql://root:root@localhost/compustore_online"}

branch_titles = {"branch1": "Kingston Branch",
                 "branch2": "Ocho Rios Branch",
                 "branch3": "Montego Bay Branch",
                 "online": "Online Store"}


def validate_branch(f):
    @wraps(f)
    def wrapper(branch, *args, **kwargs):
        if not branch in branch_titles:
            abort(404)
        else:
            return f(branch, *args, **kwargs)

    return wrapper


def get_engine(to, echo=False):
    url = urls.get(to, None)
    if url is None:
        return url
    engine = create_engine(url, echo=echo)
    metadata = MetaData(bind=engine)
    return engine


def get_customers(offset, maxResults=30, where="1", engine=get_engine("online")):
    return engine.execute(text('select * from customer WHERE :where LIMIT :offset, :maxResults'),
                          {"where": where, "offset": offset, "maxResults": maxResults}).fetchall()


def make_branch_purchase(engine, laptops):
    """

    :param engine: Database engine object
    :param laptops: dictionary of laptop_ids and quantity of each => {(vendor,model) : qty}
    :return: order_id if successful, error message otherwise
    """
    connection = engine.connect()
    transaction = connection.begin()
    try:
        id = connection.execute(text("SELECT MAX(orderid) FROM `store_purchases`")).first()[0]
        if id is None:
            id = 1
        else:
            id = int(id) + 1
        insert_purchase = text("INSERT INTO `store_purchases` (`orderid`, `purchase_date`) VALUES(:id, :date)")
        connection.execute(insert_purchase, {"id": str(id), "date": datetime.date.today().isoformat()})
        for laptop, (qty, cost) in laptops.items():
            insert_line_item = text(
                "INSERT INTO `line_item` (`vendor`, `model`, `orderid`, `quantity`, `line_total`) VALUES (:vendor, :model, :orderid, :quantity, :line_total)")
            connection.execute(insert_line_item,
                               {'vendor': laptop[0], 'model': laptop[1], 'orderid': id, 'quantity': qty,
                                "line_total": int(qty) * float(cost)})
            connection.execute(text(
                "UPDATE `inventory` SET `quantity` = `quantity` - :quantity WHERE `vendor`=:vendor and `model`=:model"),
                               {'quantity': qty, "vendor": laptop[0], "model": laptop[1]})
        transaction.commit()
        return id, None
    except Exception, e:
        transaction.rollback()
        return None, e.message


def make_online_purchase(customer_id, laptops):
    """

    :param engine: Connection engine
    :param customer_id: customer purchasing this item
    :param laptops: dictionary of laptops -> qty + branch => {(vendor, model):(qty, branch, cost)}
    :return: order_id, tracking_id
    """
    connections = {}
    transactions = {}
    for id in urls.keys():
        connections[id] = get_engine(id).connect()
        transactions[id] = connections[id].begin()
    try:
        id = connections['online'].execute(text("SELECT MAX(orderid) FROM `online_purchases`")).first()[0]
        if id is None:
            id = 1
        else:
            id = int(id) + 1
        trackingno = str(uuid.uuid4())
        insert_purchase = text(
            "INSERT INTO `online_purchases` (`orderid`, `purchase_date`, `trackingno`, `custid`) VALUES(:id, :date, :trackingno, :custid)")
        connections['online'].execute(insert_purchase, {"id": str(id), "date": datetime.date.today().isoformat(),
                                                        "trackingno": trackingno, "custid": customer_id})
        for (vendor, model), (qty, branch, cost) in laptops.items():
            insert_line_item = text(
                "INSERT INTO `line_item` (`vendor`, `model`, `orderid`, `quantity`, `branch_id`, `line_total`) VALUES (:vendor, :model, :orderid, :quantity, :branch_id, :line_total)")
            connections['online'].execute(insert_line_item, {'vendor': vendor, 'model': model, 'orderid': id,
                                                             'quantity': qty, "branch_id": branch,
                                                             "line_total": int(qty) * float(cost)})
            connections[branch].execute(text(
                "UPDATE `inventory` SET `quantity` = `quantity` - :quantity WHERE `vendor`=:vendor and `model`=:model"),
                                        {'quantity': qty, "vendor": vendor, "model": model})
        for transaction in transactions.values():
            transaction.commit()
        return id, trackingno
    except Exception, e:
        for transaction in transactions.values():
            transaction.rollback()
        return None, e


def get_laptops(engine, offset=0, maxResults=50):
    connection = engine.connect()
    return connection.execute(text("SELECT * FROM `inventory` LIMIT :offset, :maxResults"),
                              {"offset": offset, "maxResults": maxResults}).fetchall()


def get_laptop(engine, vendor, model):
    return engine.execute(text("SELECT * FROM `inventory` WHERE `vendor`=:vendor and `model`=:model"),
                          {"vendor": vendor, "model": model}).first()


def get_customer(custid, engine=get_engine("online")):
    string = text(
        "SELECT cust.*, cc.ccnumber, cc.address as ccaddress, cc.expirydate, cc.securitycode FROM `customer` as cust  join `creditcards` as cc on cust.custid=cc.custid WHERE cust.`custid` = :id")
    return engine.execute(string, {"id": custid}).first()


def get_branch_order(engine, orderid):
    order = engine.execute(text("SELECT * FROM `store_purchases` WHERE `orderid`=:orderid"),
                           {"orderid": orderid}).first()
    if order is None:
        return None
    line_items = engine.execute(text("SELECT * FROM `line_item` WHERE `orderid`=:orderid"),
                                {"orderid": orderid}).fetchall()
    return {"order": order, "line_items": line_items}


def get_online_order(orderid, engine=get_engine("online")):
    order = engine.execute(text("SELECT * FROM `online_purchases` WHERE `orderid`=:orderid"),
                           {"orderid": orderid}).first()
    if order is None:
        return None
    line_items = engine.execute(text("SELECT * FROM `line_item` WHERE `orderid`=:orderid"),
                                {"orderid": orderid}).fetchall()
    return {"order": order, "line_items": line_items}


def get_all_branch_orders(engine):
    orders = engine.execute(text("SELECT * FROM `store_purchases`")).fetchall()
    if orders is None:
        return None
    result = []
    for order in orders:
        line_items = engine.execute(text("SELECT * FROM `line_item` WHERE `orderid`=:orderid"),
                                    {"orderid": order[0]}).fetchall()
        result.append({"order": order, "line_items": line_items})
    return result


def get_all_online_orders(engine=get_engine("online")):
    orders = engine.execute(text("SELECT * FROM `online_purchases`")).fetchall()
    if orders is None:
        return None
    result = []
    for order in orders:
        line_items = engine.execute(text("SELECT * FROM `line_item` WHERE `orderid`=:orderid"),
                                    {"orderid": order[0]}).fetchall()
        result.append({"order": order, "line_items": line_items})
    return result


def get_customer_order(custid, engine=get_engine("online")):
    order_ids = engine.execute(text("SELECT `orderid` from `online_purchases` WHERE `custid`=:custid"),
                               {"custid": custid}).fetchall()
    orders = map(lambda x: get_online_order(x[0]), order_ids)
    return {"custid": custid, "orders": orders}


def register_user(first_name, last_name, address, phone, email, passwd, ccnumber, security_code, expiry_date,
                  engine=get_engine("online")):
    """

    :param first_name:
    :param last_name:
    :param address:
    :param phone:
    :param email:
    :param passwd:
    :param ccnumber:
    :param security_code:
    :param expiry_date:
    :param engine:
    :return: Customer ID (Username) and Full Name or NONE + error message
    """
    connection = engine.connect()
    transaction = connection.begin()
    id = connection.execute(text("SELECT MAX(custid) FROM `customer`")).first()[0]
    if id is None:
        id = 1
    else:
        id = int(id) + 1
    try:
        insert_customer = text(
            "INSERT INTO `customer` VALUES(:custid, :first_name, :last_name, :address, :phone, :email, :passwd)")
        connection.execute(insert_customer,
                           {"custid": id, "first_name": first_name, "last_name": last_name, "address": address,
                            "phone": phone, "email": email,
                            "passwd": passwd})
        insert_creditcard = text(
            "INSERT INTO `creditcards` VALUES(:ccnumber, :address, :securitycode, :expirydate, :custid)")
        connection.execute(insert_creditcard, {"ccnumber": ccnumber, "address": address, "securitycode": security_code,
                                               "expirydate": expiry_date, "custid": id})
        transaction.commit()
        return id, first_name + " " + last_name
    except Exception, e:
        transaction.rollback()
        return None, e.message


def add_inventory(engine, qty, vendor, model, price, ram, hdd, screensize):
    insert_inventory = text("INSERT INTO `inventory` VALUES (:qty, :vendor, :model, :price, :ram, :hdd, :screensize)")
    connection = engine.connect()
    transaction = connection.begin()
    try:
        connection.execute(insert_inventory,
                           {"qty": qty, "vendor": vendor, "model": model, "price": price, "ram": ram, "hdd": hdd,
                            "screensize": screensize})
        transaction.commit()
        return True, None
    except Exception, e:
        transaction.rollback()
        return False, e.message


def get_customer_purchase_report_date(start_date, end_date, engine=get_engine("online")):
    return engine.execute(text("CALL getCustomerTotalsDate(:start_date, :end_date);"),
                          {"start_date": start_date, "end_date": end_date}).fetchall()


def get_customer_purchase_report_amount(amount, engine=get_engine("online")):
    return engine.execute(text("CALL getCustomerTotalsThreshold(:amount);"), {"amount": amount}).fetchall()


def get_laptops_by_top_sales(engine):
    return engine.execute(text("CALL getLaptopsByTopSale()")).fetchall()


def get_num_sales_branch(engine, start_date, end_date, ):
    return engine.execute(text("SELECT getNumberOfSales(:start_date, :end_date);"),
                          {"start_date": start_date, "end_date": end_date}).first()[0]


def check_creditcard_details(ccnumber, address, securitycode, expirydate):
    engine = create_engine("mysql://root:root@localhost/compustore_bank", echo=False)
    card = engine.execute(text("SELECT * FROM creditcards WHERE ccnumber=:ccnumber"), {"ccnumber": ccnumber}).first()
    if card is None:
        return False
    return str(ccnumber) == str(card.ccnumber) and str(address) == str(card.address) and str(securitycode) == str(
        card.securitycode) and str(expirydate) == str(card.expirydate)



def get_user_password(engine=get_engine("online"), where_user_is="1"):
    string = text("SELECT `passwd` FROM `customer` WHERE `custid` = :id")
    res = engine.execute(string, {"id": where_user_is}).first()
    if not res is None:
        return res[0]
    else:
        return None


def test_get_customers():
    print "********test_get_customers********"
    print get_customers(1)

def test_make_branch_purchase():
    print "********test_make_branch_purchase********"
    engine = get_engine("branch1")
    print make_branch_purchase(engine, {('Alienware', 'EPY'): (2, 250), ('Alienware', 'GKWV46K'): (1, 32.20)})


def test_make_online_purchase():
    print "********test_make_online_purchase********"
    print make_online_purchase("1",
                               {('Acer', 'E23Q'): (2, 'branch1', 123.123), ('Acer', 'EBJG2'): (1, 'branch1', 433.23),
                                ('Acer', 'G6Q241'): (1, 'branch2', 123.1223)})


def test_register_user():
    print "********test_register_user********"
    print register_user("Ritesh", "Reddy", "Mona UWI", "2283822", "r@r.com", "jah", "1234567890122456", "132",
                        "2017-03-03")


def test_get_all_online_orders():
    print "********test_get_all_online_orders********"
    print get_all_online_orders()


def test_get_online_order():
    print "********test_get_online_order********"
    print get_online_order("0")


def test_get_all_branch_orders():
    print "********test_get_all_branch_orders********"
    print get_all_branch_orders(get_engine("branch1"))


def test_get_branch_orders():
    print "********test_get_branch_orders********"
    print get_branch_order(get_engine("branch1"), "1")


def test_get_laptop():
    print "********test_get_laptop********"
    print get_laptop(get_engine("branch1"), "Acer", "00H")


def test_get_laptops():
    print "********test_get_laptops********"
    print get_laptops(get_engine("branch1"), 10)


def test_get_customer():
    print "********test_get_customer********"
    print get_customer(2)


def test_get_customer_order():
    print "********test_get_customer_order********"
    print get_customer_order(1)


def test_add_inventory():
    print "********test_add_inventory********"
    print add_inventory(get_engine("branch1"), 100, "Ritesh", "Starship Enterprise!", 302320, 32, 4096, 14.4)


def test_get_customer_purchase_report_date():
    print "********test_get_customer_purchase_report_date********"
    print get_customer_purchase_report_date("2015-04-05", "2015-04-09")


def test_get_laptops_by_top_sales():
    print "********test_get_laptops_by_top_sales********"
    print get_laptops_by_top_sales(get_engine("branch1"))
    print get_laptops_by_top_sales(get_engine("branch2"))
    print get_laptops_by_top_sales(get_engine("branch3"))


def test_get_num_sales_branch():
    print "********test_get_num_sales_branch********"
    print get_num_sales_branch(get_engine("branch1"), "2015-04-03", datetime.date.today().isoformat())
    print get_num_sales_branch(get_engine("branch2"), "2015-04-03", datetime.date.today().isoformat())
    print get_num_sales_branch(get_engine("branch3"), "2015-04-03", datetime.date.today().isoformat())


def test_check_creditcard_details():
    print "********test_check_creditcard_details********"
    print check_creditcard_details(4040000001, "452 Mona Road, Montego Bay, 87142", 600, "2017-03-11")
    print check_creditcard_details(4040000000000001, "452 Mona Road, Montego Bay, 87142", 600, "2017-03-11")
    print check_creditcard_details(4040000000000002, "126 Spanish Town Road, Kingston, 26763", 212, "2019-07-19")

if __name__ == "__main__":
    test_get_customers()
    test_make_branch_purchase()
    test_make_online_purchase()
    # test_register_user()
    test_get_all_online_orders()
    test_get_online_order()
    test_get_all_branch_orders()
    test_get_branch_orders()
    test_get_laptop()
    test_get_laptops()
    test_get_customer()
    test_get_customer_order()
    #test_add_inventory()
    test_get_customer_purchase_report_date()
    test_get_laptops_by_top_sales()
    test_get_num_sales_branch()
    test_check_creditcard_details()