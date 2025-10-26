from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health')
def health():
    return jsonify(status='ok')


if __name__ == '__main__':
    # Use 127.0.0.1 for local development. Remove debug=True in production.
    app.run(debug=True, host='127.0.0.1', port=5000)
