from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import random, string

app = Flask(__name__)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model
class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_id = db.Column(db.String(6), unique=True, nullable=False)
    original_url = db.Column(db.String(500), nullable=False)

# Function to generate unique short ID
def generate_short_id(num_chars=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))

@app.route('/', methods=['GET', 'POST'])
def home():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['url']
        short_id = generate_short_id()

        # check if short_id already exists
        while URL.query.filter_by(short_id=short_id).first():
            short_id = generate_short_id()

        new_url = URL(original_url=original_url, short_id=short_id)
        db.session.add(new_url)
        db.session.commit()
        short_url = request.host_url + short_id
    return render_template('index.html', short_url=short_url)

@app.route('/<short_id>')
def redirect_to_url(short_id):
    url_entry = URL.query.filter_by(short_id=short_id).first()
    if url_entry:
        return redirect(url_entry.original_url)
    return "Invalid URL", 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
