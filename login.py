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


@app.route('/', endpoint="index")
@app.route('/<name>')
@authenticate
def hello_world(name=None):
    return render_template('hello.html', name=name)


@app.route('/login', methods=["GET", "POST"])
def login():
    errors = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        isValid = check_user(username, password)
        if isValid:
            session['username'] = username
            return redirect(request.args.get('next', url_for('index')))
        else:
            errors = "Invalid login/password"

    return render_template("login.html", errors=errors)


@app.route("/logout")
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/signup", methods=["POST"])
def signup():
    errors = None
    # save user to database and sign them in


@app.route("/branch1")
@authenticate
def home():
    return render_template("branch1.html", branch=branch1, laptops=laptops)


@app.route("/item/<identifier>")
@authenticate
def item(identifier=None):
    laptop = None

    if identifier:
        laptop = get_laptop(identifier)  #get laptop based on id

    return render_template("item.html", identifier=identifier, laptop=laptop)


def check_user(username, password):
    return username == password


def get_laptop(identifier):
    for laptop in laptops:
        if int(identifier) == laptop.get('id'):
            return laptop
    return None

