from flask import Flask, jsonify, request, session, redirect, url_for, render_template, make_response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import logging
import hashlib

import config.config as config

app = Flask(__name__, static_folder="web", static_url_path="/", template_folder="web/html")
app.secret_key = config.SECRET_KEY  # @CRITICAL: Change this to a secure key in production

# @CRITICAL: Change app.config.update before production
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE="Lax"
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

"""
@app.after_request
def set_csp(response):
    response.headers["Content-Security-Policy"] = (
        "default-src "self"; "
        "script-src "self"; "
        "object-src "none"; "
        "style-src "self"
        "base-uri "self"; "
        "frame-ancestors "none"; "
    )
    return response
"""

class FilterLogs(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # Filter out log messages containing ".svg" or "/favicon"
        return ".svg" not in msg and "/favicon" not in msg

log = logging.getLogger("werkzeug")
log.addFilter(FilterLogs())

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))  # Redirect to /login
    return render_template("index.html", username=session.get("username"), token = session.get("auth_token"))

# Note: The following endpoints are POST requests to handle login and logout actions.
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        if session.get("logged_in"):
            return redirect(url_for("index"))
        return render_template("login.html")
    else:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        try:
            api_res = requests.post(
                f"{config.HOST}:{config.PORT_API}/auth/login",
                json={
                "username": username,
                "password": password
                }
            )
            if api_res.ok:
                session["username"] = username
                session["logged_in"] = True
                message = api_res.json().get("message", "")
                token = message.split(", ("")[1].split(""")[0]  # You might want to improve this parsing later
                session["auth_token"] = token  # Store token securely in session (Flask will handle the cookie)
                return jsonify({"success": True}), 200
            else:
                return jsonify({"success": False}), 401
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

@app.route("/password", methods=["GET", "POST", "PATCH", "DELETE"])
def password():
    try:
        method = request.method
        access_token = session.get("access_token")

        def do_request():
            if method == "POST":
                data = request.get_json()
                payload = data.get("payload")
                return requests.post(
                    f"{config.HOST}:{config.PORT_API}/password",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"payload": payload}
                )

            elif method == "GET":
                return requests.get(
                    f"{config.HOST}:{config.PORT_API}/password",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

            elif method == "UPDATE":
                data = request.get_json()
                passwordId = data.get("passwordId")
                replacements = data.get("replacements")
                return requests.patch(
                    f"{config.HOST}:{config.PORT_API}/password",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"passwordId": passwordId, "replacements": replacements}
                )

            elif method == "DELETE":
                data = request.get_json()
                passwordId = data.get("passwordId")
                return requests.delete(
                    f"{config.HOST}:{config.PORT_API}/password",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json={"passwordId": passwordId}
                )

            else:
                raise Exception("Invalid method or request type")

        # First attempt
        api_res = do_request()

        # If expired, try refresh
        if api_res.status_code == 401:
            refresh_token = session.get("refresh_token")
            refresh_res = requests.post(
                f"{config.HOST}:{config.PORT_API}/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            if refresh_res.ok:
                access_token = refresh_res.json()["access_token"]
                session["access_token"] = access_token
                # Retry once with new token
                api_res = do_request()
            else:
                return jsonify({"success": False, "error": "Session expired"}), 401

        if api_res.ok:
            try:
                return jsonify({"success": True, "data": api_res.json()}), 200
            except Exception:
                return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def authenticate(token):
    try:
        api_res = requests.post(
            f"{config.HOST}:{config.PORT_API}/auth/token",
            json={
            "token": token
            }
        )
        if api_res:
            return True
        else:
            False
    except:
        pass   

@app.route("/salt", methods=["POST"])
def salt():
    data = request.get_json()
    username = data.get("username")
    try:
        api_res = requests.post(
            f"{config.HOST}:{config.PORT_API}/auth/salt",
            json={
            "requestMethod": "utils",
            "action": "fetchSalt",
            "username": username
            }
        )
        if api_res.ok:
            return jsonify({"success": True, "salt": api_res.json()}), 200
        else:
            return jsonify({"success": False}), 500
    except Exception as e:
        return jsonify({"succes": False, "error": str(e)}), 500

@app.route("/validate-session")
def valideSession():
    if session.get("logged_in"):
        return "", 200
    return "", 401

@app.route("/favicon")
def get_favicon():
    domain = request.args.get("domain")
    if not domain:
        return jsonify({"error": "Missing domain"}), 400

    # Google Favicon API URLs
    favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
    placeholder_url = "https://www.google.com/s2/favicons?domain=none&sz=64"

    try:
        # Fetch favicon and placeholder
        fav_resp = requests.get(favicon_url, timeout=10)
        place_resp = requests.get(placeholder_url, timeout=10)

        # Hash both images
        fav_hash = hashlib.sha256(fav_resp.content).hexdigest()
        place_hash = hashlib.sha256(place_resp.content).hexdigest()

        # Compare
        if fav_hash == place_hash:
            return jsonify({"favicon": None, "message": "No favicon found"})
        else:
            return jsonify({"favicon": favicon_url})
    except Exception as e:
        return jsonify({"favicon": None, "error": str(e)}), 500

@app.route("/check-password", methods=["POST"])
def check_password():
    data = request.get_json()
    prefix = data.get("prefix")
    suffix = data.get("suffix")

    if not prefix or not suffix:
        return jsonify({"error": "prefix and suffix required"}), 400

    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return jsonify({"error": "HIBP request failed"}), 502

    for line in resp.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return jsonify({"breached": True, "count": int(count)})

    return jsonify({"breached": False, "count": 0})

@app.route("/set-status", methods=["POST"])
def set_status():
    data = request.get_json()
    username = data.get("username")
    passwordId = data.get("passwordId")
    key = data.get("key")
    value = data.get("value")
    if key == "isBreached":
        try:
            api_res = requests.post(
                f"{config.HOST}:{config.PORT_API}/",
                json={
                "requestMethod": "utils",
                "action": "setBreached",
                "username": username,
                "passwordId": passwordId,
                "value": value
                }
            )
            if api_res.ok:
                return jsonify({"success": True}), 200
            else:
                return jsonify({"success": False}), 500
        except Exception as e:
            return jsonify({"succes": False, "error": str(e)}), 500
    elif key == "isFavorite":
        pass
    else:
        return jsonify({"error": "Key doesn't match an appropriate value"}), 400

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("username", None)
    session.pop("logged_in", None)
    if request.method == "POST":
        return "", 204  # no content for beacon
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.FLASK_HOST, port=config.PORT_WEB)  # Run the Flask app on passafe.local:4000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.
# This is a simple Flask application that serves as an API for password management.