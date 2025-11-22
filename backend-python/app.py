from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/metrics', methods=['POST'])
def receive_metrics():
    data = request.json
    print("Received metrics:", data)
    with open("metrics_log.json", "a") as f:
        f.write(f"{data}\n")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
