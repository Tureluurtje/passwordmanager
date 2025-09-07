from flask import Flask, jsonify, request
from flask_cors import CORS
import base64
import datetime
import json 

from core.server import handleAuth, handlePassword
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

@app.route("/ping/")
def ping():
    return jsonify({"message": "pong"})

# NOTE: This route handles API requests
@app.route("/")
def requestReceiver() -> dict:
    try:
        #result, code = requestHandler(request)
        return jsonify({"message": "Hello World!"}), 200
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
        
@app.route("/auth/<path:subpath>", methods=["GET","POST"])
def authenticate(subpath: str) -> dict:
    try:
        auth_header = request.headers.get("Authorization")
        auth_token = None
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ", 1)[1]

        data = request.get_json(silent=True) or {}
        allowed_subpaths = ["login", "register", "refresh", "logout", "check"]

        if subpath not in allowed_subpaths:
            return jsonify({"success": False, "error": f"Invalid auth route: {subpath}"}), 404

        return handleAuth(subpath, data, auth_token)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.FLASK_HOST, port=config.PORT_API)  # Run the Flask app on localhost:5000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.