from flask import Flask, request, jsonify, render_template_string
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智慧交通規劃助手</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft JhengHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        #result {
            margin-top: 30px;
        }
        .route-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid #667eea;
        }
        .route-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .route-detail {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .gpt-card {
            background: #fff3cd;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            border-left: 5px solid #ffc107;
        }
        .gpt-card h3 {
            color: #ff6b6b;
            margin-bottom: 10px;
        }
        .loading {
            text-align: center;
            color: #667eea;
            font-size: 18px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>智慧交通規劃助手</h1>
        <p class="subtitle">結合傳統AI路徑規劃與生成式AI旅遊建議</p>
        
        <div class="input-group">
    <label>出發地點</label>
    <select id="origin">
        <option value="基隆市">基隆市</option>
        <option value="台北市">台北市</option>
        <option value="新北市">新北市</option>
        <option value="桃園市">桃園市</option>
        <option value="新竹市">新竹市</option>
        <option value="新竹縣">新竹縣</option>
        <option value="苗栗縣">苗栗縣</option>
        <option value="台中市" selected>台中市</option>
        <option value="彰化縣">彰化縣</option>
        <option value="南投縣">南投縣</option>
        <option value="雲林縣">雲林縣</option>
        <option value="嘉義市">嘉義市</option>
        <option value="嘉義縣">嘉義縣</option>
        <option value="台南市">台南市</option>
        <option value="高雄市">高雄市</option>
        <option value="屏東縣">屏東縣</option>
        <option value="宜蘭縣">宜蘭縣</option>
        <option value="花蓮縣">花蓮縣</option>
        <option value="台東縣">台東縣</option>
        <option value="澎湖縣">澎湖縣</option>
        <option value="金門縣">金門縣</option>
        <option value="連江縣">連江縣</option>
    </select>
</div>

<div class="input-group">
    <label>目的地</label>
    <select id="destination">
        <option value="基隆市">基隆市</option>
        <option value="台北市">台北市</option>
        <option value="新北市">新北市</option>
        <option value="桃園市">桃園市</option>
        <option value="新竹市">新竹市</option>
        <option value="新竹縣">新竹縣</option>
        <option value="苗栗縣">苗栗縣</option>
        <option value="台中市">台中市</option>
        <option value="彰化縣">彰化縣</option>
        <option value="南投縣">南投縣</option>
        <option value="雲林縣">雲林縣</option>
        <option value="嘉義市">嘉義市</option>
        <option value="嘉義縣">嘉義縣</option>
        <option value="台南市">台南市</option>
        <option value="高雄市">高雄市</option>
        <option value="屏東縣">屏東縣</option>
        <option value="宜蘭縣">宜蘭縣</option>
        <option value="花蓮縣" selected>花蓮縣</option>
        <option value="台東縣">台東縣</option>
        <option value="澎湖縣">澎湖縣</option>
        <option value="金門縣">金門縣</option>
        <option value="連江縣">連江縣</option>
    </select>
</div>
        
        <div class="input-group">
            <label>出發時間</label>
            <input type="datetime-local" id="departure_time" value="2024-12-20T09:00">
        </div>
        
        <button id="planBtn">開始規劃</button>
        
        <div class="loading" id="loading">正在規劃最佳路線...</div>
        
        <div id="result"></div>
    </div>
    
    <script>
        document.getElementById('planBtn').addEventListener('click', async function() {
            const origin = document.getElementById('origin').value;
            const destination = document.getElementById('destination').value;
            const departure_time = document.getElementById('departure_time').value;
            
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const button = document.getElementById('planBtn');
            
            loading.style.display = 'block';
            result.innerHTML = '';
            button.disabled = true;
            
            try {
                const response = await fetch('/api/plan_route', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ origin, destination, departure_time })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    const routes = data.routes;
                    const gptText = data.gpt_suggestions.split('\\n').join('<br>');
                    
                    result.innerHTML = 
                        '<div class="route-card">' +
                        '<h3>時間最短方案</h3>' +
                        '<div class="route-detail"><strong>類型：</strong>' + routes.fastest.type + '</div>' +
                        '<div class="route-detail"><strong>時長：</strong>' + routes.fastest.total_duration + ' 分鐘</div>' +
                        '<div class="route-detail"><strong>費用：</strong>NT$ ' + routes.fastest.total_cost + '</div>' +
                        '<div class="route-detail" style="color: #666; font-size: 14px; margin-top: 8px;">' + routes.fastest.note + '</div>' +
                        '</div>' +
    
                        '<div class="route-card">' +
                        '<h3>費用最低方案</h3>' +
                        '<div class="route-detail"><strong>類型：</strong>' + routes.cheapest.type + '</div>' +
                        '<div class="route-detail"><strong>時長：</strong>' + routes.cheapest.total_duration + ' 分鐘</div>' +
                        '<div class="route-detail"><strong>費用：</strong>NT$ ' + routes.cheapest.total_cost + '</div>' +
                        '<div class="route-detail" style="color: #666; font-size: 14px; margin-top: 8px;">' + routes.cheapest.note + '</div>' +
                        '</div>' +
    
                        '<div class="route-card">' +
                        '<h3>綜合推薦方案</h3>' +
                        '<div class="route-detail"><strong>類型：</strong>' + routes.recommended.type + '</div>' +
                        '<div class="route-detail"><strong>時長：</strong>' + routes.recommended.total_duration + ' 分鐘</div>' +
                        '<div class="route-detail"><strong>費用：</strong>NT$ ' + routes.recommended.total_cost + '</div>' +
                        '<div class="route-detail" style="color: #666; font-size: 14px; margin-top: 8px;">' + routes.recommended.note + '</div>' +
                        '</div>' +
    
                        '<div class="gpt-card">' +
                        '<h3>AI 旅遊建議</h3>' +
                        '<p>' + gptText + '</p>' +
                        '</div>';
                }
            } catch (error) {
                result.innerHTML = '<p style="color: red;">發生錯誤：' + error + '</p>';
            } finally {
                loading.style.display = 'none';
                button.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/plan_route', methods=['POST'])
def plan_route():
    data = request.get_json()
    
    origin = data.get('origin')
    destination = data.get('destination')
    departure_time = data.get('departure_time')
    
    if not all([origin, destination, departure_time]):
        return jsonify({
            "status": "error",
            "message": "缺少必要參數"
        }), 400
    
    routes = calculate_routes(origin, destination, departure_time)
    best_routes = select_best_routes(routes)
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
    routes = []
    
    # 方案1: 高鐵+台鐵（有優惠票種）
    routes.append({
        "id": 1,
        "type": "高鐵+台鐵",
        "note": "高鐵可購買早鳥票或大學生票更優惠",
        "segments": [
            {"mode": "高鐵", "from": origin, "to": "台北", "duration": 50, "cost": 700, "ticket_type": "標準票"},
            {"mode": "台鐵", "from": "台北", "to": destination, "duration": 180, "cost": 583, "ticket_type": "全票"}
        ],
        "total_duration": 230,
        "total_cost": 1283,
        "transfers": 1
    })
    
    # 方案2: 台鐵直達（無優惠票）
    routes.append({
        "id": 2,
        "type": "台鐵直達",
        "note": "台鐵無優惠票價，一律以全票計算",
        "segments": [
            {"mode": "台鐵", "from": origin, "to": destination, "duration": 300, "cost": 966, "ticket_type": "全票"}
        ],
        "total_duration": 300,
        "total_cost": 966,
        "transfers": 0
    })
    
    # 方案3: 飛機
    routes.append({
        "id": 3,
        "type": "飛機",
        "note": "最快速但價格較高",
        "segments": [
            {"mode": "飛機", "from": origin, "to": destination, "duration": 60, "cost": 2800, "ticket_type": "經濟艙"}
        ],
        "total_duration": 60,
        "total_cost": 2800,
        "transfers": 0
    })
    
    return routes

def select_best_routes(routes):
    fastest = min(routes, key=lambda r: r['total_duration'])
    cheapest = min(routes, key=lambda r: r['total_cost'])
    
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
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return "請設定 OPENAI_API_KEY 環境變數"
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        prompt = f"""用戶要從{origin}前往{destination}。
推薦方案：{routes['recommended']['type']}，時長{routes['recommended']['total_duration']}分鐘，費用{routes['recommended']['total_cost']}元。

請用繁體中文生成簡潔建議（100字內）：
1. 穿搭建議
2. 轉乘注意事項
3. 景點美食推薦"""
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"GPT API錯誤"
            
    except Exception as e:
        return f"GPT建議暫時無法使用"

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "success", "message": "API is working!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


