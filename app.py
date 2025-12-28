from flask import Flask, request, jsonify, render_template_string
import requests
from datetime import datetime
import os

app = Flask(__name__)

# 班次資料庫
SCHEDULES = {
    "hsr_taichung_taipei": [
        {"train_no": "1202", "depart": "07:21", "arrive": "08:04", "duration": 43},
        {"train_no": "0802", "depart": "07:25", "arrive": "08:29", "duration": 64},
        {"train_no": "0204", "depart": "07:48", "arrive": "08:34", "duration": 46},
        {"train_no": "1602", "depart": "07:40", "arrive": "08:39", "duration": 59}
    ],
    "tra_taipei_hualien": [
        {"train_no": "3000-472", "type": "自強3000", "depart": "08:40", "arrive": "11:05", "duration": 145},
        {"train_no": "212", "type": "自強", "depart": "08:52", "arrive": "11:51", "duration": 179},
        {"train_no": "3000-418", "type": "自強3000", "depart": "09:26", "arrive": "11:46", "duration": 140},
        {"train_no": "3000-280", "type": "自強3000", "depart": "09:45", "arrive": "12:11", "duration": 146}
    ],
    "tra_taichung_hualien": [
        {"train_no": "170", "type": "自強", "depart": "07:24", "arrive": "12:44", "duration": 320},
        {"train_no": "3000-280", "type": "自強3000", "depart": "07:49", "arrive": "12:11", "duration": 262}
    ]
}

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
            max-width: 900px;
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
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .loading {
            text-align: center;
            color: #667eea;
            display: none;
            margin: 20px 0;
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
            cursor: pointer;
            transition: all 0.3s;
        }
        .route-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .route-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .route-summary {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .schedule-list {
            display: none;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #e0e0e0;
        }
        .schedule-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            cursor: pointer;
            transition: all 0.3s;
        }
        .schedule-item:hover {
            border-color: #667eea;
            box-shadow: 0 2px 8px rgba(102,126,234,0.2);
        }
        .schedule-detail {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 14px;
        }
        .gpt-section {
            background: #fff3cd;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            border-left: 5px solid #ffc107;
            display: none;
        }
        .gpt-section h3 {
            color: #ff6b6b;
            margin-bottom: 10px;
        }
        .book-link {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
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
                <option value="台中市" selected>台中市</option>
            </select>
        </div>
        
        <div class="input-group">
            <label>目的地</label>
            <select id="destination">
                <option value="花蓮縣" selected>花蓮縣</option>
            </select>
        </div>
        
        <div class="input-group">
            <label>出發時間</label>
            <input type="datetime-local" id="departure_time">
        </div>
        
        <button id="planBtn">開始規劃</button>
        
        <div class="loading" id="loading">正在規劃最佳路線...</div>
        
        <div id="result"></div>
        <div class="gpt-section" id="gptSection"></div>
    </div>
    
    <script>
        // 設定預設時間為今天 07:00
        const now = new Date();
        now.setHours(7, 0, 0, 0);
        const dateStr = now.toISOString().slice(0, 16);
        document.getElementById('departure_time').value = dateStr;
        
        let currentData = null;
        
        document.getElementById('planBtn').addEventListener('click', async function() {
            const origin = document.getElementById('origin').value;
            const destination = document.getElementById('destination').value;
            const departure_time = document.getElementById('departure_time').value;
            
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            const gptSection = document.getElementById('gptSection');
            
            loading.style.display = 'block';
            result.innerHTML = '';
            gptSection.style.display = 'none';
            
            try {
                const response = await fetch('/api/plan_route', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ origin, destination, departure_time })
                });
                
                const data = await response.json();
                currentData = data;
                
                if (data.status === 'success') {
                    displayRoutes(data.routes);
                }
            } catch (error) {
                result.innerHTML = '<p style="color: red;">發生錯誤：' + error + '</p>';
            } finally {
                loading.style.display = 'none';
            }
        });
        
        function displayRoutes(routes) {
            const result = document.getElementById('result');
            
            result.innerHTML = `
                <div class="route-card" onclick="toggleSchedule('fastest')">
                    <h3>⚡ 時間最短方案</h3>
                    <div class="route-summary"><strong>類型：</strong>高鐵+台鐵</div>
                    <div class="route-summary"><strong>預估時長：</strong>約 3.5-4 小時</div>
                    <div class="route-summary"><strong>預估費用：</strong>NT$ 1,283</div>
                    <div class="route-summary" style="color: #666; font-size: 14px;">高鐵可購買早鳥票或大學生票更優惠</div>
                    <div id="fastest-schedule" class="schedule-list"></div>
                </div>
                
                <div class="route-card" onclick="toggleSchedule('cheapest')">
                    <h3>💰 費用最低方案</h3>
                    <div class="route-summary"><strong>類型：</strong>台鐵直達</div>
                    <div class="route-summary"><strong>預估時長：</strong>4-5 小時</div>
                    <div class="route-summary"><strong>預估費用：</strong>NT$ 966</div>
                    <div class="route-summary" style="color: #666; font-size: 14px;">台鐵無優惠票價，一律以全票計算</div>
                    <div id="cheapest-schedule" class="schedule-list"></div>
                </div>
                
                <div class="route-card" onclick="toggleSchedule('recommended')">
                    <h3>⭐ 推薦方案（折衷）</h3>
                    <div class="route-summary"><strong>類型：</strong>高鐵+台鐵（轉乘時間充裕）</div>
                    <div class="route-summary"><strong>預估時長：</strong>約 4 小時</div>
                    <div class="route-summary"><strong>預估費用：</strong>NT$ 1,283</div>
                    <div class="route-summary" style="color: #666; font-size: 14px;">轉乘時間較充裕，不易錯過班次</div>
                    <div id="recommended-schedule" class="schedule-list"></div>
                </div>
            `;
        }
        
        async function toggleSchedule(type) {
            const scheduleDiv = document.getElementById(type + '-schedule');
            
            if (scheduleDiv.style.display === 'block') {
                scheduleDiv.style.display = 'none';
                return;
            }
            
            // 關閉其他展開的
            document.querySelectorAll('.schedule-list').forEach(el => el.style.display = 'none');
            
            // 載入班次
            const response = await fetch('/api/get_schedules?type=' + type);
            const data = await response.json();
            
            scheduleDiv.innerHTML = data.schedules.map(s => 
                '<div class="schedule-item" onclick="selectSchedule(\'' + type + '\', ' + s.id + ')">' +
                '<div class="schedule-detail"><strong>' + s.title + '</strong></div>' +
                '<div class="schedule-detail">' + s.detail + '</div>' +
                '<div class="schedule-detail"><span>時長：' + s.duration + '</span><span>費用：NT$ ' + s.cost + '</span></div>' +
                '</div>'
            ).join('');
            
            scheduleDiv.style.display = 'block';
        }
        
        async function selectSchedule(type, scheduleId) {
            const response = await fetch('/api/get_suggestion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, schedule_id: scheduleId })
            });
            
            const data = await response.json();
            
            const gptSection = document.getElementById('gptSection');
            gptSection.innerHTML = `
                <h3>🤖 AI 旅遊建議</h3>
                <p>${data.suggestion.replace(/\\n/g, '<br>')}</p>
                <a href="${data.booking_link}" target="_blank" class="book-link">前往訂票</a>
            `;
            gptSection.style.display = 'block';
        }
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
    return jsonify({
        "status": "success",
        "routes": {}
    })

@app.route('/api/get_schedules', methods=['GET'])
def get_schedules():
    route_type = request.args.get('type')
    
    if route_type == 'fastest':
        # 最快方案：最佳高鐵+台鐵組合
        schedules = [
            {
                "id": 1,
                "title": "高鐵1202 (07:21→08:04) + 台鐵3000-472 (08:40→11:05)",
                "detail": "台中07:21出發 → 花蓮11:05抵達",
                "duration": "3小時44分",
                "cost": "1,283"
            },
            {
                "id": 2,
                "title": "高鐵0204 (07:48→08:34) + 台鐵212 (08:52→11:51)",
                "detail": "台中07:48出發 → 花蓮11:51抵達",
                "duration": "4小時3分",
                "cost": "1,283"
            }
        ]
    elif route_type == 'cheapest':
        # 最省方案：台鐵直達
        schedules = [
            {
                "id": 3,
                "title": "台鐵自強170 (07:24→12:44)",
                "detail": "台中直達花蓮，無需轉乘",
                "duration": "5小時20分",
                "cost": "966"
            },
            {
                "id": 4,
                "title": "台鐵自強3000-280 (07:49→12:11)",
                "detail": "台中直達花蓮，無需轉乘",
                "duration": "4小時22分",
                "cost": "966"
            }
        ]
    else:  # recommended
        # 推薦方案：轉乘時間較充裕
        schedules = [
            {
                "id": 5,
                "title": "高鐵0802 (07:25→08:29) + 台鐵3000-418 (09:26→11:46)",
                "detail": "台中07:25出發 → 花蓮11:46抵達（轉乘時間57分鐘）",
                "duration": "4小時21分",
                "cost": "1,283"
            },
            {
                "id": 6,
                "title": "高鐵1602 (07:40→08:39) + 台鐵3000-280 (09:45→12:11)",
                "detail": "台中07:40出發 → 花蓮12:11抵達（轉乘時間66分鐘）",
                "duration": "4小時31分",
                "cost": "1,283"
            }
        ]
    
    return jsonify({"schedules": schedules})

@app.route('/api/get_suggestion', methods=['POST'])
def get_suggestion():
    data = request.get_json()
    schedule_id = data.get('schedule_id')
    
    # 根據班次生成GPT建議
    suggestion = generate_gpt_suggestion(schedule_id)
    
    # 售票連結
    if schedule_id in [1, 2, 5, 6]:
        booking_link = "https://www.thsrc.com.tw/"  # 高鐵
    else:
        booking_link = "https://www.railway.gov.tw/"  # 台鐵
    
    return jsonify({
        "suggestion": suggestion,
        "booking_link": booking_link
    })

def generate_gpt_suggestion(schedule_id):
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return "請設定 OPENAI_API_KEY"
        
        schedules_info = {
            1: "高鐵07:21出發，08:04抵達台北，轉乘08:40台鐵，11:05抵達花蓮",
            2: "高鐵07:48出發，08:34抵達台北，轉乘08:52台鐵，11:51抵達花蓮",
            3: "台鐵自強號07:24直達，12:44抵達花蓮",
            4: "台鐵自強3000號07:49直達，12:11抵達花蓮",
            5: "高鐵07:25出發，08:29抵達台北，轉乘09:26台鐵，11:46抵達花蓮",
            6: "高鐵07:40出發，08:39抵達台北，轉乘09:45台鐵，12:11抵達花蓮"
        }
        
        info = schedules_info.get(schedule_id, "")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        prompt = f"""用戶選擇了以下班次：{info}

請用繁體中文提供簡潔建議（100字內）：
1. 根據出發時間的穿搭建議
2. 如果有轉乘，提醒轉乘注意事項
3. 抵達花蓮後的景點美食推薦"""
        
        request_data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200
        }
        
        response = requests.post(url, headers=headers, json=request_data, timeout=30)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "GPT建議暫時無法使用"
            
    except Exception as e:
        return f"AI建議載入中..."

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
