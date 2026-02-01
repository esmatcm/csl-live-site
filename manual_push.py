import requests
import json
import time
import base64
import hashlib
from datetime import datetime
import pytz

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
REMOTE_PATH = "/www/wwwroot/hsapi.xyz/index.html"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def push_to_server(content):
    print("Pushing to server...")
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
    payload = {
        'request_time': now_time, 'request_token': token,
        'path': REMOTE_PATH, 'data': content, 'encoding': 'utf-8'
    }
    requests.post(url, data=payload, timeout=10)
    print("Push Done.")

def run_manual():
    print("Fetching Data...")
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        data = r.json()
    except: data = {}
    
    live = []
    upcoming = []
    if 'matches' in data:
        for m in data['matches']:
            if m['status'] in ['IN_PLAY', 'PAUSED']: live.append(m)
            else: upcoming.append(m)
            
    print(f"Live: {len(live)}, Upcoming: {len(upcoming)}")
    
    # Generate Simple HTML for Speed
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>CSL PRO (Manual)</title></head>
<body style="background:#000; color:#fff; padding:20px;">
    <h1>CSL PRO (v42.1 Manual Push)</h1>
    <p>更新時間: {datetime.now(TAIPEI_TZ)}</p>
    <h2>Live ({len(live)})</h2>
    {''.join([f'<div>{m["homeTeam"]["name"]} vs {m["awayTeam"]["name"]}</div>' for m in live]) or '暫無賽事'}
    <h2>Upcoming</h2>
    {''.join([f'<div>{m["utcDate"]} {m["homeTeam"]["name"]} vs {m["awayTeam"]["name"]}</div>' for m in upcoming[:5]])}
</body>
</html>"""

    push_to_server(html)

if __name__ == "__main__":
    run_manual()
