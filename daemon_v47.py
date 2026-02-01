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

# I18N
I18N_STATUS = {
    "IN_PLAY": "進行中", "PAUSED": "暫停", "HT": "中場", "FT": "完賽",
    "FINISHED": "完賽", "SCHEDULED": "未開賽", "TIMED": "未開賽",
    "POSTPONED": "推遲", "CANCELLED": "取消", "SUSPENDED": "中斷", "AWARDED": "裁定"
}
# League Names (Add more as needed, others fallback to English)
I18N_LEAGUES = {
    "Premier League": "英超", "Primera Division": "西甲", "Serie A": "意甲",
    "Bundesliga": "德甲", "Ligue 1": "法甲", "Championship": "英冠",
    "Primeira Liga": "葡超", "Eredivisie": "荷甲", "UEFA Champions League": "歐冠",
    "Serie B": "意乙", "Segunda Division": "西乙"
}
# Map code to short name for buttons
LEAGUE_SHORT_NAMES = {
    "PL": "英超", "PD": "西甲", "SA": "意甲", "BL1": "德甲", "FL1": "法甲",
    "ELC": "英冠", "PPL": "葡超", "DED": "荷甲", "CL": "歐冠",
    "SB": "意乙", "SD": "西乙"
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
        r = requests.post(url, data=payload, timeout=10)
        print(f"Push: {r.status_code}")
    except Exception as e:
        print(f"Push Error: {e}")

def fetch_slow():
    # Only fetch Top 5 standings to save API calls
    standings = {}
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = requests.get(f"{BASE_URL}/competitions/{code}/standings", headers=HEADERS, timeout=5)
            if r.status_code == 200:
                table = []
                for row in r.json()['standings'][0]['table'][:15]:
                    table.append({
                        "pos": row['position'],
                        "team": row['team']['name'], # Translate later or keep en
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
    # 1. Fetch Matches
    print("Fetching...")
    live = []
    upcoming = []
    
    # Track which leagues exist in the data for dynamic buttons
    live_leagues = set()
    upcoming_leagues = set()
    
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        matches = r.json().get('matches', [])
        matches.sort(key=lambda x: x['utcDate'])
        
        for m in matches:
            status = m['status']
            lg_name = m['competition']['name']
            lg_code = m['competition']['code']
            
            # Translate League
            lg_zh = I18N_LEAGUES.get(lg_name, lg_name)
            
            # Time
            utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(TAIPEI_TZ)
            time_display = local_dt.strftime('%H:%M') # Just HH:MM
            date_display = local_dt.strftime('%m/%d')
            
            # Minute Logic
            minute_display = I18N_STATUS.get(status, status)
            # API doesn't standardly give minute in list view, but if it did:
            if 'minute' in m:
                minute_display = f"{m['minute']}'"
            elif status == 'IN_PLAY':
                # Heuristic: if we had start time, we could calc, but half-time breaks mess it up.
                # Default to "進行中" or specific if available
                pass
                
            item = {
                "id": m['id'],
                "league": lg_zh,
                "code": lg_code,
                "home": m['homeTeam']['shortName'] or m['homeTeam']['name'],
                "away": m['awayTeam']['shortName'] or m['awayTeam']['name'],
                "homeLogo": m['homeTeam']['crest'],
                "awayLogo": m['awayTeam']['crest'],
                "score": f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
                "status": minute_display,
                "time": time_display,
                "date": date_display
            }
            
            if status in ['IN_PLAY', 'PAUSED', 'HT']:
                live.append(item)
                live_leagues.add(lg_code)
            elif status in ['TIMED', 'SCHEDULED']:
                upcoming.append(item)
                upcoming_leagues.add(lg_code)
                
    except Exception as e:
        print(f"Fetch Error: {e}")

    # 2. Generate Filter Buttons HTML
    def make_buttons(codes, active_all=True):
        html = f'<button class="filter-btn {"active" if active_all else ""}" onclick="filter(this, \'ALL\')">全部</button>'
        # Sort codes to keep order consistent (Top 5 first)
        priority = ['PL','PD','SA','BL1','FL1','CL']
        sorted_codes = sorted(list(codes), key=lambda x: priority.index(x) if x in priority else 99)
        
        for c in sorted_codes:
            name = LEAGUE_SHORT_NAMES.get(c, c)
            html += f'<button class="filter-btn" onclick="filter(this, \'{c}\')">{name}</button>'
        return html

    live_filters = make_buttons(live_leagues)
    upcoming_filters = make_buttons(upcoming_leagues)

    # 3. Generate HTML
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M')
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO</title>
<style>
    :root {{ --bg: #05070a; --card: #0f172a; --text: #e2e8f0; --accent: #22c55e; --border: #1e293b; }}
    body {{ background:var(--bg); color:var(--text); font-family:sans-serif; margin:0; padding-bottom:50px; }}
    
    /* Nav */
    .nav {{ background:var(--card); padding:15px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); position:sticky; top:0; z-index:100; }}
    .logo {{ font-size:20px; font-weight:900; }}
    
    /* Layout */
    .container {{ max-width:1000px; margin:0 auto; padding:15px; }}
    .section-title {{ color:var(--accent); margin:30px 0 10px 0; font-size:16px; display:flex; justify-content:space-between; align-items:center; }}
    
    /* Filters */
    .filters {{ overflow-x:auto; white-space:nowrap; padding-bottom:10px; margin-bottom:10px; -webkit-overflow-scrolling:touch; }}
    .filter-btn {{ background:transparent; border:1px solid #334155; color:#94a3b8; padding:5px 12px; border-radius:15px; font-size:13px; margin-right:8px; cursor:pointer; transition:0.2s; }}
    .filter-btn.active {{ background:var(--accent); color:#000; border-color:var(--accent); font-weight:bold; }}
    
    /* Cards */
    .grid {{ display:grid; grid-template-columns:1fr; gap:10px; }}
    @media (min-width: 768px) {{ .grid {{ grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }} }}
    
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:15px; position:relative; transition:0.2s; }}
    .card:hover {{ border-color:#475569; transform:translateY(-2px); }}
    .live-border {{ border-color:var(--accent); }}
    
    .card-header {{ display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-bottom:10px; }}
    .time-badge {{ background:#1e293b; padding:2px 6px; border-radius:4px; color:#fff; }}
    
    .match-row {{ display:flex; align-items:center; justify-content:space-between; }}
    .team {{ display:flex; align-items:center; gap:8px; font-size:14px; font-weight:500; width:40%; }}
    .team.away {{ justify-content:flex-end; }}
    .team img {{ width:24px; height:24px; object-fit:contain; }}
    
    .score-box {{ width:20%; text-align:center; }}
    .score {{ font-size:20px; font-weight:bold; color:var(--accent); }}
    .vs {{ font-size:12px; color:#64748b; }}
    
    .status-badge {{ position:absolute; top:15px; left:50%; transform:translateX(-50%); font-size:12px; font-weight:bold; color:var(--accent); }}
    
    /* Modal */
    .modal {{ display:none; position:fixed; z-index:999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); }}
    .modal-box {{ background:var(--card); width:90%; max-width:400px; margin:20vh auto; padding:20px; border-radius:12px; border:1px solid var(--accent); text-align:center; }}
</style>
</head>
<body>

<div class="nav">
    <div class="logo">CSL<span style="color:var(--accent)">PRO</span></div>
    <div style="font-size:12px; color:#94a3b8;">{now_str}</div>
</div>

<div class="container">

    <!-- LIVE SECTION -->
    <div class="section-title">
        <span>正在進行</span>
        <span style="font-size:12px; color:#64748b;">Live</span>
    </div>
    <div class="filters" id="live-filters">{live_filters}</div>
    <div class="grid" id="live-grid">
        {''.join([f'''
        <div class="card live-border" data-league="{m['code']}" onclick="alert('{m['home']} vs {m['away']}')">
            <div class="card-header">
                <span>{m['league']}</span>
                <span class="time-badge" style="background:var(--accent); color:#000;">{m['status']}</span>
            </div>
            <div class="match-row">
                <div class="team">{m['home']} <img src="{m['homeLogo']}"></div>
                <div class="score-box"><div class="score">{m['score']}</div></div>
                <div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div>
            </div>
        </div>''' for m in live]) or '<div style="text-align:center; padding:20px; color:#666;">暫無賽事</div>'}
    </div>

    <!-- UPCOMING SECTION -->
    <div class="section-title">
        <span>即將開賽</span>
        <span style="font-size:12px; color:#64748b;">Upcoming</span>
    </div>
    <div class="filters" id="upcoming-filters">{upcoming_filters}</div>
    <div class="grid" id="upcoming-grid">
        {''.join([f'''
        <div class="card" data-league="{m['code']}">
            <div class="card-header">
                <span>{m['league']}</span>
                <span class="time-badge">{m['date']} {m['time']}</span>
            </div>
            <div class="match-row">
                <div class="team">{m['home']} <img src="{m['homeLogo']}"></div>
                <div class="score-box"><div class="vs">VS</div></div>
                <div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div>
            </div>
        </div>''' for m in upcoming[:30]])}
    </div>

</div>

<div style="text-align:center; font-size:11px; color:#475569; margin-top:30px;">
    v47.0 Auto-Sync • Beijing Time (UTC+8)
</div>

<script>
    function filter(btn, code) {{
        // Find parent container (live or upcoming filters)
        let container = btn.parentElement;
        // Find target grid ID based on filter ID
        let gridId = container.id.replace('filters', 'grid');
        let grid = document.getElementById(gridId);
        
        // Active Class
        container.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Filter Cards
        grid.querySelectorAll('.card').forEach(card => {{
            if(code === 'ALL' || card.dataset.league === code) {{
                card.style.display = 'block'; # Should be block or flex depending on card style, but block works for grid item visibility if not using d-none class
                # Better:
                card.style.display = 'block'; # Reset
            }} else {{
                card.style.display = 'none';
            }}
        }});
    }}
</script>
</body>
</html>"""
    
    push_to_server(html)

if __name__ == "__main__":
    # First run immediately
    generate_and_push()
    # Then loop
    while True:
        time.sleep(30)
        generate_and_push()
