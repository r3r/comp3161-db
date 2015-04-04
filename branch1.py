__author__ = 'RiteshReddy'
import __setup_path
from db import *
from flask_base import *


laptops = [  # fake array of laptops
             {
                 'id': 1,
                 'name': 'Dell Inspiron',
                 'price': 45,
                 'description': 'Description of dell inspiron'
             },
             {
                 'id': 2,
                 'name': 'Hp note',
                 'price': 60,
                 'description': 'Decription of hp note'
             },
             {
                 'id': 3,
                 'name': 'Apple Macintosh',
                 'price': 600,
                 'description': 'Decription of mac'
             }
]

branch1 = {
    'name': 'Branch 1'
}


@app.route("/branch1")
@authenticate
def home():
    return render_template("branch1.html", branch=branch1, laptops=laptops)


@app.route("/branch1/item/<identifier>")
@authenticate
def item(identifier=None):
    laptop = None

    if identifier:
        laptop = get_laptop(identifier)  # get laptop based on id

    return render_template("item.html", identifier=identifier, laptop=laptop)


def get_laptop(identifier):
    for laptop in laptops:
        if int(identifier) == laptop.get('id'):
            return laptop
    return None
