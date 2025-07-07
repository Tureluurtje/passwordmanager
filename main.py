from flask import Flask, jsonify, request
from core.server import requestHandler
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    #Default return
    return jsonify({'message': 'Hello, World!'})

@app.route('/ping/')
def ping():
    #Server ping
    return jsonify({'message': 'pong'})

@app.route('/api/', methods=['GET'])
def requestReceiver():
    try:
        result, code = requestHandler(request)
        return jsonify({
            "message": result
        }), code
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)  # Run the Flask app on localhost:5000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.
# This is a simple Flask application that serves as an API for password management.