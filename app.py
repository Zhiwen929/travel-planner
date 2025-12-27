from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta
import os
from openai import OpenAI

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
    
    # 計算三個方案（傳統AI - 路徑規劃演算法）
    routes = calculate_routes(origin, destination, departure_time)
    
    # 多目標優化（傳統AI）：篩選三個方案
    best_routes = select_best_routes(routes)
    
    # 生成 GPT-4 建議（生成式AI）
    gpt_suggestions = generate_suggestions(origin, destination, best_routes)
    
    return jsonify({
        "status": "success",
        "query": {
            "origin": origin,
            "destination": destination,
            "departure_time": departure_time
        },
        "routes": best_routes,
        "gpt_suggestions": gpt_suggestions
    })

def calculate_routes(origin, destination, departure_time):
    """路徑規劃演算法（傳統AI）"""
    routes = []
    
    # 方案1: 高鐵+台鐵
    routes.append({
        "id": 1,
        "type": "高鐵+台鐵",
        "segments": [
            {"mode": "高鐵", "from": origin, "to": "台北", "duration": 50, "cost": 700},
            {"mode": "台鐵", "from": "台北", "to": destination, "duration": 120, "cost": 440}
        ],
        "total_duration": 170,
        "total_cost": 1140,
        "transfers": 1
    })
    
    # 方案2: 台鐵直達
    routes.append({
        "id": 2,
        "type": "台鐵直達",
        "segments": [
            {"mode": "台鐵", "from": origin, "to": destination, "duration": 240, "cost": 563}
        ],
        "total_duration": 240,
        "total_cost": 563,
        "transfers": 0
    })
    
    # 方案3: 飛機
    routes.append({
        "id": 3,
        "type": "飛機",
        "segments": [
            {"mode": "飛機", "from": origin, "to": destination, "duration": 60, "cost": 2800}
        ],
        "total_duration": 60,
        "total_cost": 2800,
        "transfers": 0
    })
    
    return routes

def select_best_routes(routes):
    """多目標優化（傳統AI）"""
    # 找出時間最短
    fastest = min(routes, key=lambda r: r['total_duration'])
    
    # 找出費用最低
    cheapest = min(routes, key=lambda r: r['total_cost'])
    
    # 計算綜合最佳（時間和費用各佔50%權重）
    for route in routes:
        time_score = route['total_duration'] / max([r['total_duration'] for r in routes])
        cost_score = route['total_cost'] / max([r['total_cost'] for r in routes])
        route['combined_score'] = 0.5 * time_score + 0.5 * cost_score
    
    recommended = min(routes, key=lambda r: r['combined_score'])
    
    return {
        "fastest": fastest,
        "cheapest": cheapest,
        "recommended": recommended
    }

def generate_suggestions(origin, destination, routes):
    """使用 GPT-4 生成旅遊建議（生成式AI）"""
    try:
        # 從環境變數讀取 API Key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return "請設定 OPENAI_API_KEY 環境變數"
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""用戶要從{origin}前往{destination}。
推薦方案：{routes['recommended']['type']}，時長{routes['recommended']['total_duration']}分鐘，費用{routes['recommended']['total_cost']}元。

請用繁體中文生成簡潔建議（150字內）：
1. 天氣穿搭建議
2. 轉乘注意事項（如果有轉乘）
3. 目的地景點美食推薦"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"GPT建議暫時無法使用: {str(e)}"

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "message": "API is working!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
