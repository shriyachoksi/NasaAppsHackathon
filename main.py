from flask import Flask, session, flash, redirect, url_for, render_template
from flask_socketio import SocketIO
from functools import wraps
from flask_pymongo import PyMongo
app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
app.config['SECRET_KEY']="b2f2396d21492f5bdb91df40f29c55ec1ac2d8726197690fb3397c284debded6"
mongo = PyMongo(app)
socket = SocketIO(app)

Users=mongo.db.users
Messages=mongo.db.messages
Skills=mongo.db.skills
Interests=mongo.db.interests

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("login"))
    return wrap

@app.get("/login")
def login():
    return "This is Login Page!"
@app.post("/login")
def login_post():
    return "This is Login Page with Post Method!"

@app.get("/")
def home():
    return "This is Home Page!"

@app.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for("login"))


if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=5500, debug=True)