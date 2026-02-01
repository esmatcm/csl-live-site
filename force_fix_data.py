import json
import requests
import hashlib
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
PATH_DATA = "/www/wwwroot/hsapi.xyz/data.json"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def force_push():
    print("Forcing Data Restore...")
    
    # Minimal Valid Data Structure to unblock UI
    mock_data = {
        "standings": {},
        "matches": [{
            "id": 999999,
            "league": {"en": "System", "tc": "系統", "sc": "系统"},
            "code": "PL",
            "home": {"en": "System Restore", "tc": "系統恢復中", "sc": "系统恢复中"},
            "away": {"en": "Please Wait", "tc": "請稍候", "sc": "请稍候"},
            "homeLogo": "https://via.placeholder.com/50",
            "awayLogo": "https://via.placeholder.com/50",
            "score": "0-0",
            "status": {"en": "LIVE", "tc": "進行中", "sc": "进行中"},
            "statusRaw": "IN_PLAY",
            "time": "NOW",
            "date": "02/01",
            "events": [],
            "streams": []
        }]
    }
    
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
