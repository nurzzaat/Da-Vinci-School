from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helper import apology, login_required, calculate_distance, lookup


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///balloon.db")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("select * from users where id=?" , session.get("user_id"))
    username  = rows[0]["username"]
    cash=rows[0]["caapital"]
    size = rows[0]["size"]

    return render_template("index.html" , username=username,cash=cash, size=size)

@app.route("/select" , methods=["POST" , "GET"])
@login_required
def select():
    if request.method == "POST":
        fcity = request.form["from"]
        tcity = request.form["to"]

        if lookup(fcity) is None:
            return apology("must provide source city" , 400)
        if lookup(tcity) is None:
            return apology("must provide destination city" , 400)


        session["fcity"] = fcity
        session["tcity"] = tcity

        rows = db.execute("Select * from users where id=?" , session.get("user_id"))
        size = rows[0]["size"]

        #Calculate distance and cost between start city and selected city
        distance = calculate_distance(float(lookup(fcity)['latitude']), float(lookup(fcity)['longitude']),
                                       float(lookup(tcity)['latitude']), float(lookup(tcity)['longitude']))
        session["distance"] = distance

        if size == "small":
            if distance > 300:
                return render_template("between.html", f=fcity, t=tcity)
            else:
                old_cash = db.execute("select caapital from users where id=?" , session.get("user_id"))[0]["caapital"]
                new_cash = (int)(old_cash) - (int)(distance)
                if new_cash < 0:
                    return render_template("cash.html")
                db.execute('insert into history ("from", "to", distance, capital, size, user_id) values(?,?,?,?,?,?)' , fcity, tcity, (int)(distance), (int)(distance), size, session.get("user_id"))
                db.execute("update users set caapital=? where id=?" , new_cash , session.get("user_id"))
                return redirect("/")


        if size == "big":
            if distance > 700:
                return render_template("/between.html", f=fcity, t=tcity)
            else:
                old_cash = db.execute("select caapital from users where id=?" , session.get("user_id"))[0]["caapital"]
                new_cash = (int)(old_cash) - (int)(distance)
                if new_cash < 0:
                    return render_template("cash.html")
                db.execute('insert into history ("from", "to", distance, capital, size, user_id) values(?,?,?,?,?,?)' , fcity, tcity, (int)(distance), (int)(distance), size, session.get("user_id"))
                db.execute("update users set caapital=? where id=?" , new_cash , session.get("user_id"))
                return redirect("/")

        return redirect("/")
    else:
        return render_template("select.html")


@app.route("/between" , methods=["POST" , "GET"])
@login_required
def between():
    if request.method == "POST":
        between = request.form["between"]


        if lookup(between) is None:
            return apology("must provide between city" , 400)

        distance1 = calculate_distance(float(lookup(session["fcity"])['latitude']), float(lookup(session["fcity"])['longitude']),
                                        float(lookup(between)['latitude']), float(lookup(between)['longitude']))

        distance2 = calculate_distance(float(lookup(between)['latitude']), float(lookup(between)['longitude']),
                                        float(lookup(session["fcity"])['latitude']), float(lookup(session["fcity"])['longitude']))

        if distance1 > session["distance"]:
            return render_template("between.html", f=session["fcity"], t=session["tcity"], message="That city is farther than destination city. Choose another one")
        else:
            rows = db.execute("Select * from users where id=?" , session.get("user_id"))
            size = rows[0]["size"]

            if size == "small":
                if distance1 < 300:
                    if distance2 < 300:
                        old_cash = db.execute("select caapital from users where id=?" , session.get("user_id"))[0]["caapital"]
                        new_cash = (int)(session["distance"]) + 10
                        if new_cash > old_cash:
                            return render_template("cash.html")
                        db.execute('insert into history ("from", "to", distance, capital, size, user_id) values(?,?,?,?,?,?)' , session["fcity"], session["tcity"],(int)(session["distance"]), new_cash, size, (int)(session.get("user_id")))
                        db.execute("update users set caapital=? where id=?" , old_cash - new_cash , session.get("user_id"))
                        return redirect("/")
                    else:
                        return render_template("between.html" , f=between , t=session["tcity"] , message="Next parts are harder, i couldn't find a way to get all data from that API to show, sorry for my easy submission")
                else:
                    return render_template("between.html" , f=between , t=session["tcity"] , message="Next parts are harder (if i randomly will take Almaty->New York) , it takes a long time to do , sorry for my easy submission")

            if size == "big":
                if distance1 < 700:
                    if distance2 < 700:
                        old_cash = db.execute("select caapital from users where id=?" , session.get("user_id"))[0]["caapital"]
                        new_cash = (int)(session["distance"]) + 10
                        if new_cash > old_cash:
                            return render_template("cash.html")
                        db.execute('insert into history ("from", "to", distance, capital, size, user_id) values(?,?,?,?,?,?)' , session["fcity"], session["tcity"],(int)(session["distance"]), new_cash, size, (int)(session.get("user_id")))
                        db.execute("update users set caapital=? where id=?" , old_cash - new_cash , session.get("user_id"))
                        return redirect("/")
                    else:
                        return render_template("between.html" , f=between , t=session["tcity"] , message="Next parts are harder, i couldn't find a way to get all data from that API to show, sorry for my easy submission")
                else:
                    return render_template("between.html" , f=between , t=session["tcity"] , message="Next parts are harder (if i randomly will take Almaty->New York) , it takes a long time to do , sorry for my easy submission")

    else:
        return render_template("between.html")

@app.route("/cash" ,methods=["POST" , "GET"])
@login_required
def cash():
    if request.method == "POST":
        cash = request.form["amount"]
        old_cash = db.execute("select caapital from users where id=?" , session.get("user_id"))[0]["caapital"]
        new_cash = (int)(old_cash) + (int)(cash)
        db.execute("update users set caapital=? where id=?" , new_cash , session.get("user_id"))
        return render_template("select.html")
    else:
        return render_template("cash.html")

@app.route("/history")
@login_required
def history():
    # Retrieve all transactions for the current user
    rows = db.execute("SELECT * FROM history WHERE user_id =?",session.get("user_id"))
    items = []

    items = [{
            'from' : "Source",
            'to' : "Destination",
            'distance' : "Distance" ,
            'capital' : "Capital",
            'size' : "Size"
    }]


    # Format the date and time of each transaction
    for row in rows:
        items.append(row)

    return render_template("history.html" , items=items)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        passw = request.form["password"]
        conf = request.form["confirmation"]
        if passw != conf:
            return apology("passwords must match", 400)
        capital = request.form["capital"]
        size = request.form["balloon_size"]
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)

        # Ensure username is not already taken
        if len(rows) != 0:
            return apology("username already taken", 400)

        # Insert new user into database
        db.execute("INSERT INTO users (username, hash , caapital , size) VALUES (:username, :hash, :caapital, :size )",
                   username=request.form.get("username"),
                   hash=generate_password_hash(passw), caapital=capital, size=size)

        # # Redirect user to login page
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password" , 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
