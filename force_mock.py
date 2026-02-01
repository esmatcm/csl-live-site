import json
import requests
import time
import hashlib
import sys

sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
PATH_DATA = "/www/wwwroot/hsapi.xyz/data_v60.json"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def force_push():
    print("Forcing Mock Data...")
    
    mock_data = [{
        "id": 888888,
        "league": {"en": "TEST LEAGUE", "tc": "測試聯賽", "sc": "测试联赛"},
        "home": {"en": "Man City", "tc": "曼城", "sc": "曼城"},
        "away": {"en": "Liverpool", "tc": "利物浦", "sc": "利物浦"},
        "homeLogo": "https://crests.football-data.org/65.png",
        "awayLogo": "https://crests.football-data.org/64.png",
        "score": "3-3",
        "status": {"en": "LIVE", "tc": "進行中", "sc": "进行中"},
        "statusRaw": "IN_PLAY",
        "time": "NOW",
        "date": "02/01",
        "events": [
            {"minute": 90, "type": "goal", "text": {"en": "Goal: Foden", "tc": "進球: 福登", "sc": "进球: 福登"}},
            {"minute": 12, "type": "card", "card": "red", "text": {"en": "Red: Klopp", "tc": "紅牌: 克洛普", "sc": "红牌: 克洛普"}}
        ],
        "lineups": {
            "home": ["Ederson", "Walker"], 
            "away": ["Alisson", "Salah"],
            "bench_home": ["Ortega"],
            "bench_away": ["Kelleher"]
        },
        "referees": ["Test Ref"],
        "coach": {"home": "Pep", "away": "Klopp"}
    }]
    
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': PATH_DATA, 'data': json.dumps(mock_data), 'encoding': 'utf-8'}
        r = requests.post(url, data=payload, timeout=10)
        print(f"Status: {r.status_code}, Res: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    force_push()
