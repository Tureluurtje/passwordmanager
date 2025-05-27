from flask import Flask, jsonify, request

from core.server import requestHandler

app = Flask(__name__)


@app.route('/')
def home():
    #Default return
    return jsonify({'message': 'Hello, World!'})

@app.route('/ping/')
def ping():
    #Server ping
    return jsonify('pong')

@app.route('/api/', methods=['GET'])
def requestReceiver():
    try:
        result = requestHandler(request)
        return jsonify({
            "succes": True,
            "data": result
        }), 200
    except Exception as e:
        return jsonify({
            "succes": False,
            "data": str(e)
        }), 400

if __name__ == '__main__':
    #Run the server
    app.run(host='127.0.0.1', port=5000)
# This is the main entry point for the Flask application.