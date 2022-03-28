import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

#import helper functions
from helpers import apology, login_required

#configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#configure database
db = SQL("sqlite:///KVcord.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"]= "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    #shows the chat and all the messages sent previously
    
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        #copy paste login functionality
         # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        #copy paste the register method
        if not request.form.get("username"):
            return apology("must provide username", 400)

        db_usernames = db.execute("SELECT username FROM users")

        for db_username in db_usernames:
            if request.form.get("username") == db_username["username"]:
                return apology("username taken, please try again", 400)

        if not request.form.get("password"):
            return apology("must provide password", 400)

        if not request.form.get("confirmation"):
            return apology("most confirm password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("both passwords must match", 400)

        password = request.form.get("password")
        special = ["!",'"',"#","$","%","&","'","(",")","*", '+', ",","-", ".","/",":",";","<","=",">","?","@","[","]", "^", "_","`","{","|","}","~","]"]
        s_count = 0

        for i in special:
            for word in password:
                if i == word:
                    s_count = s_count + 1

        if not s_count >= 1:
            return apology("Password needs a special character", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?,?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        return redirect("/login")
    else:
        return render_template("register.html")