import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from flask_socketio import SocketIO

#import helper functions
from helpers import apology, login_required

#configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#configure socket
app.config['SECRET_KEY'] = 'ty2hfoupal2kddi[2ihf['
socketio = SocketIO(app)

# Configure session to use filesystem (instead of signed cookies)
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

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        chat = int(request.form.get("chat"))
        if chat > 5 or chat < 1:
            return apology("not a valid chat number", 400)
        if chat == 1:
            return redirect("/chat1")
        if chat == 2:
            return redirect("/chat2")
        if chat == 3:
            return redirect("/chat3")
        if chat == 4:
            return redirect("/chat4")
        if chat == 5:          
            return redirect("/chat5")
        else:
            return apology("Enter a valid chat number", 400)
    else:
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]

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

@app.route("/chat1")
@login_required
def chat1():
    return render_template('chat1.html')

def messager_received(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=message-received)

if __name__ == '__main__':
    socketio.run(app, debug=True)