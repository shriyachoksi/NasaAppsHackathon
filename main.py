#importing libraries
from flask import Flask, session, flash, redirect, url_for, render_template, request
from flask_socketio import SocketIO
from functools import wraps
from flask_pymongo import MongoClient
from pymongo.server_api import ServerApi
from hashlib import sha256
import smtplib, json

#SMTP
with open("adminInfo.json", "r") as f:
    adminInfo=json.load(f)["AdminInfo"]
host = smtplib.SMTP('smtp.gmail.com', 587)
host.starttls()
host.login(adminInfo["adminEmail"], adminInfo["adminPassword"])
# host.sendmail(adminInfo["adminEmail"], ["pjpanot260305@gmail.com"], "This is a Trial message!")
# host.close()

# print(adminInfo["adminEmail"])

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

def encode(text):
    return sha256(sha256(text.encode("utm-8")).hexdigest().encode("utm-8")).hexdigest()

User={}
#decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session["logged_in"]:
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
    passw = encode(request.form.get("pass"))

    if (Users.count_documents({"username":user, "password": passw})):
        session["logged_in"]=True
        usr=Users.find_one({"username":user, "password":passw})
        session['usrname']=usr['_id']
        return redirect("/")

#signup function
@app.get("/signup")
def signup():
    return "This is Login Page!"
@app.post("/signup")
def signup_post():
    user= request.form.get('username')
    passw = encode(request.form.get("pass"))

    if (Users.count_documents({"username":user, "password": passw})):
        session["logged_in"]=True
        usr=Users.find_one({"username":user, "password":passw})
        session['usrname']=usr['_id']
        return redirect("/")

#home function
@app.get("/")
def home():
    # print(Users.find_one({"email":"email@gmail.com"}))
    return ""

#logout function
@app.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for("login"))


if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=5500, debug=True)