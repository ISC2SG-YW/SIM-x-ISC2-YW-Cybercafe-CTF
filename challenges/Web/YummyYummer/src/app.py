from flask import Flask, request, render_template, session, redirect, url_for, flash
from sqlite3 import connect, Row
from db_init import init_db
from functools import wraps
from hashlib import sha256
import os

init_db()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
DB_PATH = "yummy_yummer.db"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

def require_role(*allowed):
    def deco(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not session.get("username"):
                flash("Please log in to continue.", "warning")
                return redirect(url_for("home"))
            if allowed and session.get("role") not in allowed:
                flash("You don't have access to that area.", "danger")
                return redirect(url_for("home"))
            return view(*args, **kwargs)
        return wrapper
    return deco

def get_conn():
    conn = connect(DB_PATH)
    conn.row_factory = Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def users_table():
    with get_conn() as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_schema WHERE type='table' AND name IN ('user','app_users') LIMIT 1"
        ).fetchone()
        return row["name"] if row else "user"

def browse_menu(search):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT sku, name, category, price_cents "
            "FROM menu "
            f"WHERE is_active = 1 AND name LIKE '%{search}%' "
            "ORDER BY 2"
        )
        return [dict(r) for r in cur.fetchall()]

def default_menu():
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT sku,name,category,price_cents FROM menu "
            "WHERE is_active = 1 ORDER BY name"
        )
        return [dict(r) for r in cur.fetchall()]

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/menu", methods=["GET"])
@require_role("customer", "admin", "guest")
def menu():
    q = request.args.get("q", "")
    items = browse_menu(q) if q else default_menu()
    return render_template("menu.html", items=items, q=q)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "")
        p = request.form.get("password", "")
        hash_p = sha256(p.encode("utf-8")).hexdigest()
        tbl = users_table()
        sql = (
            f"SELECT username, role, is_active FROM {tbl} "
            f"WHERE username='{u}' AND password_hash='{hash_p}' AND is_active=1"
        )
        with get_conn() as conn:
            row = conn.execute(sql).fetchone()
        if not row:
            flash("Invalid credentials or inactive account.", "danger")
            return redirect(url_for("login"))
        session["username"] = row["username"]
        session["role"] = row["role"]
        flash(f"Welcome, {row['username']}!", "success")
        return redirect(url_for("menu"))
    return render_template("login.html")

@app.route("/guest", methods=["POST"])
def guest():
    session["username"] = "guest"
    session["role"] = "guest"
    flash("Continuing as guest.", "info")
    return redirect(url_for("menu"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

@app.route("/flag", methods=["GET"])
@require_role("admin")
def flag():
    return (os.getenv("FLAG", "Um, theres a problem here, please approach one of us to get the flag and fix this thanks"), 200)

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Something went wrong"), 500

@app.route("/whoami")
def whoami():
    return {
        "username": session.get("username"),
        "role": session.get("role"),
        "logged_in": bool(session.get("username")),
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6767, debug=False)
