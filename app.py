from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date
import random

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# ---------------- DUMMY ADMIN USER ----------------
ADMIN_USER = {
    "username": "Admin",
    "password": "admin123"
}

# ---------------- GLOBAL DATA ----------------
BUSES = [
    {"name": "Volvo AC", "time": "08:00 AM", "price": 800, "seats": 20},
    {"name": "Sleeper", "time": "10:30 PM", "price": 1200, "seats": 10},
    {"name": "Express", "time": "06:15 AM", "price": 600, "seats": 30}
]

TRAINS = [
    {"name": "Rajdhani Express", "time": "06:00 AM", "price": 1500, "seats": 12},
    {"name": "Shatabdi Express", "time": "07:30 AM", "price": 1200, "seats": 25},
    {"name": "Duronto Express", "time": "09:00 PM", "price": 1800, "seats": 5}
]

# ---------------- HOME ----------------
@app.route("/")
def home():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        captcha = request.form.get("captcha")

        if int(captcha) != session.get("captcha"):
            flash("Captcha incorrect", "error")
            return redirect(url_for("login"))

        if username == ADMIN_USER["username"] and password == ADMIN_USER["password"]:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    a = random.randint(1, 9)
    b = random.randint(1, 9)
    session["captcha"] = a + b
    return render_template("login.html", a=a, b=b)

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        session["user"] = request.form.get("name")
        return redirect(url_for("dashboard"))
    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("index.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- SEARCH ----------------
@app.route("/search", methods=["POST"])
def search():
    session["from_city"] = request.form.get("from_city")
    session["to_city"] = request.form.get("to_city")
    session["journey_date"] = request.form.get("journey_date")

    mode = request.form.get("mode")
    if mode == "bus":
        return redirect(url_for("bus_results"))
    return redirect(url_for("train_results"))

# ---------------- BUS RESULTS ----------------
@app.route("/bus-results")
def bus_results():
    return render_template("bus_results.html", buses=BUSES)

# ---------------- TRAIN RESULTS ----------------
@app.route("/train-results")
def train_results():
    return render_template("train_results.html", trains=TRAINS)

# ---------------- PASSENGER DETAILS ----------------
@app.route("/passenger-details/<transport>/<name>/<int:price>", methods=["GET", "POST"])
def passenger_details(transport, name, price):
    if not session.get("user"):
        return redirect(url_for("login"))

    if request.method == "POST":
        passenger_name = request.form.get("passenger_name")
        age = request.form.get("age")
        journey_date = request.form.get("journey_date")

        if journey_date == date.today().isoformat():
            flash("Booking for today is not allowed", "error")
            return redirect(request.url)

        if transport == "bus":
            for b in BUSES:
                if b["name"] == name:
                    if b["seats"] <= 0:
                        flash("No seats available", "error")
                        return redirect(request.url)
                    b["seats"] -= 1
                    break

        if transport == "train":
            for t in TRAINS:
                if t["name"] == name:
                    if t["seats"] <= 0:
                        flash("No seats available", "error")
                        return redirect(request.url)
                    t["seats"] -= 1
                    break

        booking = {
            "user": session["user"],
            "transport": transport,
            "name": name,
            "price": price,
            "passenger": passenger_name,
            "age": age,
            "journey_date": journey_date
        }

        session.setdefault("bookings", []).append(booking)
        return redirect(url_for("booking_success"))

    return render_template(
        "passenger_details.html",
        transport=transport,
        name=name,
        price=price
    )

# ---------------- BOOKINGS ----------------
@app.route("/bookings")
def bookings():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("bookings.html", bookings=session.get("bookings", []))

# ---------------- BOOKING SUCCESS ----------------
@app.route("/booking-success")
def booking_success():
    booking = session.get("bookings")[-1]
    return render_template(
        "booking_confirmed.html",
        transport=booking["transport"],
        name=booking["name"]
    )

# ---------------- HELP ----------------
@app.route("/help")
def help_page():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("help.html")

# ---------------- START ----------------
if __name__ == "__main__":
    app.run(debug=True)
