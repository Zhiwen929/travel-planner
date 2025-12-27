from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return "智慧交通規劃 API - v1.0"

@app.route('/api/plan_route', methods=['POST'])
def plan_route():
    """主要的路徑規劃API"""
    data = request.get_json()
    
    origin = data.get('origin')
    destination = data.get('destination')
    departure_time = data.get('departure_time')
    
    if not all([origin, destination, departure_time]):
        return jsonify({
            "status": "error",
            "message": "缺少必要參數: origin, destination, departure_time"
        }), 400
    
    # 計算三個方案（暫時用模擬資料）
    routes = calculate_routes(origin, destination, departure_time)
    
    # 多目標優化：篩選三個方案
    best_routes = select_best_routes(routes)
    
    return jsonify({
        "status": "success",
        "query": {
            "origin": origin,
            "destination": destination,
            "departure_time": departure_time
        },
        "routes": best_routes
    })

def calculate_routes(origin, destination, departure_time):
    """路徑規劃演算法（傳統AI）- 目前用模擬資料"""
    
    # 模擬計算出的所有可行路線
    routes = []
    
    # 方案1: 高鐵+台鐵（快速但貴）
    routes.append({
        "id": 1,
        "type": "HSR+TRA",
        "segments": [
            {"mode": "高鐵", "from": origin, "to": "台北", "duration": 50, "cost": 700},
            {"mode": "台鐵", "from": "台北", "to": destination, "duration": 120, "cost": 440}
        ],
        "total_duration": 170,  # 分鐘
        "total_cost": 1140,
        "transfers": 1
    })
    
    # 方案2: 台鐵直達（慢但便宜）
    routes.append({
        "id": 2,
        "type": "TRA",
        "segments": [
            {"mode": "台鐵", "from": origin, "to": destination, "duration": 240, "cost": 563}
        ],
        "total_duration": 240,
        "total_cost": 563,
        "transfers": 0
    })
    
    # 方案3: 飛機（超快但最貴）
    routes.append({
        "id": 3,
        "type": "Flight",
        "segments": [
            {"mode": "飛機", "from": origin, "to": destination, "duration": 60, "cost": 2800}
        ],
        "total_duration": 60,
        "total_cost": 2800,
        "transfers": 0
    })
    
    return routes

def select_best_routes(routes):
    """多目標優化（傳統AI）- 篩選三個最佳方案"""
    
    # 找出時間最短
    fastest = min(routes, key=lambda r: r['total_duration'])
    
    # 找出費用最低
    cheapest = min(routes, key=lambda r: r['total_cost'])
    
    # 計算綜合最佳（時間和費用各佔50%權重）
    for route in routes:
        # 正規化分數
        time_score = route['total_duration'] / max([r['total_duration'] for r in routes])
        cost_score = route['total_cost'] / max([r['total_cost'] for r in routes])
        route['combined_score'] = 0.5 * time_score + 0.5 * cost_score
    
    recommended = min(routes, key=lambda r: r['combined_score'])
    
    return {
        "fastest": fastest,
        "cheapest": cheapest,
        "recommended": recommended
    }

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "message": "API is working!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
