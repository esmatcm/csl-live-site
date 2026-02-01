import requests
import json
import time
import hashlib
import sys
from datetime import datetime, timedelta
import pytz

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
REMOTE_PATH = "/www/wwwroot/hsapi.xyz/index.html"

# I18N Mappings
I18N = {
    "status": {
        "IN_PLAY": "進行中", "PAUSED": "中場休息", "HT": "半場", "FT": "完賽",
        "FINISHED": "已完賽", "SCHEDULED": "未開賽", "TIMED": "未開賽",
        "POSTPONED": "推遲", "CANCELLED": "取消", "SUSPENDED": "中斷"
    },
    "leagues": {
        "Premier League": "英超", "Primera Division": "西甲", "Serie A": "意甲",
        "Bundesliga": "德甲", "Ligue 1": "法甲", "Championship": "英冠",
        "Primeira Liga": "葡超", "Eredivisie": "荷甲", "UEFA Champions League": "歐冠"
    },
    "teams": {
        "Manchester City FC": "曼城", "Liverpool FC": "利物浦", "Arsenal FC": "阿森納",
        "Real Madrid CF": "皇家馬德里", "FC Barcelona": "巴塞隆納", "FC Bayern München": "拜仁慕尼黑",
        "Inter Milan": "國際米蘭", "Aston Villa FC": "阿斯頓維拉", "Tottenham Hotspur FC": "熱刺",
        "Manchester United FC": "曼聯", "Newcastle United FC": "紐卡斯爾聯", "Chelsea FC": "切爾西"
    }
}

def translate(cat, key):
    res = I18N.get(cat, {}).get(key, key)
    if cat == 'teams' and res == key:
        for en, zh in I18N['teams'].items():
            if en in key: return zh
    return res

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def push_to_server(content):
    print("Pushing...")
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {
            'request_time': now_time, 'request_token': token,
            'path': REMOTE_PATH, 'data': content, 'encoding': 'utf-8'
        }
        res = requests.post(url, data=payload, timeout=15)
        print(f"Push Status: {res.status_code}") 
    except Exception as e:
        print(f"Push Failed: {e}")

def run():
    print("Fetching Matches...")
    live = []
    upcoming = []
    
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        matches = r.json().get('matches', [])
        
        # Sort matches: Live first, then by time
        matches.sort(key=lambda x: x['utcDate'])
        
        for m in matches:
            status = m['status']
            # Format time to Taipei
            utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(TAIPEI_TZ)
            time_str = local_dt.strftime('%m-%d %H:%M')
            
            item = {
                "id": m['id'],
                "league": translate('leagues', m['competition']['name']),
                "home": translate('teams', m['homeTeam']['name']),
                "away": translate('teams', m['awayTeam']['name']),
                "homeLogo": m['homeTeam']['crest'],
                "awayLogo": m['awayTeam']['crest'],
                "score": f"{m['score']['fullTime']['home'] or 0} - {m['score']['fullTime']['away'] or 0}",
                "status": translate('status', status),
                "time": time_str,
                "venue": "Venue Info" 
            }
            
            if status in ['IN_PLAY', 'PAUSED', 'HT']:
                 live.append(item)
            elif status in ['TIMED', 'SCHEDULED']:
                 upcoming.append(item)
            # We ignore FINISHED for now to save space, or keep them separate
            
    except Exception as e:
        print(f"Fetch Error: {e}")
    
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M:%S')
    
    # HTML Template (Responsive Grid)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO Live</title>
<style>
    /* 基礎樣式 (手機優先) */
    body {{ background:#05070a; color:#e2e8f0; font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin:0; padding:0; }}
    .nav {{ background:#0f172a; padding:15px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; position:sticky; top:0; z-index:100; box-shadow: 0 2px 10px rgba(0,0,0,0.3); }}
    
    .container {{ padding: 10px; max-width: 1200px; margin: 0 auto; }}
    
    .card {{ background:#0f172a; margin-bottom:12px; padding:15px; border-radius:12px; border:1px solid #1e293b; transition: transform 0.2s; }}
    .card:hover {{ border-color: #334155; }}
    .live {{ border:1px solid #22c55e; position: relative; }}
    .live::after {{ content: 'LIVE'; position: absolute; top: 10px; right: 10px; background: #22c55e; color: #000; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
    
    .score {{ font-size:24px; font-weight:bold; color:#22c55e; text-align:center; min-width: 80px; }}
    .row {{ display:flex; justify-content:space-between; align-items:center; }}
    .team-col {{ flex: 1; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    .team-logo {{ width: 40px; height: 40px; object-fit: contain; margin-bottom: 5px; }}

    /* Tab Scroll */
    .tab-scroll {{ overflow-x: auto; white-space: nowrap; padding-bottom: 10px; margin-bottom: 10px; -webkit-overflow-scrolling: touch; }}
    .tab-btn {{ background:#1e293b; color:#94a3b8; padding:8px 16px; border-radius:20px; border:1px solid #333; margin-right:8px; cursor: pointer; transition: all 0.3s; }}
    .tab-btn.active {{ background:#22c55e; color: #05070a; font-weight: bold; border-color: #22c55e; }}

    /* PC Responsive */
    @media (min-width: 768px) {{
        #live-container, #upcoming-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
        }}
        .card {{ margin-bottom: 0; }}
        .nav {{ padding: 15px 40px; }}
    }}
</style>
</head>
<body>
<div class="nav">
    <div style="font-size: 20px; font-weight:900; letter-spacing: -1px; color:#fff;">CSL<span style="color:#22c55e;">PRO</span></div>
    <div style="font-size:12px; color:#64748b;">{now_str}</div>
</div>

<div class="container">
    <h3 style="color:#22c55e; margin-top: 0;">正在進行 (Live)</h3>
    <div id="live-container">
        {''.join([f'''
        <div class="card live">
            <div style="font-size:12px; color:#aaa; margin-bottom:5px;">{m['league']} | {m['time']}</div>
            <div class="row">
                <div class="team-col"><img src="{m['homeLogo']}" class="team-logo"><br>{m['home']}</div>
                <div class="score">{m['score']}</div>
                <div class="team-col"><img src="{m['awayLogo']}" class="team-logo"><br>{m['away']}</div>
            </div>
            <div style="text-align:center; font-size:12px; margin-top:5px; color:#666;">{m['status']}</div>
        </div>''' for m in live]) or '<div class="card" style="grid-column: 1/-1; text-align:center; color:#666;">目前暫無即時賽事</div>'}
    </div>

    <h3 style="margin-top: 30px; color: #64748b;">即將開賽</h3>
    <div id="upcoming-container">
        {''.join([f'''
        <div class="card">
            <div style="font-size:12px; color:#64748b; margin-bottom: 8px;">{m['time']} | {m['league']}</div>
            <div class="row">
                <span style="font-weight: bold;">{m['home']}</span>
                <span style="color: #64748b; font-size: 12px; background:#1e293b; padding:2px 8px; border-radius:10px;">VS</span>
                <span style="font-weight: bold;">{m['away']}</span>
            </div>
        </div>''' for m in upcoming[:12]])}
    </div>
</div>

<div style="text-align:center; padding:40px; color:#475569; font-size: 12px;">v45.2 Pro Responsive</div>
</body>
</html>"""

    push_to_server(html)

if __name__ == "__main__":
    run()
