from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "智慧交通規劃 API 正在運行！"

@app.route('/api/test', methods=['GET'])
def test():
    name = request.args.get('name', 'Guest')
    return jsonify({
        "status": "success",
        "message": f"Hello, {name}!",
        "version": "1.0"
    })

@app.route('/api/call_external', methods=['GET'])
def call_external():
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/todos/1')
        data = response.json()
        return jsonify({
            "status": "success",
            "message": "成功呼叫外部 API！",
            "data": data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
