#importing libraries
from flask import Flask, session, flash, redirect, url_for, render_template
from flask_socketio import SocketIO
from functools import wraps
from flask_pymongo import PyMongo

#initialization of Flask app
app = Flask(__name__)

#setting env variables
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
app.config['SECRET_KEY']="b2f2396d21492f5bdb91df40f29c55ec1ac2d8726197690fb3397c284debded6"

#initialization of DB and sockets
mongo = PyMongo(app)
socket = SocketIO(app)

#DB Tables
Users=mongo.db.users
Messages=mongo.db.messages
Skills=mongo.db.skills
Interests=mongo.db.interests

#decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for("login"))
    return wrap

#login functions
@app.get("/login")
def login():
    return "This is Login Page!"
@app.post("/login")
def login_post():
    return "This is Login Page with Post Method!"

#home function
@app.get("/")
def home():
    return "This is Home Page!"

#logout function
@app.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for("login"))


if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=5500, debug=True)