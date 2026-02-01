import requests
import json
import os
import time
import base64
import hashlib
import sys
import traceback
from datetime import datetime, timedelta
import pytz

# 1. 核心修正：強制 UTF-8 輸出，防止 Windows 控制台崩潰
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
REMOTE_PATH = "/www/wwwroot/hsapi.xyz/index.html"

# i18n
I18N = {
    "status": {
        "IN_PLAY": "進行中", "PAUSED": "中場休息", "HT": "半場", "FT": "完賽",
        "FINISHED": "已完賽", "SCHEDULED": "未開賽", "TIMED": "已排程",
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

DATA_CACHE = {"news": [], "standings": {}, "last_slow": 0}

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

def translate(cat, key):
    res = I18N.get(cat, {}).get(key, key)
    if cat == 'teams' and res == key:
        for en, zh in I18N['teams'].items():
            if en in key: return zh
    return res

def get_image_base64(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
        if r.status_code == 200:
            return f"data:image/jpeg;base64,{base64.b64encode(r.content).decode('utf-8')}"
    except: pass
    return "https://via.placeholder.com/80"

def fetch_slow():
    print("Fetching Slow Data...")
    standings = {}
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = requests.get(f"{BASE_URL}/competitions/{code}/standings", headers=HEADERS, timeout=5)
            if r.status_code == 200:
                table = []
                for row in r.json()['standings'][0]['table'][:15]:
                    table.append({
                        "pos": row['position'], "team": translate('teams', row['team']['name']),
                        "played": row['playedGames'], "points": row['points'], "crest": row['team']['crest']
                    })
                standings[code] = table
        except: pass
    DATA_CACHE['standings'] = standings

    news = []
    try:
        r = requests.get("https://api.dongqiudi.com/app/tabs/iphone/1.json", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        for article in r.json().get('articles', [])[:6]:
            if 'thumb' in article:
                news.append({
                    "id": article['id'], "title": article['title'],
                    "img": get_image_base64(article['thumb']),
                    "url": article.get('share', '#'),
                    "body": article.get('description', '')
                })
    except: pass
    DATA_CACHE['news'] = news
    DATA_CACHE['last_slow'] = time.time()

def fetch_fast():
    live = []
    upcoming = []
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=5)
        if r.status_code == 200:
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
                    "utcDate": m['utcDate'],
                    "venue": m.get('venue', '未提供'),
                    "events": [], "lineups": {"home": [], "away": []}
                }
                if m['status'] in ['IN_PLAY', 'PAUSED']:
                    try:
                        d = requests.get(f"{BASE_URL}/matches/{m['id']}", headers=HEADERS, timeout=3).json()
                        item['events'] = d.get('goals', [])
                        item['lineups']['home'] = [p['name'] for p in d.get('homeTeam', {}).get('lineup', [])]
                        item['lineups']['away'] = [p['name'] for p in d.get('awayTeam', {}).get('lineup', [])]
                    except: pass
                    live.append(item)
                else:
                    upcoming.append(item)
    except: pass
    return live, upcoming

def generate_html(live, upcoming):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M:%S')
    
    standings_html = ""
    for lg, tbl in DATA_CACHE['standings'].items():
        rows = "".join([f"<tr><td>{t['pos']}</td><td><img src='{t['crest']}' width='20'> {t['team']}</td><td>{t['played']}</td><td><strong>{t['points']}</strong></td></tr>" for t in tbl])
        standings_html += f"<div class='card standings-card' id='standings-{lg}' style='display:none;'><h3>{lg} 積分榜</h3><table>{rows}</table></div>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO Live</title>
<style>
    body {{ background:#05070a; color:#e2e8f0; font-family:sans-serif; margin:0; padding:0; }}
    .nav {{ background:#0f172a; padding:15px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; position:sticky; top:0; z-index:100; }}
    .card {{ background:#0f172a; margin:10px; padding:15px; border-radius:12px; border:1px solid #1e293b; }}
    .live {{ border-color:#22c55e; }}
    .score {{ font-size:24px; font-weight:bold; color:#22c55e; text-align:center; }}
    .row {{ display:flex; justify-content:space-between; align-items:center; }}
    .news-item {{ display:flex; gap:10px; margin-bottom:10px; }}
    .news-img {{ width:80px; height:60px; object-fit:cover; border-radius:8px; }}
    .modal {{ display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.9); }}
    .modal-content {{ background:#0f172a; margin:10% auto; padding:20px; width:90%; border-radius:12px; border:1px solid #22c55e; max-height:80vh; overflow-y:auto; }}
    .tab-btn {{ background:#1e293b; color:#fff; padding:5px 12px; border-radius:15px; border:1px solid #333; margin-right:5px; }}
    .tab-btn.active {{ background:#22c55e; }}
    table {{ width:100%; border-collapse:collapse; }}
    td, th {{ padding:8px; border-bottom:1px solid #333; text-align:center; }}
</style>
</head>
<body>
<div class="nav">
    <div style="font-weight:bold;">CSL<span style="color:#22c55e;">PRO</span></div>
    <div style="font-size:12px; color:#aaa;">{now_str}</div>
</div>

<div id="live-container">
    <h3 style="padding:0 15px; color:#22c55e;">正在進行 (Live)</h3>
    {''.join([f'''
    <div class="card live" onclick='openMatch({json.dumps(m, ensure_ascii=False)})'>
        <div class="row" style="font-size:12px; color:#aaa; margin-bottom:5px;"><span>{m['league']}</span><span>{m['status']}</span></div>
        <div class="row">
            <div style="text-align:center; flex:1;"><img src="{m['homeLogo']}" width="40"><br>{m['home']}</div>
            <div class="score">{m['score']}</div>
            <div style="text-align:center; flex:1;"><img src="{m['awayLogo']}" width="40"><br>{m['away']}</div>
        </div>
        <div style="text-align:center; font-size:12px; margin-top:5px;">📍 {m['venue']}</div>
    </div>''' for m in live]) or '<div style="text-align:center; padding:20px; color:#666;">目前暫無賽事</div>'}
</div>

<div style="padding:15px;">
    <button class="tab-btn active" onclick="showTab('PL', this)">英超</button>
    <button class="tab-btn" onclick="showTab('PD', this)">西甲</button>
    <button class="tab-btn" onclick="showTab('SA', this)">意甲</button>
</div>
{standings_html}

<div class="card">
    <h3>最新新聞</h3>
    {''.join([f'''<div class="news-item" onclick='openNews({json.dumps(n, ensure_ascii=False)})'><img src="{n['img']}" class="news-img"><div>{n['title']}</div></div>''' for n in DATA_CACHE['news']])}
</div>

<div id="upcoming-container">
    <h3 style="padding:0 15px; color:#aaa;">即將開賽</h3>
    {''.join([f'''<div class="card"><div style="font-size:12px; color:#aaa;">{m['utcDate']} | {m['league']}</div><div class="row"><span>{m['home']}</span><span>vs</span><span>{m['away']}</span></div></div>''' for m in upcoming[:10]])}
</div>

<div id="myModal" class="modal"><div id="modal-content" class="modal-content"></div></div>
<div style="text-align:center; padding:30px; color:#666;">v44.0 Auto-Daemon</div>

<script>
function openMatch(m) {{
    let events = m.events.map(e => `<div>${{e.minute}}' ${{e.scorer.name}} (⚽)</div>`).join('') || '無進球事件';
    let lineups = (m.lineups.home.length > 0) ? `主隊: ${{m.lineups.home.join(', ')}}<br><br>客隊: ${{m.lineups.away.join(', ')}}` : '需升級 API 方案以查看名單';
    document.getElementById('modal-content').innerHTML = `
        <h2 style="text-align:center; color:#22c55e;">${{m.home}} vs ${{m.away}}</h2>
        <h1 style="text-align:center;">${{m.score}}</h1>
        <hr><h3>事件</h3>${{events}}<h3>名單</h3><div style="font-size:12px; color:#aaa;">${{lineups}}</div>
        <button onclick="document.getElementById('myModal').style.display='none'" style="width:100%; margin-top:20px; padding:10px; background:#333; color:#fff; border:none;">關閉</button>
    `;
    document.getElementById('myModal').style.display = 'block';
}}
function openNews(n) {{
    document.getElementById('modal-content').innerHTML = `<h3>${{n.title}}</h3><img src="${{n.img}}" style="width:100%;"><p>${{n.body}}</p><button onclick="document.getElementById('myModal').style.display='none'" style="width:100%; margin-top:20px; padding:10px; background:#333; color:#fff; border:none;">關閉</button>`;
    document.getElementById('myModal').style.display = 'block';
}}
function showTab(lg, btn) {{
    document.querySelectorAll('.standings-card').forEach(e => e.style.display='none');
    document.getElementById('standings-'+lg).style.display='block';
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    if(btn) btn.classList.add('active');
}}
showTab('PL');
</script>
</body>
</html>"""
    push_to_server(html)

if __name__ == "__main__":
    fetch_slow()
    while True:
        try:
            generate_and_push()
            time.sleep(30)
        except Exception as e:
            # 2. 核心修正：捕獲所有錯誤並繼續，防止卡死
            print(f"Error: {e}")
            traceback.print_exc()
            time.sleep(30)
