
import os

from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)

# Demonstration-only configuration.
# Never use these credentials or this fallback key in production.
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "local-demo-secret-key"
)

DEMO_USERNAME = "student"
DEMO_PASSWORD = "wrongpassword"


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if (
            username == DEMO_USERNAME
            and password == DEMO_PASSWORD
        ):
            session["username"] = username
            return redirect(url_for("dashboard"))

        error = "Invalid username or password"

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))

    app.run(
        host="127.0.0.1",
        port=port,
        debug=False
    )