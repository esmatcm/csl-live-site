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

# Allowed
ALLOWED = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']
LEAGUE_CONF = [
    {'code': 'PL', 'name': '英超'}, {'code': 'PD', 'name': '西甲'},
    {'code': 'SA', 'name': '意甲'}, {'code': 'BL1', 'name': '德甲'},
    {'code': 'FL1', 'name': '法甲'}, {'code': 'CL', 'name': '歐冠'}
]

# Translation
I18N = {
    "teams": {
        "Manchester City": "曼城", "Liverpool": "利物浦", "Arsenal": "阿森納",
        "Real Madrid": "皇家馬德里", "Barcelona": "巴塞隆納", "Bayern Munich": "拜仁慕尼黑",
        "Inter": "國際米蘭", "Milan": "AC米蘭", "Juventus": "尤文圖斯",
        "Paris Saint-Germain": "巴黎聖日耳門", "Chelsea": "切爾西", "Man United": "曼聯",
        "Tottenham": "熱刺", "Newcastle": "紐卡斯爾", "Aston Villa": "阿斯頓維拉",
        "Leverkusen": "勒沃庫森", "Dortmund": "多特蒙德", "Atletico": "馬德里競技",
        "Napoli": "拿坡里", "Lazio": "拉齊奧", "Roma": "羅馬", "Atalanta": "亞特蘭大",
        "West Ham": "西漢姆聯", "Everton": "艾弗頓", "Wolves": "狼隊",
        "Brighton": "布萊頓", "Fulham": "富勒姆", "Brentford": "布倫特福德",
        "Crystal Palace": "水晶宮", "Nottm Forest": "諾丁漢森林", "Bournemouth": "伯恩茅斯",
        "Luton": "卢顿", "Burnley": "伯恩利", "Sheff Utd": "謝菲爾德聯",
        "Girona": "赫羅納", "Real Sociedad": "皇家社會", "Betis": "貝蒂斯",
        "Athletic": "畢爾包", "Valencia": "瓦倫西亞", "Villarreal": "比利亚雷亚尔",
        "Sevilla": "塞維利亞", "Lyon": "里昂", "Marseille": "馬賽", "Monaco": "摩納哥",
        "Lille": "里爾", "Lens": "朗斯", "Rennes": "雷恩", "Nice": "尼斯"
    },
    "status": {
        "IN_PLAY": "進行中", "PAUSED": "中場", "HT": "半場", "FT": "完賽",
        "SCHEDULED": "未開賽", "TIMED": "未開賽", "POSTPONED": "推遲"
    }
}

def translate(txt, cat='teams'):
    # Exact match
    if txt in I18N[cat]: return I18N[cat][txt]
    # Partial match
    for k, v in I18N[cat].items():
        if k in txt: return v
    return txt

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def push(content):
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': REMOTE_PATH, 'data': content, 'encoding': 'utf-8'}
        requests.post(url, data=payload, timeout=10)
    except: pass

def run():
    print("Fetching...")
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        matches = r.json().get('matches', [])
    except: return

    live, upcoming = [], []
    
    for m in matches:
        code = m['competition']['code']
        if code not in ALLOWED: continue
        
        status = m['status']
        
        # Translate
        home_en = m['homeTeam']['shortName'] or m['homeTeam']['name']
        away_en = m['awayTeam']['shortName'] or m['awayTeam']['name']
        home_zh = translate(home_en)
        away_zh = translate(away_en)
        
        # League Name
        lg_name = next((l['name'] for l in LEAGUE_CONF if l['code'] == code), code)
        
        # Time
        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(TAIPEI_TZ)
        time_str = local_dt.strftime('%H:%M')
        date_str = local_dt.strftime('%m/%d')
        
        # Status
        status_zh = I18N['status'].get(status, status)
        if status == 'IN_PLAY' and 'minute' in m: status_zh = f"{m['minute']}'"

        item = {
            'league': lg_name, 'code': code,
            'home': home_zh, 'away': away_zh,
            'homeLogo': m['homeTeam']['crest'], 'awayLogo': m['awayTeam']['crest'],
            'score': f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
            'status': status_zh, 'time': time_str, 'date': date_str
        }
        
        if status in ['IN_PLAY', 'PAUSED', 'HT']: live.append(item)
        elif status in ['TIMED', 'SCHEDULED']: upcoming.append(item)

    # HTML Generation
    filter_html = '<button class="filter-btn active" onclick="filter(\'ALL\', this)">全部</button>'
    for lg in LEAGUE_CONF:
        filter_html += f'<button class="filter-btn" onclick="filter(\'{lg["code"]}\', this)">{lg["name"]}</button>'

    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M')
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO</title>
<style>
    :root {{ --bg:#05070a; --card:#0f172a; --text:#e2e8f0; --accent:#22c55e; --border:#1e293b; }}
    body {{ background:var(--bg); color:var(--text); font-family:sans-serif; margin:0; padding-bottom:50px; }}
    .nav {{ background:var(--card); padding:15px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; }}
    .container {{ max-width:1000px; margin:0 auto; padding:15px; }}
    
    .filter-bar {{ white-space:nowrap; overflow-x:auto; padding-bottom:10px; margin-bottom:15px; }}
    .filter-btn {{ background:var(--card); border:1px solid #334155; color:#94a3b8; padding:6px 14px; border-radius:20px; margin-right:8px; cursor:pointer; }}
    .filter-btn.active {{ background:var(--accent); color:#000; border-color:var(--accent); font-weight:bold; }}
    
    .grid {{ display:grid; grid-template-columns:1fr; gap:10px; }}
    @media (min-width: 768px) {{ .grid {{ grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }} }}
    
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:15px; }}
    .live-border {{ border:1px solid var(--accent); }}
    
    .header {{ display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-bottom:10px; }}
    .badge {{ background:#1e293b; padding:2px 6px; border-radius:4px; color:#fff; }}
    .badge.live {{ background:var(--accent); color:#000; font-weight:bold; }}
    
    .match {{ display:flex; align-items:center; justify-content:space-between; }}
    .team {{ display:flex; align-items:center; gap:8px; width:40%; font-size:14px; font-weight:500; }}
    .team.away {{ justify-content:flex-end; }}
    .team img {{ width:28px; height:28px; object-fit:contain; }}
    .score {{ font-size:22px; font-weight:bold; color:var(--accent); text-align:center; min-width:60px; }}
</style>
</head>
<body>
<div class="nav">
    <div style="font-weight:900; font-size:18px;">CSL<span style="color:var(--accent)">PRO</span></div>
    <div style="font-size:12px; color:#aaa;">{now_str}</div>
</div>
<div class="container">
    
    <div style="color:var(--accent); font-weight:bold; margin:10px 0;">正在進行 (Live)</div>
    <div class="filter-bar">{filter_html.replace('filter(', 'filterLive(')}</div>
    <div class="grid" id="live-grid">
        {''.join([f'''
        <div class="card live-border" data-lg="{m['code']}">
            <div class="header"><span>{m['league']}</span><span class="badge live">{m['status']}</span></div>
            <div class="match">
                <div class="team">{m['home']} <img src="{m['homeLogo']}"></div>
                <div class="score">{m['score']}</div>
                <div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div>
            </div>
        </div>''' for m in live]) or '<div style="text-align:center; padding:20px; color:#666;">暫無進行中賽事</div>'}
    </div>

    <div style="color:#aaa; font-weight:bold; margin:30px 0 10px 0;">即將開賽</div>
    <div class="filter-bar">{filter_html.replace('filter(', 'filterUp(')}</div>
    <div class="grid" id="up-grid">
        {''.join([f'''
        <div class="card" data-lg="{m['code']}">
            <div class="header"><span>{m['league']}</span><span class="badge">{m['date']} {m['time']}</span></div>
            <div class="match">
                <div class="team">{m['home']} <img src="{m['homeLogo']}"></div>
                <div class="score" style="font-size:14px; color:#666;">VS</div>
                <div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div>
            </div>
        </div>''' for m in upcoming[:40]])}
    </div>

</div>
<script>
function filterLive(code, btn) {{ filter('live-grid', code, btn); }}
function filterUp(code, btn) {{ filter('up-grid', code, btn); }}

function filter(gridId, code, btn) {{
    // UI
    btn.parentNode.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    // Logic
    document.getElementById(gridId).querySelectorAll('.card').forEach(c => {{
        if(code === 'ALL' || c.dataset.lg === code) c.style.display = 'block';
        else c.style.display = 'none';
    }});
}}
</script>
</body>
</html>"""
    push(html)

if __name__ == "__main__":
    run()
    while True:
        time.sleep(30)
        run()
