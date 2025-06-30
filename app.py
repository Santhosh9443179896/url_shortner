from flask import Flask, request, redirect, render_template
import random, string

app = Flask(__name__)
url_db = {}

def generate_short_id(num_chars=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_chars))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['url']
        short_id = generate_short_id()
        url_db[short_id] = original_url
        short_url = request.host_url + short_id
        return render_template('index.html', short_url=short_url)
    return render_template('index.html')

@app.route('/<short_id>')
def redirect_to_url(short_id):
    original_url = url_db.get(short_id)
    if original_url:
        return redirect(original_url)
    return "Invalid URL", 404

if __name__ == '__main__':
    app.run(debug=True)
