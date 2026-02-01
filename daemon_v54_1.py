import requests
import json
import time
import hashlib
import sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

PATH_INDEX = "/www/wwwroot/hsapi.xyz/index.html"
PATH_FULL = "/www/wwwroot/hsapi.xyz/full.html"
PATH_JSON = "/www/wwwroot/hsapi.xyz/api.json"

ALLOWED = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']
LEAGUE_CONF = [
    {'code': 'PL', 'name': '英超'}, {'code': 'PD', 'name': '西甲'},
    {'code': 'SA', 'name': '意甲'}, {'code': 'BL1', 'name': '德甲'},
    {'code': 'FL1', 'name': '法甲'}, {'code': 'CL', 'name': '歐冠'}
]

# I18N
I18N = {
    "teams": {
        "Man City": "曼城", "Manchester City": "曼城", "Liverpool": "利物浦", "Arsenal": "阿森納",
        "Chelsea": "切爾西", "Man United": "曼聯", "Tottenham": "熱刺", "Newcastle": "紐卡斯爾聯",
        "Aston Villa": "阿斯頓維拉", "West Ham": "西漢姆聯", "Everton": "艾弗頓", "Wolves": "狼隊",
        "Brighton": "布萊頓", "Fulham": "富勒姆", "Brentford": "布倫特福德", "Crystal Palace": "水晶宮",
        "Nottm Forest": "諾丁漢森林", "Bournemouth": "伯恩茅斯", "Luton": "卢顿", "Burnley": "伯恩利",
        "Sheff Utd": "謝菲爾德聯", "Real Madrid": "皇家馬德里", "Barcelona": "巴塞隆納", "Girona": "赫羅納",
        "Atletico": "馬德里競技", "Athletic": "畢爾包", "Real Sociedad": "皇家社會", "Betis": "貝蒂斯",
        "Valencia": "瓦倫西亞", "Villarreal": "比利亚雷亚尔", "Sevilla": "塞維利亞", "Leverkusen": "勒沃庫森",
        "Bayern": "拜仁慕尼黑", "Stuttgart": "斯圖加特", "Dortmund": "多特蒙德", "Leipzig": "萊比錫",
        "Frankfurt": "法蘭克福", "Inter": "國際米蘭", "Milan": "AC米蘭", "Juventus": "尤文圖斯",
        "Bologna": "博洛尼亞", "Roma": "羅馬", "Atalanta": "亞特蘭大", "Napoli": "拿坡里",
        "Lazio": "拉齊奧", "PSG": "巴黎聖日耳門", "Monaco": "摩納哥", "Brest": "布雷斯特",
        "Lille": "里爾", "Nice": "尼斯", "Lens": "朗斯", "Marseille": "馬賽", "Lyon": "里昂",
        "Benfica": "本菲卡", "Sporting CP": "葡萄牙體育", "Porto": "波爾圖", "Ajax": "阿賈克斯",
        "PSV": "PSV埃因霍溫", "Feyenoord": "費耶諾德", "Galatasaray": "加拉塔薩雷", "Fenerbahce": "費內巴切"
    },
    "status": {
        "IN_PLAY": "進行中", "PAUSED": "中場", "HT": "半場", "FT": "完賽",
        "SCHEDULED": "未開賽", "TIMED": "未開賽", "POSTPONED": "推遲"
    }
}

DATA_CACHE = {"standings": {}, "last_slow": 0}

def translate(txt):
    if not txt: return ""
    if txt in I18N["teams"]: return I18N["teams"][txt]
    for k, v in I18N["teams"].items():
        if k in txt: return v
    return txt

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def push(content, path):
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': path, 'data': content, 'encoding': 'utf-8'}
        requests.post(url, data=payload, timeout=10)
    except: pass

def fetch_slow():
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = requests.get(f"{BASE_URL}/competitions/{code}/standings", headers=HEADERS, timeout=5)
            if r.status_code == 200:
                table = []
                for row in r.json()['standings'][0]['table'][:15]:
                    table.append({
                        "pos": row['position'],
                        "team": translate(row['team']['shortName'] or row['team']['name']),
                        "played": row['playedGames'],
                        "points": row['points'],
                        "crest": row['team']['crest']
                    })
                DATA_CACHE['standings'][code] = table
                time.sleep(0.5)
        except: pass
    DATA_CACHE['last_slow'] = time.time()

def run():
    if not DATA_CACHE['standings'] or time.time() - DATA_CACHE['last_slow'] > 3600:
        fetch_slow()

    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        matches = r.json().get('matches', [])
    except: return

    live_main, upcoming_main = [], []
    live_all, upcoming_all = [], []
    json_data = []
    matches_js_main = {}
    
    for m in matches:
        code = m['competition']['code']
        status = m['status']
        lg_name = next((l['name'] for l in LEAGUE_CONF if l['code'] == code), m['competition']['name'])
        
        # TIME v54.1: UTC+8 (Beijing)
        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        bj_dt = utc_dt + timedelta(hours=8) 
        time_str = bj_dt.strftime('%H:%M')
        date_str = bj_dt.strftime('%m/%d')
        
        status_zh = I18N['status'].get(status, status)
        minute = ""
        if status == 'IN_PLAY':
            minute = f"{m.get('minute', 'Live')}'"
            status_zh = "進行中"

        home_zh = translate(m['homeTeam']['shortName'] or m['homeTeam']['name'])
        away_zh = translate(m['awayTeam']['shortName'] or m['awayTeam']['name'])

        item = {
            'id': m['id'], 'league': lg_name, 'code': code,
            'home': home_zh, 'away': away_zh,
            'homeLogo': m['homeTeam']['crest'], 'awayLogo': m['awayTeam']['crest'],
            'score': f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
            'status': status_zh, 'minute': minute,
            'time': time_str, 'date': date_str
        }
        
        json_data.append(item)
        
        if status in ['IN_PLAY', 'PAUSED', 'HT']: live_all.append(item)
        elif status in ['TIMED', 'SCHEDULED']: upcoming_all.append(item)
        
        if code in ALLOWED:
            matches_js_main[m['id']] = item
            if status in ['IN_PLAY', 'PAUSED', 'HT']: live_main.append(item)
            elif status in ['TIMED', 'SCHEDULED']: upcoming_main.append(item)

    push(json.dumps(json_data, ensure_ascii=False), PATH_JSON)

    filter_html = '<button class="filter-btn active" onclick="filter(\'ALL\', this)">全部</button>'
    for lg in LEAGUE_CONF:
        filter_html += f'<button class="filter-btn" onclick="filter(\'{lg["code"]}\', this)">{lg["name"]}</button>'

    std_tabs, std_content = "", ""
    first = True
    for code, table in DATA_CACHE['standings'].items():
        active, display = ('active', 'block') if first else ('', 'none')
        lg_name = next((l['name'] for l in LEAGUE_CONF if l['code'] == code), code)
        std_tabs += f'<button class="tab-btn {active}" onclick="showTab(\'{code}\', this)">{lg_name}</button>'
        rows = "".join([f"<tr><td>{t['pos']}</td><td style='text-align:left; display:flex; align-items:center;'><img src='{t['crest']}' style='width:20px; margin-right:5px;'> {t['team']}</td><td>{t['played']}</td><td><strong>{t['points']}</strong></td></tr>" for t in table])
        std_content += f"<div id='tab-{code}' class='tab-content' style='display:{display};'><table><thead><tr><th style='width:10%'>#</th><th style='text-align:left'>球隊</th><th style='width:15%'>賽</th><th style='width:15%'>分</th></tr></thead><tbody>{rows}</tbody></table></div>"
        first = False

    now_str = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y/%m/%d %H:%M')
    
    def make_html(live_list, up_list, js_data, filters, show_standings=True, title_suffix=""):
        # LAYOUT: Live -> Upcoming -> Standings
        
        standings_block = ""
        if show_standings:
            standings_block = f'''
            <div style="color:#aaa; font-weight:bold; margin:40px 0 10px 0;">積分榜</div>
            <div class="tab-bar">{std_tabs}</div>
            {std_content}'''
            
        return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>CSL PRO {title_suffix}</title><style>:root {{ --bg:#05070a; --card:#0f172a; --text:#e2e8f0; --accent:#22c55e; --border:#1e293b; }} body {{ background:var(--bg); color:var(--text); font-family:sans-serif; margin:0; padding-bottom:50px; }} .nav {{ background:var(--card); padding:15px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; position:sticky; top:0; z-index:100; }} .container {{ max-width:1000px; margin:0 auto; padding:15px; }} .filter-bar {{ white-space:nowrap; overflow-x:auto; padding-bottom:10px; margin-bottom:15px; }} .filter-btn {{ background:var(--card); border:1px solid #334155; color:#94a3b8; padding:6px 14px; border-radius:20px; margin-right:8px; cursor:pointer; }} .filter-btn.active {{ background:var(--accent); color:#000; border-color:var(--accent); font-weight:bold; }} .grid {{ display:grid; grid-template-columns:1fr; gap:10px; }} @media (min-width: 768px) {{ .grid {{ grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }} }} .card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:15px; cursor:pointer; }} .live-border {{ border:1px solid var(--accent); }} .header {{ display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-bottom:10px; }} .badge {{ background:#1e293b; padding:2px 6px; border-radius:4px; color:#fff; }} .badge.live {{ background:var(--accent); color:#000; font-weight:bold; }} .match {{ display:flex; align-items:center; justify-content:space-between; }} .team {{ display:flex; align-items:center; gap:8px; width:40%; font-size:14px; font-weight:500; }} .team.away {{ justify-content:flex-end; }} .team img {{ width:28px; height:28px; object-fit:contain; }} .score {{ font-size:22px; font-weight:bold; color:var(--accent); text-align:center; min-width:60px; }} .tab-bar {{ margin-bottom:10px; overflow-x:auto; white-space:nowrap; }} .tab-btn {{ background:transparent; border:none; color:#94a3b8; padding:8px 15px; cursor:pointer; font-size:14px; }} .tab-btn.active {{ color:var(--accent); border-bottom:2px solid var(--accent); font-weight:bold; }} .tab-content table {{ width:100%; border-collapse:collapse; background:var(--card); border-radius:12px; overflow:hidden; }} .tab-content th, .tab-content td {{ padding:10px; border-bottom:1px solid var(--border); text-align:center; font-size:14px; }} .modal {{ display:none; position:fixed; z-index:999; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); }} .modal-box {{ background:var(--card); width:90%; max-width:400px; margin:20vh auto; padding:20px; border-radius:12px; border:1px solid var(--accent); text-align:center; }}</style></head><body><div class="nav"><div style="font-weight:900; font-size:18px;">CSL<span style="color:var(--accent)">PRO</span> {title_suffix}</div><div style="font-size:12px; color:#aaa;">{now_str}</div></div><div class="container"><div style="color:var(--accent); font-weight:bold; margin:10px 0;">正在進行 (Live)</div><div class="filter-bar">{filters.replace('filter(', 'filterLive(')}</div><div class="grid" id="live-grid">{''.join([f'''<div class="card live-border" data-lg="{m['code']}" onclick="openModal({m['id']})"><div class="header"><span>{m['league']}</span><span><span class="badge" style="margin-right:5px;">{m['time']}</span><span class="badge live">{m['minute'] or m['status']}</span></span></div><div class="match"><div class="team">{m['home']} <img src="{m['homeLogo']}"></div><div class="score">{m['score']}</div><div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div></div></div>''' for m in live_list]) or '<div style="text-align:center; padding:20px; color:#666;">暫無賽事</div>'}</div><div style="color:#aaa; font-weight:bold; margin:30px 0 10px 0;">即將開賽</div><div class="filter-bar">{filters.replace('filter(', 'filterUp(')}</div><div class="grid" id="up-grid">{''.join([f'''<div class="card" data-lg="{m['code']}"><div class="header"><span>{m['league']}</span><span class="badge">{m['date']} {m['time']}</span></div><div class="match"><div class="team">{m['home']} <img src="{m['homeLogo']}"></div><div class="score" style="font-size:14px; color:#666;">VS</div><div class="team away"><img src="{m['awayLogo']}"> {m['away']}</div></div></div>''' for m in up_list])}</div>{standings_block}</div><div id="modal" class="modal" onclick="closeModal(event)"><div class="modal-box" id="modal-content"></div></div><script>const MATCHES = {json.dumps(js_data, ensure_ascii=False)};function openModal(id) {{ const m = MATCHES[id]; if(!m) return; document.getElementById('modal-content').innerHTML = `<h3 style="color:#22c55e">${{m.league}}</h3><p>${{m.status}} | ${{m.time}}</p><div style="display:flex; justify-content:space-around; align-items:center; margin:20px 0;"><div><img src="${{m.homeLogo}}" width="50"><br>${{m.home}}</div><div style="font-size:30px; font-weight:bold;">${{m.score}}</div><div><img src="${{m.awayLogo}}" width="50"><br>${{m.away}}</div></div><button onclick="closeModal({{target:{{id:'modal'}} }})" style="background:#333; color:#fff; border:none; padding:10px 20px; border-radius:5px;">關閉</button>`; document.getElementById('modal').style.display = 'block'; }} function closeModal(e) {{ if(e.target.id === 'modal') document.getElementById('modal').style.display = 'none'; }} function filterLive(code, btn) {{ filter('live-grid', code, btn); }} function filterUp(code, btn) {{ filter('up-grid', code, btn); }} function filter(gridId, code, btn) {{ btn.parentNode.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active')); btn.classList.add('active'); document.getElementById(gridId).querySelectorAll('.card').forEach(c => {{ c.style.display = (code === 'ALL' || c.dataset.lg === code) ? 'block' : 'none'; }}); }} function showTab(code, btn) {{ document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active')); btn.classList.add('active'); document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none'); document.getElementById('tab-'+code).style.display = 'block'; }}</script></body></html>"""

    push(make_html(live_main, upcoming_main, matches_js_main, filter_html, True), PATH_INDEX)
    push(make_html(live_all, upcoming_all, matches_js_main, "", False, "(FULL)"), PATH_FULL)

if __name__ == "__main__":
    run()
    while True:
        time.sleep(30)
        run()
