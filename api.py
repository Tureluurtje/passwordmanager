from flask import Flask, jsonify, request
from flask_cors import CORS

from core.server import requestHandler
import config.config as config

app = Flask(__name__)
CORS(app)


@app.route('/ping/')
def ping():
    #Server ping
    return jsonify({'message': 'pong'})

# NOTE: This route handles API requests
@app.route('/', methods=['GET'])
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
    app.run(debug=config.DEBUG, host=config.FLASK_HOST, port=config.PORT_API)  # Run the Flask app on localhost:5000
# Note: In production, use a proper WSGI server like Gunicorn or uWSGI.