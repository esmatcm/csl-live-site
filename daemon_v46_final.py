import requests
import json
import time
import hashlib
import sys
import base64
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

# Full I18N Dictionary
I18N = {
    "status": {
        "IN_PLAY": "進行中", "PAUSED": "中場休息", "HT": "半場", "FT": "完賽",
        "FINISHED": "已完賽", "SCHEDULED": "未開賽", "TIMED": "未開賽",
        "POSTPONED": "推遲", "CANCELLED": "取消", "SUSPENDED": "中斷", "AWARDED": "裁定"
    },
    "leagues": {
        "Premier League": "英超", "Primera Division": "西甲", "Serie A": "意甲",
        "Bundesliga": "德甲", "Ligue 1": "法甲", "Championship": "英冠",
        "Primeira Liga": "葡超", "Eredivisie": "荷甲", "UEFA Champions League": "歐冠",
        "European Championship": "歐國盃", "Copa Libertadores": "南美解放者盃"
    },
    "league_codes": {
        "PL": "英超", "PD": "西甲", "SA": "意甲", "BL1": "德甲", "FL1": "法甲", "CLC": "歐冠"
    },
    "teams": {
        "Manchester City FC": "曼城", "Liverpool FC": "利物浦", "Arsenal FC": "阿森納",
        "Real Madrid CF": "皇家馬德里", "FC Barcelona": "巴塞隆納", "FC Bayern München": "拜仁慕尼黑",
        "Inter Milan": "國際米蘭", "Aston Villa FC": "阿斯頓維拉", "Tottenham Hotspur FC": "熱刺",
        "Manchester United FC": "曼聯", "Newcastle United FC": "紐卡斯爾聯", "Chelsea FC": "切爾西",
        "Juventus FC": "尤文圖斯", "AC Milan": "AC米蘭", "Bayer 04 Leverkusen": "勒沃庫森",
        "Borussia Dortmund": "多特蒙德", "Paris Saint-Germain FC": "巴黎聖日耳門",
        "Atlético de Madrid": "馬德里競技", "AS Roma": "羅馬", "SS Lazio": "拉齊奧",
        "SSC Napoli": "拿坡里", "Everton FC": "艾弗頓", "West Ham United FC": "西漢姆聯",
        "Crystal Palace FC": "水晶宮", "Wolverhampton Wanderers FC": "狼隊"
    }
}

DATA_CACHE = {"standings": {}, "last_slow": 0}

def translate(cat, key):
    # Direct match
    res = I18N.get(cat, {}).get(key)
    if res: return res
    
    # Partial match for teams (slower but safer)
    if cat == 'teams':
        for en, zh in I18N['teams'].items():
            if en in key: return zh
    # Fallback to key if no translation
    return key

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

def fetch_slow():
    print("Fetching Standings...")
    standings = {}
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = requests.get(f"{BASE_URL}/competitions/{code}/standings", headers=HEADERS, timeout=5)
            if r.status_code == 200:
                table = []
                for row in r.json()['standings'][0]['table'][:15]:
                    table.append({
                        "pos": row['position'], 
                        "team": translate('teams', row['team']['name']),
                        "played": row['playedGames'], 
                        "points": row['points'], 
                        "crest": row['team']['crest']
                    })
                standings[code] = table
                time.sleep(0.5) # Avoid rate limit
        except: pass
    DATA_CACHE['standings'] = standings
    DATA_CACHE['last_slow'] = time.time()

def run_once():
    # 1. Check if we need standings (every 30 mins or if empty)
    if not DATA_CACHE['standings'] or time.time() - DATA_CACHE['last_slow'] > 1800:
        fetch_slow()

    # 2. Fetch Matches
    print("Fetching Matches...")
    live = []
    upcoming = []
    
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        matches = r.json().get('matches', [])
        matches.sort(key=lambda x: x['utcDate'])
        
        for m in matches:
            status = m['status']
            league_code = m['competition']['code']
            
            # Minute simulation (API free tier often lacks 'minute', we use status)
            minute = ""
            if status == 'IN_PLAY':
                # Try to calculate from lastUpdated? Or just show "Live"
                minute = "Live" 
            elif status == 'HT':
                minute = "HT"
            
            # Format time
            utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(TAIPEI_TZ)
            time_str = local_dt.strftime('%m-%d %H:%M')

            item = {
                "id": m['id'],
                "league": translate('leagues', m['competition']['name']),
                "leagueCode": league_code, # For filtering
                "home": translate('teams', m['homeTeam']['name']),
                "away": translate('teams', m['awayTeam']['name']),
                "homeLogo": m['homeTeam']['crest'],
                "awayLogo": m['awayTeam']['crest'],
                "score": f"{m['score']['fullTime']['home'] or 0} - {m['score']['fullTime']['away'] or 0}",
                "status": translate('status', status),
                "time": time_str,
                "minute": minute,
                # Simple lineups/events placeholder for modal
                "events": [], 
                "lineups": {"home": [], "away": []}
            }
            
            if status in ['IN_PLAY', 'PAUSED', 'HT']:
                 live.append(item)
            elif status in ['TIMED', 'SCHEDULED']:
                 upcoming.append(item)
    except Exception as e:
        print(f"Fetch Error: {e}")

    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M:%S')

    # 3. Generate HTML (v46 Final Structure)
    
    # Standings HTML Generator
    standings_html = ""
    for lg, tbl in DATA_CACHE['standings'].items():
        rows = "".join([f"<tr><td>{t['pos']}</td><td style='text-align:left; display:flex; align-items:center;'><img src='{t['crest']}' style='width:20px; margin-right:5px;'> {t['team']}</td><td>{t['played']}</td><td><strong>{t['points']}</strong></td></tr>" for t in tbl])
        display = "block" if lg == "PL" else "none"
        standings_html += f"<div class='standings-table' id='st-{lg}' style='display:{display};'><table><thead><tr><th style='width:10%'>#</th><th style='text-align:left'>球隊</th><th style='width:15%'>賽</th><th style='width:15%'>分</th></tr></thead><tbody>{rows}</tbody></table></div>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO Live</title>
<style>
    /* CSS Variables */
    :root {{ --bg: #05070a; --card-bg: #0f172a; --text: #e2e8f0; --accent: #22c55e; --border: #1e293b; }}
    
    body {{ background:var(--bg); color:var(--text); font-family:-apple-system, BlinkMacSystemFont, sans-serif; margin:0; padding-bottom:40px; }}
    .nav {{ background:var(--card-bg); padding:15px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); position:sticky; top:0; z-index:100; }}
    
    .container {{ padding: 15px; max-width: 1200px; margin: 0 auto; }}
    
    /* Filters */
    .filter-bar {{ overflow-x: auto; white-space: nowrap; margin-bottom: 20px; padding-bottom: 5px; }}
    .filter-btn {{ background:var(--card-bg); color:#94a3b8; border:1px solid var(--border); padding:6px 14px; border-radius:20px; margin-right:8px; font-size:13px; cursor:pointer; transition:0.2s; }}
    .filter-btn.active {{ background:var(--accent); color:#000; border-color:var(--accent); font-weight:bold; }}

    /* Cards */
    .card {{ background:var(--card-bg); border:1px solid var(--border); border-radius:12px; padding:15px; margin-bottom:12px; cursor:pointer; position:relative; }}
    .card:active {{ transform: scale(0.98); }}
    
    .live-card {{ border-color: var(--accent); }}
    .minute-badge {{ position:absolute; top:10px; right:10px; color:var(--accent); font-size:12px; font-weight:bold; animation: pulse 1s infinite; }}
    
    .row {{ display:flex; justify-content:space-between; align-items:center; }}
    .team {{ flex:1; text-align:center; display:flex; flex-direction:column; align-items:center; font-size:14px; }}
    .team img {{ width:36px; height:36px; margin-bottom:4px; object-fit:contain; }}
    .score {{ font-size:24px; font-weight:bold; color:var(--accent); min-width:60px; text-align:center; }}
    
    /* Standings */
    .standings-table table {{ width:100%; border-collapse:collapse; background:var(--card-bg); border-radius:12px; overflow:hidden; }}
    .standings-table th, .standings-table td {{ padding:12px 15px; border-bottom:1px solid var(--border); text-align:center; font-size:14px; }}
    
    /* Modal */
    .modal {{ display:none; position:fixed; z-index:999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); backdrop-filter:blur(3px); }}
    .modal-content {{ background:var(--card-bg); width:100%; height:60%; position:fixed; bottom:0; border-radius:20px 20px 0 0; border-top:1px solid var(--accent); padding:20px; animation: slideUp 0.3s; overflow-y:auto; }}
    
    @keyframes slideUp {{ from {{ bottom:-100%; }} to {{ bottom:0; }} }}
    @keyframes pulse {{ 0% {{ opacity:1; }} 50% {{ opacity:0.5; }} 100% {{ opacity:1; }} }}

    /* PC Responsive */
    @media (min-width: 768px) {{
        #live-grid, #upcoming-grid {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap:15px; }}
        .card {{ margin-bottom:0; transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-3px); border-color:#fff; }}
        
        .modal-content {{ width:400px; height:auto; max-height:80vh; top:50%; left:50%; transform:translate(-50%, -50%); border-radius:12px; bottom:auto; border:1px solid var(--accent); animation: none; }}
        .container {{ padding: 30px; }}
    }}
</style>
</head>
<body>

<div class="nav">
    <div style="font-size:20px; font-weight:900;">CSL<span style="color:var(--accent)">PRO</span></div>
    <div style="font-size:12px; color:#64748b">{now_str}</div>
</div>

<div class="container">
    
    <!-- LIVE -->
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3 style="color:var(--accent);">正在進行</h3>
        <div class="filter-bar">
            <button class="filter-btn active" onclick="filterMatches('ALL', this)">全部</button>
            <button class="filter-btn" onclick="filterMatches('PL', this)">英超</button>
            <button class="filter-btn" onclick="filterMatches('PD', this)">西甲</button>
            <button class="filter-btn" onclick="filterMatches('SA', this)">意甲</button>
            <button class="filter-btn" onclick="filterMatches('BL1', this)">德甲</button>
            <button class="filter-btn" onclick="filterMatches('FL1', this)">法甲</button>
        </div>
    </div>
    
    <div id="live-grid">
        {''.join([f'''
        <div class="card live-card" data-league="{m['leagueCode']}" onclick='openModal({json.dumps(m, ensure_ascii=False)})'>
            <div class="minute-badge">{m['minute']}</div>
            <div style="font-size:12px; color:#94a3b8; margin-bottom:8px;">{m['league']}</div>
            <div class="row">
                <div class="team"><img src="{m['homeLogo']}">{m['home']}</div>
                <div class="score">{m['score']}</div>
                <div class="team"><img src="{m['awayLogo']}">{m['away']}</div>
            </div>
        </div>''' for m in live]) or '<div style="grid-column:1/-1; text-align:center; padding:30px; color:#64748b; background:#0f172a; border-radius:12px;">目前暫無進行中賽事</div>'}
    </div>

    <!-- STANDINGS -->
    <h3 style="margin-top:40px;">積分榜</h3>
    <div class="filter-bar">
        <button class="filter-btn active" onclick="showStandings('PL', this)">英超</button>
        <button class="filter-btn" onclick="showStandings('PD', this)">西甲</button>
        <button class="filter-btn" onclick="showStandings('SA', this)">意甲</button>
        <button class="filter-btn" onclick="showStandings('BL1', this)">德甲</button>
        <button class="filter-btn" onclick="showStandings('FL1', this)">法甲</button>
    </div>
    <div id="standings-container">
        {standings_html}
    </div>

    <!-- UPCOMING -->
    <h3 style="margin-top:40px;">即將開賽</h3>
    <div id="upcoming-grid">
        {''.join([f'''
        <div class="card" data-league="{m['leagueCode']}">
            <div style="font-size:12px; color:#64748b; margin-bottom:8px;">{m['time']} | {m['league']}</div>
            <div class="row">
                <div class="team" style="flex-direction:row; justify-content:flex-end; gap:8px;">{m['home']} <img src="{m['homeLogo']}" style="width:24px; height:24px; margin:0;"></div>
                <div style="font-size:12px; color:#64748b; padding:0 10px;">VS</div>
                <div class="team" style="flex-direction:row; justify-content:flex-start; gap:8px;"><img src="{m['awayLogo']}" style="width:24px; height:24px; margin:0;"> {m['away']}</div>
            </div>
        </div>''' for m in upcoming[:20]])}
    </div>

</div>

<!-- MODAL -->
<div id="matchModal" class="modal" onclick="closeModal(event)">
    <div class="modal-content">
        <div style="text-align:right;"><span onclick="document.getElementById('matchModal').style.display='none'" style="font-size:24px; cursor:pointer;">&times;</span></div>
        <div id="modal-body" style="text-align:center;">
            <!-- Content Injected via JS -->
        </div>
    </div>
</div>

<script>
    function filterMatches(code, btn) {{
        // UI Active State
        btn.parentNode.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Filter Logic
        document.querySelectorAll('#live-grid .card, #upcoming-grid .card').forEach(card => {{
            if(code === 'ALL' || card.dataset.league === code) {{
                card.style.display = 'block';
            }} else {{
                card.style.display = 'none';
            }}
        }});
    }}

    function showStandings(code, btn) {{
        btn.parentNode.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        document.querySelectorAll('.standings-table').forEach(t => t.style.display = 'none');
        document.getElementById('st-'+code).style.display = 'block';
    }}

    function openModal(data) {{
        const modal = document.getElementById('matchModal');
        const body = document.getElementById('modal-body');
        
        body.innerHTML = `
            <h4 style="color:#22c55e; margin:0;">${{data.league}}</h4>
            <div style="font-size:12px; color:#aaa; margin-bottom:20px;">${{data.status}} | ${{data.time}}</div>
            
            <div style="display:flex; justify-content:space-around; align-items:center; margin-bottom:30px;">
                <div><img src="${{data.homeLogo}}" width="60"><br><strong>${{data.home}}</strong></div>
                <div style="font-size:36px; font-weight:bold; color:#22c55e;">${{data.score}}</div>
                <div><img src="${{data.awayLogo}}" width="60"><br><strong>${{data.away}}</strong></div>
            </div>
            
            <div style="background:#1e293b; padding:15px; border-radius:10px; font-size:13px; color:#cbd5e1;">
                比賽詳細數據需升級 API 方案
            </div>
        `;
        modal.style.display = 'block';
    }}
    
    function closeModal(e) {{
        if(e.target.id === 'matchModal') e.target.style.display = 'none';
    }}
</script>

</body>
</html>"""
    push_to_server(html)

if __name__ == "__main__":
    run_once()
