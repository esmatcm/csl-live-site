import requests
import json
import time
import hashlib
import sys
from datetime import datetime
import pytz

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
REMOTE_PATH = "/www/wwwroot/hsapi.xyz/index.html"

# Strict Filter
ALLOWED_LEAGUES = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']
LEAGUE_MAP = {'PL': '英超', 'PD': '西甲', 'SA': '意甲', 'BL1': '德甲', 'FL1': '法甲', 'CL': '歐冠'}

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def push(content):
    print("Pushing...")
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': REMOTE_PATH, 'data': content, 'encoding': 'utf-8'}
        r = requests.post(url, data=payload, timeout=10)
        print(f"Push Status: {r.status_code}")
    except Exception as e:
        print(f"Push Error: {e}")

def run():
    print("Fetching...")
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        matches = r.json().get('matches', [])
    except Exception as e:
        print(f"Fetch Error: {e}")
        return

    live = []
    upcoming = []
    
    for m in matches:
        code = m['competition']['code']
        if code not in ALLOWED_LEAGUES: continue
        
        # Data Prep
        status = m['status']
        home = m['homeTeam']['shortName'] or m['homeTeam']['name']
        away = m['awayTeam']['shortName'] or m['awayTeam']['name']
        score = f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}"
        
        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(TAIPEI_TZ)
        time_str = local_dt.strftime('%H:%M')
        date_str = local_dt.strftime('%m/%d')
        
        item = {
            'league': LEAGUE_MAP.get(code, code),
            'code': code,
            'home': home, 'away': away, 'score': score,
            'status': f"{m.get('minute', 'Live')}'" if status == 'IN_PLAY' else status,
            'time': time_str, 'date': date_str,
            'homeLogo': m['homeTeam']['crest'],
            'awayLogo': m['awayTeam']['crest']
        }
        
        if status in ['IN_PLAY', 'PAUSED', 'HT']:
            live.append(item)
        elif status in ['TIMED', 'SCHEDULED']:
            upcoming.append(item)

    print(f"Live: {len(live)}, Upcoming: {len(upcoming)}")

    # HTML
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M')
    
    # CSS & HTML Structure (Same as v48 but simplified)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO</title>
<style>
    :root {{ --bg: #05070a; --card: #0f172a; --text: #e2e8f0; --accent: #22c55e; --border: #1e293b; }}
    body {{ background:var(--bg); color:var(--text); font-family:sans-serif; margin:0; padding-bottom:50px; }}
    .nav {{ background:var(--card); padding:15px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); }}
    .container {{ max-width:800px; margin:0 auto; padding:15px; }}
    
    .filter-btn {{ background:transparent; border:1px solid #333; color:#aaa; padding:5px 10px; border-radius:15px; margin-right:5px; cursor:pointer; }}
    .filter-btn.active {{ background:var(--accent); color:#000; border-color:var(--accent); font-weight:bold; }}
    
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:15px; margin-bottom:10px; }}
    .row {{ display:flex; justify-content:space-between; align-items:center; }}
    .team {{ display:flex; align-items:center; gap:10px; width:40%; font-size:14px; }}
    .team.away {{ justify-content:flex-end; }}
    .team img {{ width:24px; height:24px; object-fit:contain; }}
    .score {{ font-size:20px; font-weight:bold; color:var(--accent); text-align:center; width:20%; }}
    
    .live-tag {{ color:var(--accent); font-weight:bold; font-size:12px; }}
</style>
</head>
<body>
<div class="nav">
    <div style="font-size:20px; font-weight:900;">CSL<span style="color:var(--accent)">PRO</span></div>
    <div style="font-size:12px; color:#aaa;">{now_str}</div>
</div>
<div class="container">
    <h3 style="color:var(--accent)">正在進行</h3>
    <div id="live-list">
        {''.join([f'''<div class="card"><div class="row" style="font-size:12px; color:#aaa; margin-bottom:10px;"><span>{m['league']}</span><span class="live-tag">{m['status']}</span></div><div class="row"><div class="team">{m['home']} <img src="{m['homeLogo']}"></div><div class="score">{m['score']}</div><div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div></div></div>''' for m in live]) or '<div style="text-align:center; padding:20px; color:#666;">無進行中賽事</div>'}
    </div>
    
    <h3 style="color:#aaa; margin-top:30px;">即將開賽</h3>
    <div id="upcoming-list">
        {''.join([f'''<div class="card"><div class="row" style="font-size:12px; color:#aaa; margin-bottom:10px;"><span>{m['league']}</span><span>{m['date']} {m['time']}</span></div><div class="row"><div class="team">{m['home']} <img src="{m['homeLogo']}"></div><div class="score" style="font-size:14px; color:#666;">VS</div><div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div></div></div>''' for m in upcoming[:30]])}
    </div>
</div>
</body></html>"""
    
    push(html)

if __name__ == "__main__":
    run()
