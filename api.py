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

@app.route("/ping/")
def ping():
    return jsonify({"message": "pong"})

# NOTE: This route handles API requests
@app.route("/", methods=["POST"])
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

@app.route("/auth/<path:subpath>", methods=["GET","POST"])
def authenticate(subpath: str) -> dict:
    try:
        auth_header = request.headers.get("Authorization")
        auth_token = None
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ", 1)[1]

        data = request.get_json(silent=True) or {}
        allowed_subpaths = ["login", "register", "refresh", "logout", "check", "salt"]

        if subpath not in allowed_subpaths:
            return jsonify({
                "success": False,
                "error": f"Invalid auth route: {subpath}"
            }), 404
        result, code = handleAuth(subpath, data, auth_token)
        return jsonify({
            "success": True,
            "data": str(result)
        }), code

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/password", defaults={"subpath": None}, methods=["GET", "POST", "PATCH", "DELETE"])
@app.route("/password/<path:subpath>", methods=["GET", "POST", "PATCH", "DELETE"])
def password(subpath: str=None) -> dict:
    try:
        auth_header = request.headers.get("Authorization")
        auth_token = None
        if auth_header and auth_header.startswith("Bearer "):
            auth_token = auth_header.split(" ", 1)[1]
            verified, username = handleAuth("verify", None, auth_token)
            if verified and username != 401:
                return ("Authorized"), 200
            else:
                return("Not authorized"), 401
        else:
            return("Not authorized"), 401

        data = request.get_json(silent=True) or {}
        method = request.method
        if method == "POST":
            pass
        elif method == "GET":
            return handlePassword(method, username)
        elif method == "PATCH":
            pass
        elif method == "DELETE":
            pass

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.FLASK_HOST, port=config.PORT_API)  # Run the Flask app on localhost:5000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.
