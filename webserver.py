__author__ = 'RiteshReddy'
from flask_base import *
from db import *
from login import *
from branch1 import *
from purchase import *

if __name__ == '__main__':
    app.run(debug=True)
