__author__ = 'RiteshReddy'
import __setup_path
from db import *
from flask_base import *





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
    form = request.form
    id, name = register_user(form['fName'], form['lName'], form['address'], form['phone'], form['email'],
                             form['passwd'], form['ccnumber'], form['securitycode'], form['expirydate'])
    if id is None:
        errors = name
        form = {k: str(v) for k, v in form.items()}
        return render_template('signup.html', errors=errors, **form)
    else:
        return render_template('signup.html', errors=None, id=id, name=name)
    # save user to database and sign them in



def check_user(username, password):
    in_db_passwd = get_user_password(where_user_is=username)
    return password == in_db_passwd





