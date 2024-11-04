from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello():
    host = request.host.split(':')[0]  # Get the server's host
    port = request.host.split(':')[1]  # Get the server's port
    response = {
        "message": "Response from service",
        "status": "success",
        "host": host,
        "port": port
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=6000)
