#importing libraries
from flask import Flask, session, flash, redirect, url_for, render_template, request
from flask_socketio import SocketIO
from functools import wraps
from flask_pymongo import MongoClient
from pymongo.server_api import ServerApi
from hashlib import sha256

#initialization of Flask app
app = Flask(__name__)

#setting env variables
# app.config["MONGO_URI"] = 
app.config['SECRET_KEY']="b2f2396d21492f5bdb91df40f29c55ec1ac2d8726197690fb3397c284debded6"

#initialization of DB and sockets
# client = MongoClient(uri, )
mongo = MongoClient("mongodb+srv://nasaapplication:password123parthandnasaapplication@cluster0.kq6h2lm.mongodb.net/?retryWrites=true&w=majority", server_api=ServerApi('1'))
socket = SocketIO(app)

#DB Tables
mongo = mongo["NasaAppsHackathon"]
Users=mongo.users
Messages=mongo.db.messages
Skills=mongo.db.skills
Interests=mongo.db.interests


class User:
    username=""
    connections=[]
    connection_req=[]
    interests=[]
    available=False
    edu_qual=""
    location=[]
    def __init__(self, username, connections, connection_req, interests, available, edu_qual, location) -> None:
        self.username=username
        self.connections=connections
        self.connection_req=self.connection_req
        self.interests=interests
        self.available=available
        self.edu_qual=edu_qual
        self.location=location


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
    user= request.form.get('username')
    passw = request.form.get('pass')

    if (Users.count_documents({"username":user, "password": passw})):
        session["logged_in"]=True
        usr=Users.find_one({"username":user, "password":passw})
        # session["User"]=User(username=usr.get("username"), username=usr.get("username"), username=usr.get("username"), username=usr.get("username"), username=usr.get("username"), username=usr.get("username"), username=usr.get("username"), username=usr.get("username"))
    return "This is Login Page with Post Method!"

#home function
@app.get("/")
def home():
    print(Users.find_one({"email":"email@gmail.com"}))
    return ""

#logout function
@app.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for("login"))


if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=5500, debug=True)