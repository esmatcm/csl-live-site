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

# PATHS
PATH_INDEX = "/www/wwwroot/hsapi.xyz/index.html" # Production
PATH_FULL = "/www/wwwroot/hsapi.xyz/full.html"   # Full List
PATH_DATA_PROD = "/www/wwwroot/hsapi.xyz/data.json"      # For Index
PATH_DATA_FULL = "/www/wwwroot/hsapi.xyz/data_full.json" # For Full

# Allowed for Production (Strict)
ALLOWED = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']

# --- DICTIONARY (Full v55) ---
I18N_TC = {
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
    "Feyenoord": "費耶諾德", "Galatasaray": "加拉塔薩雷", "Fenerbahce": "費內巴切",
    "Celtic": "凱爾特人", "Rangers": "流浪者", "Club Brugge": "布魯日"
}
I18N_SC = {
    "阿森納": "阿森纳", "貝蒂斯": "贝蒂斯", "瓦倫西亞": "瓦伦西亚", "塞維利亞": "塞维利亚",
    "勒沃庫森": "勒沃库森", "拜仁慕尼黑": "拜仁慕尼黑", "多特蒙德": "多特蒙德", "萊比錫": "莱比锡",
    "國際米蘭": "国际米兰", "AC米蘭": "AC米兰", "尤文圖斯": "尤文图斯", "博洛尼亞": "博洛尼亚",
    "羅馬": "罗马", "亞特蘭大": "亚特兰大", "拿坡里": "那不勒斯", "拉齊奧": "拉齐奥",
    "巴黎聖日耳門": "巴黎圣日耳曼", "摩納哥": "摩纳哥", "布雷斯特": "布雷斯特", "里爾": "里尔",
    "尼斯": "尼斯", "朗斯": "朗斯", "馬賽": "马赛", "里昂": "里昂", "葡萄牙體育": "葡萄牙体育",
    "本菲卡": "本菲卡", "波爾圖": "波尔图", "阿賈克斯": "阿贾克斯", "PSV埃因霍溫": "PSV埃因霍温",
    "費耶諾德": "费耶诺德", "加拉塔薩雷": "加拉塔萨雷", "費內巴切": "费内巴切",
    "紐卡斯爾聯": "纽卡斯尔联", "謝菲爾德聯": "谢菲尔德联", "諾丁漢森林": "诺丁汉森林"
}

def get_trilingual(text_en):
    if not text_en: return {"en": "", "tc": "", "sc": ""}
    tc = text_en
    if text_en in I18N_TC: tc = I18N_TC[text_en]
    else:
        for k, v in I18N_TC.items():
            if k in text_en: tc = v; break
    sc = I18N_SC.get(tc, tc)
    return {"en": text_en, "tc": tc, "sc": sc}

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

def fetch_match_details(match_id):
    try:
        r = requests.get(f"{BASE_URL}/matches/{match_id}", headers=HEADERS, timeout=5)
        if r.status_code == 200: return r.json()
    except: pass
    return None

def run():
    # Fetch Wide Window
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    
    try:
        r = requests.get(f"{BASE_URL}/matches?dateFrom={yesterday}&dateTo={tomorrow}", headers=HEADERS, timeout=15)
        matches = r.json().get('matches', [])
    except: return

    data_prod = [] # Top 5 Only
    data_full = [] # All Matches
    
    for m in matches:
        code = m['competition']['code']
        mid = m['id']
        status = m['status']
        
        events = []
        lineups = {"home": [], "away": []}
        referees = []
        coach = {}

        # Tier 3 Details (Only if interesting status)
        if status in ['IN_PLAY', 'PAUSED', 'FINISHED']:
            details = fetch_match_details(mid)
            if details:
                for g in details.get('goals', []):
                    scorer = g['scorer']['name'] if g.get('scorer') else "Unknown"
                    events.append({"minute": g['minute'], "type": "goal", "text": {"en": f"Goal: {scorer}", "tc": f"進球: {scorer}", "sc": f"进球: {scorer}"}})
                for b in details.get('bookings', []):
                    player = b['player']['name']
                    card_en = b['card'].replace('_CARD', '').lower()
                    card_tc = "紅牌" if card_en == 'red' else "黃牌"
                    card_sc = "红牌" if card_en == 'red' else "黄牌"
                    events.append({"minute": b['minute'], "type": "card", "card": card_en, "text": {"en": f"Card: {player}", "tc": f"{card_tc}: {player}", "sc": f"{card_sc}: {player}"}})
                events.sort(key=lambda x: x['minute'], reverse=True)
                
                for p in details.get('homeTeam', {}).get('lineup', []): lineups['home'].append(p['name'])
                for p in details.get('awayTeam', {}).get('lineup', []): lineups['away'].append(p['name'])
                for r in details.get('referees', []): referees.append(r['name'])

        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        local_dt = utc_dt + timedelta(hours=9) # Japan
        time_str = local_dt.strftime('%H:%M')
        date_str = local_dt.strftime('%m/%d')
        
        status_map = {
            "IN_PLAY": {"en": "LIVE", "tc": "進行中", "sc": "进行中"},
            "PAUSED": {"en": "HT", "tc": "中場", "sc": "中场"},
            "FINISHED": {"en": "FT", "tc": "完賽", "sc": "完赛"},
            "TIMED": {"en": "UPCOMING", "tc": "未開賽", "sc": "未开赛"},
            "SCHEDULED": {"en": "UPCOMING", "tc": "未開賽", "sc": "未开赛"}
        }
        st_obj = status_map.get(status, {"en": status, "tc": status, "sc": status})
        if status == 'IN_PLAY' and 'minute' in m:
            min_str = f"{m['minute']}'"
            st_obj = {"en": min_str, "tc": min_str, "sc": min_str}

        item = {
            "id": m['id'],
            "league": get_trilingual(m['competition']['name']),
            "home": get_trilingual(m['homeTeam']['shortName'] or m['homeTeam']['name']),
            "away": get_trilingual(m['awayTeam']['shortName'] or m['awayTeam']['name']),
            "homeLogo": m['homeTeam']['crest'],
            "awayLogo": m['awayTeam']['crest'],
            "score": f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
            "status": st_obj,
            "statusRaw": status,
            "time": time_str,
            "date": date_str,
            "events": events,
            "lineups": lineups,
            "referees": referees,
            "streams": []
        }
        
        # Add Streams
        if status in ['IN_PLAY', 'TIMED', 'SCHEDULED']:
            item['streams'] = [
                {"name": {"en": "Zhibo8", "tc": "直播吧", "sc": "直播吧"}, "url": f"https://www.zhibo8.com/search/?k={item['home']['sc']}"},
                {"name": {"en": "88Kanqiu", "tc": "88看球", "sc": "88看球"}, "url": f"http://www.88kanqiu.one/search.html?q={item['home']['sc']}"}
            ]

        # Add to FULL list
        data_full.append(item)
        
        # Add to PROD list (Filtered)
        if code in ALLOWED:
            data_prod.append(item)

    # Push Data
    push(json.dumps(data_prod, ensure_ascii=False), PATH_DATA_PROD)
    push(json.dumps(data_full, ensure_ascii=False), PATH_DATA_FULL)
    
    # Push HTML (Quantum UI)
    try:
        with open('csl-live-site/index_quantum_fixed.html', 'r', encoding='utf-8') as f:
            html_base = f.read()
            
        # PROD (points to data.json)
        html_prod = html_base.replace('data_v60.json', 'data.json')
        push(html_prod, PATH_INDEX)
        
        # FULL (points to data_full.json)
        html_full = html_base.replace('data_v60.json', 'data_full.json')
        push(html_full, PATH_FULL)
        
    except: pass

if __name__ == "__main__":
    run()
    while True:
        time.sleep(30)
        run()
