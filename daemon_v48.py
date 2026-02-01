import requests
import json
import time
import hashlib
import sys
import base64
from datetime import datetime, timedelta
import pytz

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
REMOTE_PATH = "/www/wwwroot/hsapi.xyz/index.html"

# Whitelist: Only these codes are allowed
ALLOWED_LEAGUES = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']

# Mapping for Buttons
LEAGUE_CONFIG = [
    {'code': 'PL', 'name': '英超', 'color': '#3b82f6'},
    {'code': 'PD', 'name': '西甲', 'color': '#f59e0b'},
    {'code': 'SA', 'name': '意甲', 'color': '#0ea5e9'},
    {'code': 'BL1', 'name': '德甲', 'color': '#ef4444'},
    {'code': 'FL1', 'name': '法甲', 'color': '#8b5cf6'},
    {'code': 'CL', 'name': '歐冠', 'color': '#e2e8f0'}
]

# I18N Status
I18N_STATUS = {
    "IN_PLAY": "進行中", "PAUSED": "暫停", "HT": "中場", "FT": "完賽",
    "FINISHED": "完賽", "SCHEDULED": "未開賽", "TIMED": "未開賽",
    "POSTPONED": "推遲", "CANCELLED": "取消", "SUSPENDED": "中斷"
}

DATA_CACHE = {"standings": {}, "last_slow": 0}

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
        requests.post(url, data=payload, timeout=10)
    except: pass

def fetch_slow():
    standings = {}
    # Only fetch allowed leagues
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = requests.get(f"{BASE_URL}/competitions/{code}/standings", headers=HEADERS, timeout=5)
            if r.status_code == 200:
                table = []
                for row in r.json()['standings'][0]['table'][:15]:
                    table.append({
                        "pos": row['position'],
                        "team": row['team']['name'],
                        "played": row['playedGames'],
                        "points": row['points'],
                        "crest": row['team']['crest']
                    })
                standings[code] = table
                time.sleep(0.5)
        except: pass
    DATA_CACHE['standings'] = standings
    DATA_CACHE['last_slow'] = time.time()

def generate_and_push():
    # Force skip standings for now to debug match display
    # if not DATA_CACHE['standings'] or time.time() - DATA_CACHE['last_slow'] > 1800:
    #    fetch_slow()

    print("Fetching Matches...")
    live = []
    upcoming = []
    
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        matches = r.json().get('matches', [])
        matches.sort(key=lambda x: x['utcDate'])
        
        for m in matches:
            lg_code = m['competition']['code']
            
            # STRICT FILTER: Discard if not in Top 5 + CL
            if lg_code not in ALLOWED_LEAGUES:
                continue
                
            status = m['status']
            lg_name = next((l['name'] for l in LEAGUE_CONFIG if l['code'] == lg_code), m['competition']['name'])
            
            # Time (Beijing)
            utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(TAIPEI_TZ)
            time_display = local_dt.strftime('%H:%M')
            date_display = local_dt.strftime('%m/%d')
            
            # Status
            status_display = I18N_STATUS.get(status, status)
            if 'minute' in m: status_display = f"{m['minute']}'"

            item = {
                "id": m['id'],
                "league": lg_name,
                "code": lg_code,
                "home": m['homeTeam']['shortName'] or m['homeTeam']['name'],
                "away": m['awayTeam']['shortName'] or m['awayTeam']['name'],
                "homeLogo": m['homeTeam']['crest'],
                "awayLogo": m['awayTeam']['crest'],
                "score": f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
                "status": status_display,
                "time": time_display,
                "date": date_display
            }
            
            if status in ['IN_PLAY', 'PAUSED', 'HT']:
                live.append(item)
            elif status in ['TIMED', 'SCHEDULED']:
                upcoming.append(item)
                
    except Exception as e:
        print(f"Fetch Error: {e}")

    # Generate Filters HTML
    filter_html = '<button class="filter-btn active" onclick="filter(this, \'ALL\')">全部</button>'
    for lg in LEAGUE_CONFIG:
        filter_html += f'<button class="filter-btn" onclick="filter(this, \'{lg["code"]}\')">{lg["name"]}</button>'

    # Standings HTML
    standings_html = ""
    for lg, tbl in DATA_CACHE['standings'].items():
        rows = "".join([f"<tr><td>{t['pos']}</td><td style='text-align:left; display:flex; align-items:center;'><img src='{t['crest']}' style='width:20px; margin-right:5px;'> {t['team']}</td><td>{t['played']}</td><td><strong>{t['points']}</strong></td></tr>" for t in tbl])
        display = "block" if lg == "PL" else "none"
        standings_html += f"<div class='standings-table' id='st-{lg}' style='display:{display};'><table><thead><tr><th style='width:10%'>#</th><th style='text-align:left'>球隊</th><th style='width:15%'>賽</th><th style='width:15%'>分</th></tr></thead><tbody>{rows}</tbody></table></div>"

    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M')

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO</title>
<style>
    :root {{ --bg: #05070a; --card: #0f172a; --text: #e2e8f0; --accent: #22c55e; --border: #1e293b; }}
    body {{ background:var(--bg); color:var(--text); font-family:-apple-system, BlinkMacSystemFont, sans-serif; margin:0; padding-bottom:50px; }}
    
    .nav {{ background:var(--card); padding:15px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); position:sticky; top:0; z-index:100; }}
    .container {{ max-width:1000px; margin:0 auto; padding:15px; }}
    
    .filter-bar {{ overflow-x:auto; white-space:nowrap; padding-bottom:10px; margin-bottom:15px; display:flex; gap:8px; }}
    .filter-btn {{ background:var(--card); border:1px solid #334155; color:#94a3b8; padding:6px 16px; border-radius:20px; font-size:14px; cursor:pointer; transition:0.2s; min-width:60px; }}
    .filter-btn.active {{ background:var(--accent); color:#000; border-color:var(--accent); font-weight:bold; }}
    
    .grid {{ display:grid; grid-template-columns:1fr; gap:12px; }}
    @media (min-width: 768px) {{ .grid {{ grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }} }}
    
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:15px; position:relative; }}
    .live-border {{ border:1px solid var(--accent); }}
    
    .header {{ display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-bottom:12px; }}
    .time-badge {{ background:#1e293b; padding:2px 8px; border-radius:4px; color:#fff; }}
    
    .match {{ display:flex; align-items:center; justify-content:space-between; }}
    .team {{ display:flex; align-items:center; gap:10px; font-size:15px; font-weight:500; width:40%; }}
    .team.away {{ justify-content:flex-end; }}
    .team img {{ width:30px; height:30px; object-fit:contain; }}
    
    .score {{ font-size:24px; font-weight:bold; color:var(--accent); min-width:60px; text-align:center; }}
    
    .standings-table table {{ width:100%; border-collapse:collapse; background:var(--card); border-radius:12px; overflow:hidden; }}
    .standings-table th, .standings-table td {{ padding:12px; border-bottom:1px solid var(--border); text-align:center; font-size:14px; }}
    
    .section-head {{ margin:30px 0 15px 0; color:var(--accent); font-weight:bold; font-size:18px; }}
</style>
</head>
<body>

<div class="nav">
    <div style="font-size:20px; font-weight:900;">CSL<span style="color:var(--accent)">PRO</span></div>
    <div style="font-size:12px; color:#94a3b8;">{now_str}</div>
</div>

<div class="container">

    <!-- LIVE -->
    <div class="section-head">正在進行 (Live)</div>
    <div class="filter-bar" id="live-filters">{filter_html}</div>
    <div class="grid" id="live-grid">
        {''.join([f'''
        <div class="card live-border" data-league="{m['code']}">
            <div class="header">
                <span>{m['league']}</span>
                <span style="color:var(--accent); font-weight:bold;">{m['status']}</span>
            </div>
            <div class="match">
                <div class="team">{m['home']} <img src="{m['homeLogo']}"></div>
                <div class="score">{m['score']}</div>
                <div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div>
            </div>
        </div>''' for m in live]) or '<div style="text-align:center; padding:30px; color:#64748b; background:var(--card); border-radius:12px;">目前無五大聯賽賽事</div>'}
    </div>

    <!-- STANDINGS -->
    <div class="section-head">積分榜</div>
    <div class="filter-bar">
        {filter_html.replace('filter(this', 'showStandings(this')}
    </div>
    <div id="standings-container">
        {standings_html}
    </div>

    <!-- UPCOMING -->
    <div class="section-head">即將開賽</div>
    <div class="filter-bar" id="upcoming-filters">{filter_html}</div>
    <div class="grid" id="upcoming-grid">
        {''.join([f'''
        <div class="card" data-league="{m['code']}">
            <div class="header">
                <span>{m['league']}</span>
                <span class="time-badge">{m['date']} {m['time']}</span>
            </div>
            <div class="match">
                <div class="team">{m['home']} <img src="{m['homeLogo']}"></div>
                <div class="score" style="font-size:14px; color:#64748b;">VS</div>
                <div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div>
            </div>
        </div>''' for m in upcoming[:30]])}
    </div>

</div>

<script>
    function filter(btn, code) {{
        let container = btn.parentElement.nextElementSibling; // Grid is next sibling
        
        btn.parentElement.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        container.querySelectorAll('.card').forEach(card => {{
            if(code === 'ALL' || card.dataset.league === code) {{
                card.style.display = 'block';
            }} else {{
                card.style.display = 'none';
            }}
        }});
    }}

    function showStandings(btn, code) {{
        btn.parentElement.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        document.querySelectorAll('.standings-table').forEach(t => t.style.display = 'none');
        let target = document.getElementById('st-'+code);
        if(target) target.style.display = 'block';
    }}
</script>
</body>
</html>"""
    
    push_to_server(html)

if __name__ == "__main__":
    generate_and_push()
    while True:
        time.sleep(30)
        generate_and_push()
