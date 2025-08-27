from flask import Flask, jsonify, request
from flask_cors import CORS
import base64
import datetime
import json 

from core.server import requestHandler
import config.config as config

app = Flask(__name__)
CORS(app)

#Encoder for the hashes in the passwords
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except UnicodeDecodeError:
                return base64.b64encode(obj).decode("utf-8")
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app.json_provider_class = None  # disables new provider in Flask 2.2+
app.json_encoder = JSONEncoder

@app.route('/ping/')
def ping():
    return jsonify({'message': 'pong'})

# NOTE: This route handles API requests
@app.route('/', methods=['POST'])
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
        
@app.route('/', methods=['GET'])
def test_get():
    return jsonify({"message": "Hello World!"}), 200


if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.FLASK_HOST, port=config.PORT_API)  # Run the Flask app on localhost:5000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.