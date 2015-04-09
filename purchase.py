__author__ = 'Javon-Personal'

import __setup_path
from db import *
from flask_base import *


@app.route("/purchase/<laptop>")
@authenticate
def purchase_laptop(laptop=None):
    return render_template('receipt.html', name=laptop)
