# app.py
import os, random, string
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(_name_)

# ------------------------------------------------------------------
# ⿡  Database configuration
# ------------------------------------------------------------------
# • When you deploy, Render sets the env-var DATABASE_URL.
# • Locally, we fall back to SQLite so you can still run the app
#   without Postgres installed.

db_uri = os.getenv("DATABASE_URL", "sqlite:///urls.db")

# Render’s DATABASE_URL uses the old “postgres://” scheme.
# SQLAlchemy expects “postgresql://”.  Fix it if necessary:
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------------------------------------------------------
# ⿢  Model
# ------------------------------------------------------------------
class URL(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    short_id     = db.Column(db.String(6), unique=True, nullable=False)
    original_url = db.Column(db.String(500), nullable=False)
    clicks       = db.Column(db.Integer, default=0)

# ------------------------------------------------------------------
# ⿣  Helper to create unique IDs
# ------------------------------------------------------------------
def generate_short_id(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))

# ------------------------------------------------------------------
# ⿤  Create tables automatically on first request
# ------------------------------------------------------------------
@app.before_first_request
def create_tables() -> None:
    db.create_all()

# ------------------------------------------------------------------
# ⿥  Routes
# ------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None

    if request.method == "POST":
        original_url = request.form["url"]

        # OPTIONAL: reuse the same short link if the URL already exists
        existing = URL.query.filter_by(original_url=original_url).first()
        if existing:
            short_id = existing.short_id
        else:
            short_id = generate_short_id()
            while URL.query.filter_by(short_id=short_id).first():
                short_id = generate_short_id()

            db.session.add(URL(short_id=short_id, original_url=original_url))
            db.session.commit()

        short_url = request.host_url + short_id

    return render_template("index.html", short_url=short_url)


@app.route("/<short_id>")
def redirect_to_url(short_id: str):
    entry = URL.query.filter_by(short_id=short_id).first()
    if entry:
        entry.clicks += 1
        db.session.commit()
        return redirect(entry.original_url)
    return "Invalid URL", 404

# ------------------------------------------------------------------
# ⿦  Local dev entry-point
# ------------------------------------------------------------------
if _name_ == "_main_":
    app.run(debug=True)
