from flask import Flask, request, jsonify, render_template_string
import requests
from datetime import datetime
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
        .booked-trips {
            background: #e8f5e9;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 5px solid #4caf50;
            display: none;
        }
        .booked-trips h2 {
            color: #2e7d32;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .trip-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border: 2px solid #a5d6a7;
            position: relative;
        }
        .trip-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .trip-route {
            font-weight: bold;
            color: #2e7d32;
            font-size: 1.1em;
        }
        .trip-detail {
            font-size: 14px;
            color: #666;
            margin: 5px 0;
        }
        .delete-trip {
            background: #f44336;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        .delete-trip:hover {
            background: #d32f2f;
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
            margin: 5px 0;
            font-size: 14px;
        }
        .gpt-section {
            background: #fff3cd;
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
            border-left: 5px solid #ffc107;
            display: none;
        }
        .gpt-section h3 {
            color: #ff6b6b;
            margin-bottom: 10px;
        }
        .book-link, .confirm-trip {
            display: inline-block;
            margin-top: 10px;
            margin-right: 10px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 14px;
        }
        .confirm-trip {
            background: #4caf50;
        }
        .confirm-trip:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>智慧交通規劃助手</h1>
        <p class="subtitle">結合傳統AI路徑規劃與生成式AI旅遊建議</p>
        
        <div class="booked-trips" id="bookedTrips">
            <h2>📋 已訂行程</h2>
            <div id="tripsList"></div>
        </div>
        
        <div class="input-group">
            <label>出發地點</label>
            <select id="origin">
                <option value="基隆市">基隆市</option>
                <option value="台北市" selected>台北市</option>
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
                <option value="台南市" selected>台南市</option>
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
            <input type="datetime-local" id="departure_time">
        </div>
        
        <button id="planBtn">開始規劃</button>
        
        <div class="loading" id="loading">正在規劃最佳路線...</div>
        
        <div id="result"></div>
    </div>
    
    <script>
        const now = new Date();
        now.setHours(7, 0, 0, 0);
        document.getElementById('departure_time').value = now.toISOString().slice(0, 16);
        
        let bookedTrips = [];
        let currentSelection = null;
        
        document.getElementById('planBtn').addEventListener('click', function() {
            const origin = document.getElementById('origin').value;
            const destination = document.getElementById('destination').value;
            
            if (origin === destination) {
                alert('出發地點和目的地不能相同！');
                return;
            }
            
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            loading.style.display = 'block';
            result.innerHTML = '';
            
            setTimeout(function() {
                displayRoutes();
                loading.style.display = 'none';
            }, 500);
        });
        
        function displayRoutes() {
            const result = document.getElementById('result');
            result.innerHTML = `
                <div class="route-card" data-type="fastest">
                    <h3>⚡ 時間最短方案</h3>
                    <div class="route-summary"><strong>類型：</strong>高鐵+台鐵</div>
                    <div class="route-summary"><strong>預估時長：</strong>約 3.5-4 小時</div>
                    <div class="route-summary"><strong>預估費用：</strong>NT$ 1,283</div>
                    <div class="route-summary" style="color: #666; font-size: 14px;">高鐵可購買早鳥票或大學生票更優惠</div>
                    <div class="schedule-list"></div>
                    <div class="gpt-section"></div>
                </div>
                
                <div class="route-card" data-type="cheapest">
                    <h3>💰 費用最低方案</h3>
                    <div class="route-summary"><strong>類型：</strong>台鐵直達</div>
                    <div class="route-summary"><strong>預估時長：</strong>4-5 小時</div>
                    <div class="route-summary"><strong>預估費用：</strong>NT$ 966</div>
                    <div class="route-summary" style="color: #666; font-size: 14px;">台鐵無優惠票價，一律以全票計算</div>
                    <div class="schedule-list"></div>
                    <div class="gpt-section"></div>
                </div>
                
                <div class="route-card" data-type="recommended">
                    <h3>⭐ 推薦方案（折衷）</h3>
                    <div class="route-summary"><strong>類型：</strong>高鐵+台鐵（轉乘時間充裕）</div>
                    <div class="route-summary"><strong>預估時長：</strong>約 4 小時</div>
                    <div class="route-summary"><strong>預估費用：</strong>NT$ 1,283</div>
                    <div class="route-summary" style="color: #666; font-size: 14px;">轉乘時間較充裕，不易錯過班次</div>
                    <div class="schedule-list"></div>
                    <div class="gpt-section"></div>
                </div>
            `;
            
            document.querySelectorAll('.route-card').forEach(function(card) {
                card.addEventListener('click', function() {
                    toggleSchedule(this.getAttribute('data-type'));
                });
            });
        }
        
        async function toggleSchedule(type) {
            const card = document.querySelector('[data-type="' + type + '"]');
            const scheduleDiv = card.querySelector('.schedule-list');
            
            if (scheduleDiv.style.display === 'block') {
                scheduleDiv.style.display = 'none';
                return;
            }
            
            document.querySelectorAll('.schedule-list').forEach(function(el) {
                el.style.display = 'none';
            });
            
            document.querySelectorAll('.gpt-section').forEach(function(el) {
                el.style.display = 'none';
            });
            
            const response = await fetch('/api/get_schedules?type=' + type);
            const data = await response.json();
            
            let html = '';
            data.schedules.forEach(function(s) {
                html += '<div class="schedule-item" data-schedule="' + s.id + '">' +
                    '<div class="schedule-detail"><strong>' + s.title + '</strong></div>' +
                    '<div class="schedule-detail">' + s.detail + '</div>' +
                    '<div class="schedule-detail">時長：' + s.duration + ' | 費用：NT$ ' + s.cost + '</div>' +
                    '</div>';
            });
            
            scheduleDiv.innerHTML = html;
            scheduleDiv.style.display = 'block';
            
            scheduleDiv.querySelectorAll('.schedule-item').forEach(function(item) {
                item.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const scheduleId = parseInt(this.getAttribute('data-schedule'));
                    selectSchedule(type, scheduleId);
                });
            });
        }
        
        async function selectSchedule(type, scheduleId) {
            const card = document.querySelector('[data-type="' + type + '"]');
            const gptSection = card.querySelector('.gpt-section');
            
            document.querySelectorAll('.gpt-section').forEach(function(el) {
                el.style.display = 'none';
            });
            
            const response = await fetch('/api/get_suggestion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: type, schedule_id: scheduleId })
            });
            
            const data = await response.json();
            const suggestionText = data.suggestion.split('\\n').join('<br>');
            
            currentSelection = {
                type: type,
                scheduleId: scheduleId,
                scheduleTitle: data.schedule_title,
                cost: data.cost,
                bookingLinks: data.booking_links
            };
            
            let bookingHTML = '';
            if (data.booking_links.hsr && data.booking_links.tra) {
                bookingHTML = '<a href="' + data.booking_links.hsr + '" target="_blank" class="book-link">訂購高鐵</a> ' +
                              '<a href="' + data.booking_links.tra + '" target="_blank" class="book-link">訂購台鐵</a>';
            } else {
                bookingHTML = '<a href="' + data.booking_links.tra + '" target="_blank" class="book-link">前往訂票</a>';
            }
            
            gptSection.innerHTML = '<h3>🤖 助手建議</h3>' +
                '<p>' + suggestionText + '</p>' +
                bookingHTML +
                '<button class="confirm-trip" onclick="confirmTrip()">✓ 確認行程</button>';
            
            gptSection.style.display = 'block';
        }
        
        function confirmTrip() {
            if (!currentSelection) return;
            
            const origin = document.getElementById('origin').value;
            const destination = document.getElementById('destination').value;
            const departureTime = document.getElementById('departure_time').value;
            
            const trip = {
                id: Date.now(),
                origin: origin,
                destination: destination,
                departureTime: departureTime,
                schedule: currentSelection.scheduleTitle,
                cost: currentSelection.cost,
                bookingLinks: currentSelection.bookingLinks
            };
            
            bookedTrips.push(trip);
            updateBookedTrips();
            
            alert('✓ 行程已加入！');
        }
        
        function updateBookedTrips() {
            const bookedTripsDiv = document.getElementById('bookedTrips');
            const tripsList = document.getElementById('tripsList');
            
            if (bookedTrips.length === 0) {
                bookedTripsDiv.style.display = 'none';
                return;
            }
            
            bookedTripsDiv.style.display = 'block';
            
            let html = '';
            bookedTrips.forEach(function(trip) {
                const date = new Date(trip.departureTime);
                const formattedDate = date.getFullYear() + '/' + 
                                      (date.getMonth() + 1) + '/' + 
                                      date.getDate() + ' ' +
                                      String(date.getHours()).padStart(2, '0') + ':' +
                                      String(date.getMinutes()).padStart(2, '0');
                
                html += '<div class="trip-item">' +
                    '<div class="trip-item-header">' +
                    '<div class="trip-route">' + trip.origin + ' → ' + trip.destination + '</div>' +
                    '<button class="delete-trip" onclick="deleteTrip(' + trip.id + ')">刪除</button>' +
                    '</div>' +
                    '<div class="trip-detail">📅 ' + formattedDate + '</div>' +
                    '<div class="trip-detail">🚄 ' + trip.schedule + '</div>' +
                    '<div class="trip-detail">💰 NT$ ' + trip.cost + '</div>' +
                    '</div>';
            });
            
            tripsList.innerHTML = html;
            bookedTripsDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        function deleteTrip(tripId) {
            bookedTrips = bookedTrips.filter(function(trip) {
                return trip.id !== tripId;
            });
            updateBookedTrips();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get_schedules', methods=['GET'])
def get_schedules():
    route_type = request.args.get('type')
    
    if route_type == 'fastest':
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
    else:
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
    
    # 獲取班次詳細資訊
    schedule_info = {
        1: {"title": "高鐵1202 (07:21→08:04) + 台鐵3000-472 (08:40→11:05)", "cost": "1,283"},
        2: {"title": "高鐵0204 (07:48→08:34) + 台鐵212 (08:52→11:51)", "cost": "1,283"},
        3: {"title": "台鐵自強170 (07:24→12:44)", "cost": "966"},
        4: {"title": "台鐵自強3000-280 (07:49→12:11)", "cost": "966"},
        5: {"title": "高鐵0802 (07:25→08:29) + 台鐵3000-418 (09:26→11:46)", "cost": "1,283"},
        6: {"title": "高鐵1602 (07:40→08:39) + 台鐵3000-280 (09:45→12:11)", "cost": "1,283"}
    }
    
    suggestion = generate_gpt_suggestion(schedule_id)
    
    if schedule_id in [1, 2, 5, 6]:
        booking_links = {
            "hsr": "https://www.thsrc.com.tw/",
            "tra": "https://www.railway.gov.tw/"
        }
    else:
        booking_links = {
            "tra": "https://www.railway.gov.tw/"
        }
    
    return jsonify({
        "suggestion": suggestion,
        "booking_links": booking_links,
        "schedule_title": schedule_info[schedule_id]["title"],
        "cost": schedule_info[schedule_id]["cost"]
    })

# 修改後的 generate_gpt_suggestion 函數

# 修改後的 generate_gpt_suggestion 函數

def generate_gpt_suggestion(schedule_id):
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return "請設定 OPENAI_API_KEY"
        
        # 班次資訊包含轉乘時間細節
        schedules_info = {
            1: {
                "detail": "高鐵07:21出發，08:04抵達台北，轉乘08:40台鐵，11:05抵達花蓮",
                "transfer_time": 36,  # 分鐘
                "transfer_type": "medium"
            },
            2: {
                "detail": "高鐵07:48出發，08:34抵達台北，轉乘08:52台鐵，11:51抵達花蓮",
                "transfer_time": 18,  # 分鐘
                "transfer_type": "tight"
            },
            3: {
                "detail": "台鐵自強號07:24直達，12:44抵達花蓮",
                "transfer_time": 0,
                "transfer_type": "direct"
            },
            4: {
                "detail": "台鐵自強3000號07:49直達，12:11抵達花蓮",
                "transfer_time": 0,
                "transfer_type": "direct"
            },
            5: {
                "detail": "高鐵07:25出發，08:29抵達台北，轉乘09:26台鐵，11:46抵達花蓮",
                "transfer_time": 57,  # 分鐘
                "transfer_type": "long"
            },
            6: {
                "detail": "高鐵07:40出發，08:39抵達台北，轉乘09:45台鐵，12:11抵達花蓮",
                "transfer_time": 66,  # 分鐘
                "transfer_type": "long"
            }
        }
        
        info = schedules_info.get(schedule_id, {})
        detail = info.get("detail", "")
        transfer_time = info.get("transfer_time", 0)
        transfer_type = info.get("transfer_type", "")
        
        # 根據轉乘時間類型生成不同的 prompt
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 基本資訊
        base_info = f"""行程：從台中到花蓮
班次：{detail}
日期：2026年1月13日（週二）
出發時間：早上7點多

天氣狀況：1月的花蓮正值東北季風盛行期，天氣偏涼，建議穿著保暖衣物。"""
        
        # 根據轉乘類型調整建議重點
        if transfer_type == "direct":
            prompt = f"""{base_info}

這是直達班次，無需轉乘。請用繁體中文提供簡潔建議（100字內）：
1. 早上出發的穿著建議（1月花蓮天氣涼）
2. 車程較長，提醒攜帶水或點心
3. 簡單的花蓮景點提醒"""
        
        elif transfer_type == "tight":
            # 18分鐘轉乘
            prompt = f"""{base_info}
轉乘時間：約{transfer_time}分鐘

這是緊湊的轉乘時間。請用繁體中文提供簡潔建議（100字內）：
1. 1月花蓮東北季風強，天氣涼，建議穿著保暖
2. 轉乘時間緊迫（{transfer_time}分鐘），建議在高鐵上或高鐵出發前吃點東西，抵達台北車站後直接前往台鐵月台
3. 早上出發，可以稍微休息一下"""
        
        elif transfer_type == "medium":
            # 30-40分鐘轉乘
            prompt = f"""{base_info}
轉乘時間：約{transfer_time}分鐘

轉乘時間適中。請用繁體中文提供簡潔建議（100字內）：
1. 1月花蓮東北季風強，天氣涼，建議穿著保暖
2. 轉乘時間約{transfer_time}分鐘，可以在台北車站地下街快速買點東西吃或逛逛商店，台鐵月台在地下層很方便
3. 提醒：不要花太多時間，預留10-15分鐘前往月台"""
        
        else:  # long (57-66分鐘)
            prompt = f"""{base_info}
轉乘時間：約{transfer_time}分鐘

轉乘時間充裕。請用繁體中文提供簡潔建議（100字內）：
1. 1月花蓮東北季風強，天氣涼，建議穿著保暖
2. 轉乘時間充裕（約{transfer_time}分鐘），可以在台北車站地下街悠閒地吃個早餐或逛逛商店。高鐵和台鐵月台都在地下層，在地下街活動最方便，不用跑到地面樓層
3. 建議提前10-20分鐘前往台鐵月台即可"""
        
        request_data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300
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

