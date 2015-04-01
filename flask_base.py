__author__ = 'RiteshReddy'
import __setup_path
from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__)
app.secret_key = '\xa4\x1e\x8d\x1eC\x91{\xbd\x1c\x00\xd4H\xcaXC1\xdan\xbfa\xc3\xcb\x0eiXF\xd5#\xed\x9fg\xed'

def authenticate(f):
    def wrapper(*args, **kwargs):
        if 'username' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login', next=request.url))
    return wrapper

