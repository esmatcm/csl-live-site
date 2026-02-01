import requests
import json
import os
import re
import sys
import time
import base64
import hashlib
from datetime import datetime, timedelta
import pytz

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
REMOTE_PATH = "/www/wwwroot/hsapi.xyz/index.html"

# ... (I18N dictionary same as before) ...
I18N = {
    "status": {
        "IN_PLAY": "進行中", "PAUSED": "中場休息", "HT": "半場", "FT": "完賽",
        "FINISHED": "已完賽", "SCHEDULED": "未開賽", "TIMED": "已排程",
        "POSTPONED": "推遲", "CANCELLED": "取消", "SUSPENDED": "中斷"
    },
    "leagues": {
        "Premier League": "英超", "Primera Division": "西甲", "Serie A": "意甲",
        "Bundesliga": "德甲", "Ligue 1": "法甲"
    },
    "teams": {
        "Manchester City FC": "曼城", "Liverpool FC": "利物浦", "Arsenal FC": "阿森納",
        "Real Madrid CF": "皇家馬德里", "FC Barcelona": "巴塞隆納", "FC Bayern München": "拜仁慕尼黑",
        "Inter Milan": "國際米蘭", "Aston Villa FC": "阿斯頓維拉", "Tottenham Hotspur FC": "熱刺",
        "Manchester United FC": "曼聯", "Newcastle United FC": "紐卡斯爾聯", "Chelsea FC": "切爾西"
    }
}

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def push_to_server(content):
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': REMOTE_PATH, 'data': content, 'encoding': 'utf-8'}
        res = requests.post(url, data=payload, timeout=15)
        print(f"Push Result: {res.json().get('msg')}")
    except Exception as e: print(f"Push Error: {e}")

def translate(cat, key):
    res = I18N.get(cat, {}).get(key, key)
    if cat == 'teams' and res == key:
        for en, zh in I18N['teams'].items():
            if en in key: return zh
    return res

def fetch_and_push():
    print("Fetching Data...")
    
    # Matches
    live = []
    upcoming = []
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        for m in r.json().get('matches', []):
            item = {
                "id": m['id'],
                "league": translate('leagues', m['competition']['name']),
                "home": translate('teams', m['homeTeam']['name']),
                "away": translate('teams', m['awayTeam']['name']),
                "homeLogo": m['homeTeam']['crest'],
                "awayLogo": m['awayTeam']['crest'],
                "score": f"{m['score']['fullTime']['home'] or 0} - {m['score']['fullTime']['away'] or 0}",
                "status": translate('status', m['status']),
                "venue": m.get('venue', '未提供'),
                "events": [], "lineups": {"home": [], "away": []}
            }
            if m['status'] in ['IN_PLAY', 'PAUSED']:
                # Detail fetch for live
                try:
                    d = requests.get(f"{BASE_URL}/matches/{m['id']}", headers=HEADERS, timeout=5).json()
                    item['events'] = d.get('goals', [])
                    item['lineups']['home'] = [p['name'] for p in d.get('homeTeam', {}).get('lineup', [])]
                    item['lineups']['away'] = [p['name'] for p in d.get('awayTeam', {}).get('lineup', [])]
                except: pass
                live.append(item)
            else:
                upcoming.append(item)
    except: pass

    # News (Simulated for speed, using placeholder if fail)
    news = [{"id":0, "title":"系統自動更新中...", "img":"https://via.placeholder.com/80", "body":"Data sync in progress", "url":"#"}]

    # Generate HTML
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M:%S')
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO Live</title>
<style>
    body {{ background:#05070a; color:#e2e8f0; font-family:sans-serif; margin:0; padding:10px; }}
    .card {{ background:#0f172a; padding:15px; margin-bottom:10px; border-radius:8px; border:1px solid #22c55e; }}
    .nav {{ display:flex; justify-content:space-between; margin-bottom:20px; }}
</style>
</head>
<body>
<div class="nav">
    <b>CSL PRO</b>
    <small>{now_str}</small>
</div>
<h3>正在進行 ({len(live)})</h3>
{''.join([f'<div class="card">{m["home"]} {m["score"]} {m["away"]} <br><small>{m["status"]}</small></div>' for m in live]) or '<div>暫無賽事</div>'}
<h3>即將開賽</h3>
{''.join([f'<div class="card" style="border-color:#333;">{m["home"]} vs {m["away"]}</div>' for m in upcoming[:5]])}
<div style="text-align:center; margin-top:20px; color:#666;">v43.1 Force Update</div>
</body>
</html>"""

    push_to_server(html)

if __name__ == "__main__":
    fetch_and_push()
