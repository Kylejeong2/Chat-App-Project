from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400): #if something is broken or not available redirects users to apology page
    def escape(s): #fixes all of the chars that could potentially break the apology screen
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code #flask to render apology screen

def login_required(f): #checks if the user is currently logged in 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login") #if not logged in then send to the login page
        return f(*args, **kwargs)
    return decorated_function