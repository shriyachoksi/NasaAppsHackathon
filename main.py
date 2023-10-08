#importing libraries
from flask import Flask, session, flash, redirect, url_for, render_template, request
from flask_socketio import SocketIO
from functools import wraps
from flask_pymongo import MongoClient
from pymongo.server_api import ServerApi
from hashlib import sha256
import smtplib, json, random, datetime

#SMTP
with open("adminInfo.json", "r") as f:
    adminInfo=json.load(f)["AdminInfo"]
host = smtplib.SMTP('smtp.gmail.com', 587)
host.starttls()
host.login(adminInfo["adminEmail"], adminInfo["adminPassword"])

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
Messages=mongo.messages
Skills=mongo.db.skills
Interests=mongo.db.interests

def encode(text):
    return sha256(sha256(text.encode("ascii")).hexdigest().encode("ascii")).hexdigest()

User={}
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
    return render_template("login.html")
@app.post("/login")
def login_post():
    email= request.form.get('email')
    passw = encode(request.form.get("pass"))
    print(email)
    print(passw)
    if (Users.count_documents({"email":email, "password": passw})):
        session["logged_in"]=True
        usr=Users.find_one({"email":email, "password":passw})
        session['username']=usr["userID"]
        return redirect("/")
    flash("User not found!")
    return redirect("/login")

#signup function
@app.get("/signup")
def signup():
    return render_template("signup.html")

temp_user={}

@app.post("/signup")
def signup_post():
    username = request.form.get("username")
    user= f"{request.form.get('fname')} {request.form.get('lname')}"
    passw = encode(request.form.get("pass"))
    email = request.form.get("email")
    if " " in username:
        flash("Spaces not allowed!")
        return redirect("/signup")
    if datetime.datetime.now().year-int(request.form.get('byear'))<18:
        flash("Atleast 18 years of age is required!")
        return redirect("/signup")
    if (Users.count_documents({"email":email})==0):
        session["email"]=email
        temp_user["user"]={"username":user, "password":passw, "email":email, "userID": username}
        return redirect("/otp")
    flash("Email Id already present!")
    return redirect("/signup")

@app.get("/otp")
def otp_var():
    otp=random.randint(100000,999999)
    host.sendmail(adminInfo["adminEmail"], [session["email"]], f"Your OTP for NovaLink is:\n{otp}")
    print("OTP sent")
    print(session["email"])
    session["otp"]=encode(str(otp))
    return render_template("otp.html")

@app.post("/otp")
def post_otp():
    if encode(request.form.get("otp")) == session["otp"]:
        Users.insert_one(temp_user["user"])
        print(temp_user["user"])
        session["logged_in"]=True
        session["username"]=temp_user["user"].get("userID")
        return redirect("/")
    flash("Wrong OTP!")
    return redirect("/otp")
#home function
@app.get("/")
@login_required
def home():
    usr=Users.find_one({"userID":session["username"]})
    return render_template("index.html", user=usr)

@app.get("/profile/edit")
@login_required
def profile():
    usr = Users.find_one({"userID":session["username"]})
    return render_template("editprofile.html", user=usr)

@app.post("/profile/edit")
@login_required
def edit_profile():
    bio = request.form.get("bio")
    edu_qual = request.form.get("edu_qual")
    skills = request.form.get("skill")

    if bio!="" and edu_qual!="" and skills!="":
        Users.update_one({"userID":session["username"]}, {"$set":{"bio":bio, "edu_qual":edu_qual, "skills": skills}})
        return redirect("/")

    return render_template("editprofile.html")

#logout function
@app.get("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for("login"))

@app.get("/messages")
@login_required
def messages():
    usr = Users.find_one({"userID":session["username"]})
    if "contacts" in usr:
        contacts = usr["contacts"]
    else:
        contacts=[]
    return render_template("message.html", contacts=contacts)

@app.get("/messages/<message_url>")
@login_required
def Urlmessages(message_url):
    messages = Messages.find_one({"message_url":message_url})
    if session["username"] not in messages["auth"]:
        flash("User Not Allowed!")
        return redirect("/messages")
    usr = Users.find_one({"userID":session["username"]})
    if "contacts" in usr:
        contacts = usr["contacts"]
    else:
        contacts=[]
    return render_template("message.html", messages=messages["messages"], contacts=contacts)

@socket.on('check_usrname')
def check_usrname(json):
    print(str(json))
    if Users.count_documents({"userID":json["username"]})!=0:
        socket.emit("username_not_available")
    else:
        socket.emit("username_available")

@socket.on('message')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

if __name__ == "__main__":
    socket.run(app, host="0.0.0.0", port=5500, debug=True)