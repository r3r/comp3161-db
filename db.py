__author__ = 'RiteshReddy'
import __setup_path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text
import datetime, uuid


urls = {"branch1": "mysql://root:root@localhost/compustore_branch1",
        "branch2": "mysql://root:root@localhost/compustore_branch2",
        "branch3": "mysql://root:root@localhost/compustore_branch3",
        "online": "mysql://root:root@localhost/compustore_online"}


def get_engine(to, echo=False):
    url = urls.get(to, None)
    if url is None:
        return url
    engine = create_engine(url, echo=echo)
    metadata = MetaData(bind=engine)
    return engine


def get_customers(engine=get_engine("online"), where="1"):
    return engine.execute('select * from customers WHERE ' + where).fetchall()


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
        for laptop, qty in laptops.items():
            insert_line_item = text(
                "INSERT INTO `line_item` (`vendor`, `model`, `orderid`, `quantity`) VALUES (:vendor, :model, :orderid, :quantity)")
            connection.execute(insert_line_item,
                               {'vendor': laptop[0], 'model': laptop[1], 'orderid': id, 'quantity': qty})
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
    :param laptops: dictionary of laptops -> qty + branch => {(vendor, model):(qty, branch)}
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
        for laptop, details in laptops.items():
            insert_line_item = text(
                "INSERT INTO `line_item` (`vendor`, `model`, `orderid`, `quantity`, `branch_id`) VALUES (:vendor, :model, :orderid, :quantity, :branch_id)")
            connections['online'].execute(insert_line_item, {'vendor': laptop[0], 'model': laptop[1], 'orderid': id,
                                                             'quantity': details[0], "branch_id": details[1]})
            connections[details[1]].execute(text(
                "UPDATE `inventory` SET `quantity` = `quantity` - :quantity WHERE `vendor`=:vendor and `model`=:model"),
                                            {'quantity': details[0], "vendor": laptop[0], "model": laptop[1]})
        for transaction in transactions.values():
            transaction.commit()
        return id, trackingno
    except Exception, e:
        for transaction in transactions.values():
            transaction.rollback()
        return None, e


def get_laptops(engine, offset, maxResults=30):
    connection = engine.connect()
    return connection.execute(text("SELECT * FROM `inventory` LIMIT :offset, :maxResults"),
                              {"offset": offset, "maxResults": maxResults}).fetchall()


def get_laptop(engine, vendor, model):
    return engine.execute(text("SELECT * FROM `inventory` WHERE `vendor`=:vendor and `model`=:model"),
                          {"vendor": vendor, "model": model}).first()


def get_customer(custid, engine=get_engine("online")):
    string = text(
        "SELECT * FROM `customer` as cust  join `creditcards` as cc on cust.custid=cc.custid WHERE cust.`custid` = :id")
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


def get_user_password(engine=get_engine("online"), where_user_is="1"):
    string = text("SELECT `passwd` FROM `customer` WHERE `custid` = :id")
    res = engine.execute(string, {"id": where_user_is}).first()
    if not res is None:
        return res[0]
    else:
        return None



def test_make_branch_purchase():
    print "********test_make_branch_purchase********"
    engine = get_engine("branch1")
    print make_branch_purchase(engine, {('Acer', '00CA'): 2, ('Acer', '00H'): 1})


def test_make_online_purchase():
    print "********test_make_online_purchase********"
    print make_online_purchase("1", {('Acer', '00CA'): (2, 'branch1'), ('Acer', '00H'): (1, 'branch1'),
                                     ('Acer', '0071'): (1, 'branch2')})


def test_register_user():
    print "********test_register_user********"
    print register_user("Ritesh", "Reddy", "Mona UWI", "2283822", "r@r.com", "jah", "1234567890123456", "132",
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

if __name__ == "__main__":
    test_make_branch_purchase()
    test_make_online_purchase()
    test_register_user()
    test_get_all_online_orders()
    test_get_online_order()
    test_get_all_branch_orders()
    test_get_branch_orders()
    test_get_laptop()
    test_get_laptops()
    test_get_customer()