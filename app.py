from cs50 import SQL #was for cs50x course, used package to access sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session #holds the chat session
from werkzeug.security import check_password_hash, generate_password_hash #for hashing passwords to put into database
from flask_socketio import SocketIO #to save / facilitate the chat itself

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
db = SQL("sqlite:///Kcord.db")

@app.route("/", methods=["GET", "POST"]) #initial index page to join the chat
@login_required
def index():
    if request.method == "POST":  #clicking the join button
        return redirect("/chat")
    else:
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear() #clears prev logged in user (if exists)
    if request.method == "POST": #when login form submitted

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"] #sets a userID (app always checking for userId)

        return redirect("/") #redirects to the index 
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

        db_usernames = db.execute("SELECT username FROM users") #get all usernames from DB to make sure its not taken

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

        for i in special: #counts number of special chars in password
            for word in password:
                if i == word:
                    s_count = s_count + 1

        if not s_count >= 1:
            return apology("Password needs a special character", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?,?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/chat")
@login_required
def chat():
    usernames = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"]) #gets all usernames from DB
    username = ""
    for user in usernames:
        username = user["username"] #sets correct username for chat.html

    return render_template('chat.html', username=username)

def message_received(methods=['GET', 'POST']): #used for testing
    print('message was received!!!')

@socketio.on('my event') #custom code from SocketIO documentation
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=message_received)

if __name__ == '__main__':
    socketio.run(app, debug=True) #using socketIO to run the app