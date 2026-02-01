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
REMOTE_PATH = "/www/wwwroot/hsapi.xyz/index.html"

ALLOWED = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']
LEAGUE_CONF = [
    {'code': 'PL', 'name': '英超'}, {'code': 'PD', 'name': '西甲'},
    {'code': 'SA', 'name': '意甲'}, {'code': 'BL1', 'name': '德甲'},
    {'code': 'FL1', 'name': '法甲'}, {'code': 'CL', 'name': '歐冠'}
]

# Simple Prod Dictionary
I18N = {
    "Man City": "曼城", "Liverpool": "利物浦", "Arsenal": "阿森納", "Real Madrid": "皇家馬德里",
    "Barcelona": "巴塞隆納", "Bayern": "拜仁慕尼黑", "Inter": "國際米蘭", "Milan": "AC米蘭",
    "Juventus": "尤文圖斯", "PSG": "巴黎聖日耳門", "Chelsea": "切爾西", "Man United": "曼聯",
    "Tottenham": "熱刺", "Newcastle": "紐卡斯爾聯", "Aston Villa": "阿斯頓維拉",
    "West Ham": "西漢姆聯", "Everton": "艾弗頓", "Wolves": "狼隊", "Brighton": "布萊頓",
    "Fulham": "富勒姆", "Brentford": "布倫特福德", "Crystal Palace": "水晶宮",
    "Nottm Forest": "諾丁漢森林", "Bournemouth": "伯恩茅斯", "Luton": "卢顿",
    "Burnley": "伯恩利", "Sheff Utd": "謝菲爾德聯", "Girona": "赫羅納",
    "Real Sociedad": "皇家社會", "Betis": "貝蒂斯", "Athletic": "畢爾包",
    "Valencia": "瓦倫西亞", "Villarreal": "比利亚雷亚尔", "Sevilla": "塞維利亞",
    "Lyon": "里昂", "Marseille": "馬賽", "Monaco": "摩納哥", "Lille": "里爾",
    "Nice": "尼斯", "Lens": "朗斯", "Rennes": "雷恩", "Benfica": "本菲卡",
    "Sporting CP": "葡萄牙體育", "Porto": "波爾圖", "Ajax": "阿賈克斯", "PSV": "PSV埃因霍溫",
    "Feyenoord": "費耶諾德", "Galatasaray": "加拉塔薩雷", "Fenerbahce": "費內巴切"
}

def translate(txt):
    for k, v in I18N.items():
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
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    
    try:
        r = requests.get(f"{BASE_URL}/matches?dateFrom={yesterday}&dateTo={tomorrow}", headers=HEADERS, timeout=15)
        matches = r.json().get('matches', [])
    except: return

    live, upcoming = [], []
    
    for m in matches:
        code = m['competition']['code']
        if code not in ALLOWED: continue
        
        status = m['status']
        lg_name = next((l['name'] for l in LEAGUE_CONF if l['code'] == code), code)
        
        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        bj_dt = utc_dt + timedelta(hours=9) # Japan/Beijing Time Fix
        time_str = bj_dt.strftime('%H:%M')
        date_str = bj_dt.strftime('%m/%d')
        
        status_display = "進行中" if status == 'IN_PLAY' else status
        if 'minute' in m: status_display = f"{m['minute']}'"

        item = {
            'league': lg_name, 'code': code,
            'home': translate(m['homeTeam']['shortName'] or m['homeTeam']['name']),
            'away': translate(m['awayTeam']['shortName'] or m['awayTeam']['name']),
            'homeLogo': m['homeTeam']['crest'], 'awayLogo': m['awayTeam']['crest'],
            'score': f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
            'status': status_display, 'time': time_str, 'date': date_str
        }
        
        if status in ['IN_PLAY', 'PAUSED', 'HT']: live.append(item)
        elif status in ['TIMED', 'SCHEDULED']: upcoming.append(item)

    now_str = datetime.now().strftime('%Y/%m/%d %H:%M')
    
    # HTML (Stable v55 Layout)
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CSL PRO</title>
<style>
    body {{ background:#05070a; color:#e2e8f0; font-family:sans-serif; padding:10px; }}
    .nav {{ background:#0f172a; padding:15px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; }}
    .card {{ background:#0f172a; margin-bottom:10px; padding:15px; border-radius:12px; border:1px solid #1e293b; }}
    .live-border {{ border-color:#22c55e; }}
    .row {{ display:flex; justify-content:space-between; align-items:center; }}
    .team {{ display:flex; align-items:center; gap:8px; width:40%; font-size:14px; }}
    .team img {{ width:24px; }}
    .score {{ font-size:20px; font-weight:bold; color:#22c55e; }}
    .badge {{ background:#1e293b; padding:2px 6px; border-radius:4px; font-size:12px; color:#aaa; }}
</style>
</head>
<body>
<div class="nav"><div>CSL<span style="color:#22c55e">PRO</span></div><div style="font-size:12px">{now_str}</div></div>
<h3 style="color:#22c55e">正在進行</h3>
{''.join([f'''<div class="card live-border"><div class="row" style="margin-bottom:10px"><span class="badge">{m['league']}</span><span style="color:#22c55e">{m['status']}</span></div><div class="row"><div class="team">{m['home']} <img src="{m['homeLogo']}"></div><div class="score">{m['score']}</div><div class="team" style="justify-content:flex-end"><img src="{m['awayLogo']}"> {m['away']}</div></div></div>''' for m in live]) or '<div style="text-align:center;color:#666">暫無賽事</div>'}
<h3 style="color:#aaa;margin-top:30px">即將開賽</h3>
{''.join([f'''<div class="card"><div class="row" style="margin-bottom:10px"><span class="badge">{m['league']}</span><span class="badge">{m['date']} {m['time']}</span></div><div class="row"><div class="team">{m['home']} <img src="{m['homeLogo']}"></div><div class="score" style="font-size:14px;color:#666">VS</div><div class="team" style="justify-content:flex-end"><img src="{m['awayLogo']}"> {m['away']}</div></div></div>''' for m in upcoming])}
</body></html>"""
    
    push(html)

if __name__ == "__main__":
    run()
    while True:
        time.sleep(30)
        run()
