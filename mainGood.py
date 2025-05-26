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