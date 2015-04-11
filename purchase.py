__author__ = 'Javon-Personal'

import __setup_path
from db import *
from flask_base import *


@app.route("/purchase/<laptop>")
@authenticate
def purchase_laptop(laptop=None):
    return render_template('receipt.html', name=laptop)


@app.route("/laptop/<branch>/<vendor>/<model>")
@authenticate
@validate_branch
def view_laptop(branch, vendor, model):
    laptop = get_laptop(get_engine(branch), str(vendor), str(model))
    if laptop is None:
        return render_template("laptop_single.html", errors="Laptop not found!", laptop=laptop)
    else:
        return render_template("laptop_single.html", errors=None, branch=branch, laptop=laptop)


@app.route('/', endpoint="index")
@app.route("/onlinestore")
@authenticate
def online_store():
    branch1 = get_laptops(get_engine("branch1"))
    branch2 = get_laptops(get_engine("branch2"))
    branch3 = get_laptops(get_engine("branch3"))

    laptops = []
    for laptop1 in branch1:
        for laptop2 in branch2:
            for laptop3 in branch3:
                if laptop1.vendor == laptop2.vendor and laptop1.vendor == laptop3.vendor:
                    if laptop1.model == laptop2.model and laptop1.model == laptop3.model:
                        lap = laptop1.items()
                        choice = max(laptop1.quantity, laptop2.quantity, laptop3.quantity)
                        if choice == laptop1.quantity:
                            branch = "branch1"
                        elif choice == laptop2.quantity:
                            branch = "branch2"
                        else:
                            branch = "branch3"
                        lap.append(("maxquantity", choice))
                        lap.append(("branch", branch))
                        laptops.append({x[0]: x[1] for x in lap})
    return render_template("store.html", laptops=laptops)


@app.route("/buy", methods=["POST"])
@authenticate
def buy():
    laptops = {}
    display = []
    total = 0
    user = get_customer(session.get('username'))
    for key, value in request.form.items():
        vendor, model, title = (str(key)).split("-")
        if title == "qty":
            if int(value) != 0:
                quantity = int(value)
                branch = None
                for key, value in request.form.items():
                    vendor1, model1, title = (str(key)).split("-")
                    if title == "branch":
                        if vendor == vendor1 and model == model1:
                            branch = str(value)
                            break
                cost = None
                for key, value in request.form.items():
                    vendor1, model1, title = (str(key)).split("-")
                    if title == "cost":
                        if vendor == vendor1 and model == model1:
                            cost = float(value)
                            break
                laptops[(vendor, model)] = (int(quantity), str(branch), float(cost))
                display.append((vendor, model, int(quantity), str(branch), float(cost) * int(quantity)))
                total += float(cost) * int(quantity)
    valid_card = check_creditcard_details(user.ccnumber, user.ccaddress, user.securitycode, user.expirydate)
    if not valid_card:
        return render_template("receipt.html", errors="Cannot Purchase! Invalid Credit Card Details")
    id, trackingno = make_online_purchase(session.get('username'), laptops)
    if id is None:
        return render_template("receipt.html", errors="Could not make purchase")
    else:
        return render_template("receipt.html", errors=None, trackingno=trackingno, laptops=display, total=total)

