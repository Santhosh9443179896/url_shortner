import os
import random, string
from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# DATABASE setup
db_uri = os.getenv("DATABASE_URL", "sqlite:///urls.db")

if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# DB Model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_id = db.Column(db.String(6), unique=True, nullable=False)
    original_url = db.Column(db.String(500), nullable=False)
    clicks = db.Column(db.Integer, default=0)

# create tables
@app.before_first_request
def create_tables():
    db.create_all()

# generate short id
def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# routes
@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    if request.method == "POST":
        original_url = request.form["url"]
        existing = URL.query.filter_by(original_url=original_url).first()
        if existing:
            short_id = existing.short_id
        else:
            short_id = generate_short_id()
            while URL.query.filter_by(short_id=short_id).first():
                short_id = generate_short_id()
            new_url = URL(short_id=short_id, original_url=original_url)
            db.session.add(new_url)
            db.session.commit()
        short_url = request.host_url + short_id
    return render_template("index.html", short_url=short_url)

@app.route("/<short_id>")
def redirect_to_url(short_id):
    entry = URL.query.filter_by(short_id=short_id).first()
    if entry:
        entry.clicks += 1
        db.session.commit()
        return redirect(entry.original_url)
    return "Invalid URL", 404

if __name__ == "__main__":
    app.run(debug=True)
