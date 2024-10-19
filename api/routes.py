from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'message': 'Hello, World!'})

@app.route('/api/data', methods=['GET'])
def get_data():
    # Extracting query parameters
    method = request.args.get('name')
    if method == 'authenticate':
        authenticate()
    

@app.route('/api/data', methods=['POST'])
def crete_date():
    new_data = request.get_json()
    return jsonify(new_data), 201

def authenticate():
    username = request.args.get('username')
    print(username)


if __name__ == '__main__':
    app.run(debug=True)