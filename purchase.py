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