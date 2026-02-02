import requests
import json
import time
import hashlib
import sys
from datetime import datetime, timedelta

# V58.15 END-TO-END TEST (Trigger Verifier)
DAEMON_VERSION = "v58.15_e2e_test"
BUILD_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

import subprocess
import os
import shutil

# GLOBAL STATE
LAST_SIGNAL_VERSION = None

# CONFIG
MISSION_CONTROL_PATH = r"C:\ai-repos\ai-mission-control"
SIGNAL_FILE = os.path.join(MISSION_CONTROL_PATH, "DEPLOYS", "hsapi", "latest.json")
TMP_SIGNAL_FILE = os.path.join(MISSION_CONTROL_PATH, "DEPLOYS", "hsapi", "latest.json.tmp")
WEBSITE_REPO_PATH = r"C:\Users\z4000\clawd\csl-live-site" # Local repo path

def get_git_hash():
    try:
        return subprocess.check_output(["git", "-C", WEBSITE_REPO_PATH, "rev-parse", "HEAD"]).strip().decode('utf-8')
    except:
        return "unknown-hash"

# REMOVED sys.stdout config

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}

# AI CONFIG (Gemini)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# --- THROTTLING CONFIG ---
REQUEST_INTERVAL = 2.0  # Seconds between requests
MAX_RETRIES = 5
BASE_BACKOFF = 2.0      # Seconds

def safe_request(url):
    retries = 0
    while retries <= MAX_RETRIES:
        try:
            # 1. Throttling
            time.sleep(REQUEST_INTERVAL)
            
            r = requests.get(url, headers=HEADERS, timeout=10)
            
            # 2. Backoff on 429
            if r.status_code == 429:
                wait = BASE_BACKOFF * (2 ** retries)
                print(f"429 Too Many Requests. Waiting {wait}s...")
                time.sleep(wait)
                retries += 1
                continue
                
            return r
        except Exception as e:
            print(f"Request Error: {e}")
            retries += 1
            time.sleep(BASE_BACKOFF)
            
    print("Max retries exceeded.")
    return None

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

PATH_INDEX = "/www/wwwroot/hsapi.xyz/index.html"
PATH_DATA = "/www/wwwroot/hsapi.xyz/data.json"
PATH_HEALTH = "/www/wwwroot/hsapi.xyz/health.html"

ALLOWED = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']
LEAGUE_CONF = [
    {'code': 'PL', 'name': {'en': 'Premier League', 'tc': '英超', 'sc': '英超'}},
    {'code': 'PD', 'name': {'en': 'La Liga', 'tc': '西甲', 'sc': '西甲'}},
    {'code': 'SA', 'name': {'en': 'Serie A', 'tc': '意甲', 'sc': '意甲'}},
    {'code': 'BL1', 'name': {'en': 'Bundesliga', 'tc': '德甲', 'sc': '德甲'}},
    {'code': 'FL1', 'name': {'en': 'Ligue 1', 'tc': '法甲', 'sc': '法甲'}},
    {'code': 'CL', 'name': {'en': 'Champions League', 'tc': '歐冠', 'sc': '欧冠'}}
]

# --- EXPANDED DICTIONARIES ---
# TC (Traditional)
I18N_TC = {
    # Top Teams
    "Man City": "曼城", "Liverpool": "利物浦", "Arsenal": "阿森納", "Real Madrid": "皇家馬德里",
    "Barcelona": "巴塞隆納", "Bayern": "拜仁慕尼黑", "Inter": "國際米蘭", "Milan": "AC米蘭",
    "Juventus": "尤文圖斯", "PSG": "巴黎聖日耳門", "Chelsea": "切爾西", "Man United": "曼聯",
    "Tottenham": "熱刺", "Newcastle": "紐卡斯爾聯", "Aston Villa": "阿斯頓維拉",
    "West Ham": "西漢姆聯", "Everton": "艾弗頓", "Wolves": "狼隊", "Brighton": "布萊頓",
    "Fulham": "富勒姆", "Brentford": "布倫特福德", "Crystal Palace": "水晶宮",
    "Nottm Forest": "諾丁漢森林", "Bournemouth": "伯恩茅斯", "Luton": "卢顿",
    "Burnley": "伯恩利", "Sheff Utd": "謝菲爾德聯", "Girona": "赫羅納",
    "Real Sociedad": "皇家社會", "Betis": "貝蒂斯", "Athletic": "畢爾包", "Athletic Club": "畢爾包",
    "Valencia": "瓦倫西亞", "Villarreal": "比利亚雷亚尔", "Sevilla": "塞維利亞",
    "Lyon": "里昂", "Marseille": "馬賽", "Monaco": "摩納哥", "Lille": "里爾",
    "Nice": "尼斯", "Lens": "朗斯", "Rennes": "雷恩", "Benfica": "本菲卡",
    "Sporting CP": "葡萄牙體育", "Porto": "波爾圖", "Ajax": "阿賈克斯", "PSV": "PSV埃因霍溫",
    "Feyenoord": "費耶諾德", "Galatasaray": "加拉塔薩雷", "Fenerbahce": "費內巴切",
    "Celtic": "凱爾特人", "Rangers": "流浪者", "Club Brugge": "布魯日", "Union SG": "聖吉羅斯",
    "Real Oviedo": "奧維耶多", "Hoffenheim": "霍芬海姆", "Frankfurt": "法蘭克福",
    "RB Leipzig": "萊比錫", "Werder Bremen": "不萊梅", "Augsburg": "奧格斯堡",
    "Leeds United": "里茲聯", "Osasuna": "奧薩蘇納", "Paris FC": "巴黎FC",
    "Napoli": "拿坡里", "HSV": "漢堡", "Levante": "萊萬特", "Lorient": "洛里昂",
    "Cagliari": "卡利亞里", "Elche": "埃爾切", "AC Pisa": "比薩", "Como": "科莫",
    "Parma": "帕爾馬", "Venezia": "威尼斯", "Cremonese": "克雷莫納", "Sampdoria": "桑普多利亞",
    "Heidenheim": "海登海姆", "Darmstadt": "達姆施塔特", "Bochum": "波鴻", "Mainz": "美因茨",
    "St. Pauli": "聖保利", "Holstein Kiel": "基爾", "Stuttgart": "斯圖加特", "Freiburg": "弗賴堡",
    "Gladbach": "門興", "Union Berlin": "柏林聯", "Wolfsburg": "沃爾夫斯堡", "Mainz 05": "美因茨",
    "Dusseldorf": "杜塞爾多夫", "Paderborn": "帕德博恩", "Karlsruhe": "卡爾斯魯厄",
    "Hertha": "柏林赫塔", "Greuther Fürth": "菲爾特", "Elversberg": "埃爾弗斯貝格",
    "Magdeburg": "馬格德堡", "Nurnberg": "紐倫堡", "Schalke": "沙爾克04",
    "Kaiserslautern": "凱澤斯劳滕", "Wehen": "韋恩", "Rostock": "羅斯托克",
    "Braunschweig": "布倫瑞克", "Osnabrück": "奧斯納布呂克", "Salernitana": "薩勒尼塔納",
    "Frosinone": "弗羅西諾內", "Sassuolo": "薩索洛", "Udinese": "烏迪內斯", "Empoli": "恩波利",
    "Verona": "維羅納", "Lecce": "萊切", "Genoa": "熱那亞", "Monza": "蒙扎", "Torino": "都靈",
    "Lazio": "拉齊奧", "Roma": "羅馬", "Bologna": "博洛尼亞", "Fiorentina": "佛羅倫薩",
    "Atalanta": "亞特蘭大", "Southampton": "南安普頓", "Leicester": "萊斯特城", "Ipswich": "伊普斯維奇",
    "Mallorca": "馬略卡", "Rayo Vallecano": "巴列卡諾", "Alaves": "阿拉維斯", "Las Palmas": "拉斯帕爾馬斯",
    "Getafe": "赫塔費", "Cadiz": "加的斯", "Granada": "格拉納達", "Almeria": "阿爾梅里亞",
    "Strasbourg": "斯特拉斯堡", "Toulouse": "圖盧茲", "Nantes": "南特", "Le Havre": "勒阿弗爾",
    "Montpellier": "蒙彼利埃", "Metz": "梅斯", "Clermont": "克萊蒙", "Clermont Foot": "克萊蒙",
    "Lorient": "洛里昂", "Heidenheim": "海登海姆", "Darmstadt": "達姆施塔特", "Bochum": "波鴻",
    "Augsburg": "奧格斯堡", "Mainz": "美因茨", "Mainz 05": "美因茨", "Union Berlin": "柏林聯",
    "Freiburg": "弗賴堡", "Wolfsburg": "沃爾夫斯堡", "Gladbach": "門興", "M'gladbach": "門興",
    "Hoffenheim": "霍芬海姆", "Frankfurt": "法蘭克福", "Stuttgart": "斯圖加特", "Werder Bremen": "不萊梅",
    "Las Palmas": "拉斯帕爾馬斯", "Alaves": "阿拉維斯", "Cadiz": "加的斯", "Granada": "格拉納達",
    "Mallorca": "馬略卡", "Osasuna": "奧薩蘇納", "Rayo Vallecano": "巴列卡諾", "Celta": "塞爾塔",
    "Empoli": "恩波利", "Frosinone": "弗羅西諾內", "Salernitana": "薩勒尼塔納", "Lecce": "萊切",
    "Verona": "維羅納", "Hellas Verona": "維羅納", "Udinese": "烏迪內斯", "Sassuolo": "薩索洛",
    "Monza": "蒙扎", "Genoa": "熱那亞", "Torino": "都靈", "Bologna": "博洛尼亞", "Luton Town": "卢顿",
    "Sheffield United": "謝菲爾德聯", "Nottm Forest": "諾丁漢森林", "Nottingham Forest": "諾丁漢森林"
}

# SC (Simplified - Complete Mapping)
I18N_SC = {
    # Auto-mapped from TC where possible, but explicit overrides here
    "阿森納": "阿森纳", "貝蒂斯": "贝蒂斯", "瓦倫西亞": "瓦伦西亚", "塞維利亞": "塞维利亚",
    "勒沃庫森": "勒沃库森", "拜仁慕尼黑": "拜仁慕尼黑", "多特蒙德": "多特蒙德", "萊比錫": "莱比锡",
    "國際米蘭": "国际米兰", "AC米蘭": "AC米兰", "尤文圖斯": "尤文图斯", "博洛尼亞": "博洛尼亚",
    "羅馬": "罗马", "亞特蘭大": "亚特兰大", "拿坡里": "那不勒斯", "拉齊奧": "拉齐奥",
    "巴黎聖日耳門": "巴黎圣日耳曼", "摩納哥": "摩纳哥", "布雷斯特": "布雷斯特", "里爾": "里尔",
    "尼斯": "尼斯", "朗斯": "朗斯", "馬賽": "马赛", "里昂": "里昂", "葡萄牙體育": "葡萄牙体育",
    "本菲卡": "本菲卡", "波爾圖": "波尔图", "阿賈克斯": "阿贾克斯", "PSV埃因霍溫": "PSV埃因霍温",
    "費耶諾德": "费耶诺德", "加拉塔薩雷": "加拉塔萨雷", "費內巴切": "费内巴切",
    "紐卡斯爾聯": "纽卡斯尔联", "謝菲爾德聯": "谢菲尔德联", "諾丁漢森林": "诺丁汉森林",
    "凱澤斯劳滕": "凯泽斯劳滕", "漢諾威96": "汉诺威96", "紐倫堡": "纽伦堡", "奧斯納布呂克": "奥斯纳布吕克",
    "布倫瑞克": "布伦瑞克", "羅斯托克": "罗斯托克", "沙爾克04": "沙尔克04",
    "薩勒尼塔納": "萨勒尼塔纳", "弗羅西諾內": "弗罗西诺内", "薩索洛": "萨索洛", "克雷莫納": "克雷莫纳",
    "桑普多利亞": "桑普多利亚", "南蒂羅爾": "南蒂罗尔", "斯佩齊亞": "斯佩齐亚",
    "馬略卡": "马略卡", "巴列卡諾": "巴列卡诺", "阿拉維斯": "阿拉维斯", "拉斯帕爾馬斯": "拉斯帕尔马斯",
    "赫塔費": "赫塔费", "加的斯": "加的斯", "格拉納達": "格拉纳达", "阿爾梅里亞": "阿尔梅里亚",
    "蘭斯": "兰斯", "斯特拉斯堡": "斯特拉斯堡", "圖盧茲": "图卢兹", "南特": "南特", 
    "勒阿弗爾": "勒阿弗尔", "蒙彼利埃": "蒙彼利埃", "梅斯": "梅斯", "克萊蒙": "克莱蒙",
    "倫敦": "伦敦", "曼徹斯特": "曼彻斯特", "利物浦": "利物浦", "伯明翰": "伯明翰"
}

STATUS_MAP = {
    "IN_PLAY": {"en": "LIVE", "tc": "進行中", "sc": "进行中"},
    "PAUSED": {"en": "HT", "tc": "中場", "sc": "中场"},
    "FINISHED": {"en": "FT", "tc": "完賽", "sc": "完赛"},
    "TIMED": {"en": "UPCOMING", "tc": "未開賽", "sc": "未开赛"},
    "SCHEDULED": {"en": "UPCOMING", "tc": "未開賽", "sc": "未开赛"},
    "POSTPONED": {"en": "PPD", "tc": "延期", "sc": "延期"}
}

DATA_CACHE = {"standings": {}, "last_slow": 0}

def get_tri(text_en):
    if not text_en: return {"en": "", "tc": "", "sc": ""}
    
    # 1. Normalize: Remove common prefixes/suffixes/digits
    clean = text_en
    for sub in [" FC", " AFC", " CF", " UD", " SD", " SV", " 1.", "1. ", " RC", " SC"]:
        clean = clean.replace(sub, "")
    clean = clean.strip()
    
    tc = text_en # Default to original if no match
    
    # 2. Exact Match (Try original, then clean)
    if text_en in I18N_TC: 
        tc = I18N_TC[text_en]
    elif clean in I18N_TC:
        tc = I18N_TC[clean]
    else:
        # 3. Partial Match (Heuristic)
        for k, v in I18N_TC.items():
            if k == clean or k in clean: # Check if dictionary key is inside the cleaned name
                tc = v; break
    
    sc = I18N_SC.get(tc, tc) # Get SC from TC key, or fallback to TC
    
    return {"en": text_en, "tc": tc, "sc": sc}

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token


def generate_ai_summary(match):
    if not GEMINI_API_KEY:
        print("AI_WARN: GEMINI_API_KEY missing")
        return ""
    try:
        prompt = (
            "请用简体中文写约100字的赛后分析，分2-3行，每行不超过40字。"
            "要求：说明结果形成的可能原因，语气专业克制，不编造不存在的数据。"
            f"比赛：{match['home']['sc']} vs {match['away']['sc']}，比分 {match['score']}，"
            f"联赛 {match['league']['sc']}，时间 {match['date']} {match['time']}。"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.5, "maxOutputTokens": 220}
        }
        r = requests.post(
            f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
            json=body,
            timeout=15
        )
        if r.status_code != 200:
            print(f"AI_WARN: status={r.status_code} body={r.text[:200]}")
            return ""
        data = r.json()
        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        if not text:
            print(f"AI_WARN: empty response {str(data)[:200]}")
        return text
    except Exception:
        return ""

def push(content, path):
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': path, 'data': content, 'encoding': 'utf-8'}
        r = requests.post(url, data=payload, timeout=10)
        return {"status_code": r.status_code, "text": r.text}
    except Exception as e:
        return {"status_code": "ERR", "text": str(e)}

def fetch_details(mid):
    try:
        r = safe_request(f"{BASE_URL}/matches/{mid}")
        if r and r.status_code == 200: return r.json()
    except: pass
    return None

def fetch_standings_slow():
    # print("Fetching Standings...")
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = safe_request(f"{BASE_URL}/competitions/{code}/standings")
            if r and r.status_code == 200:
                table = []
                for row in r.json()['standings'][0]['table'][:15]:
                    table.append({
                        "pos": row['position'],
                        "team": get_tri(row['team']['shortName'] or row['team']['name']),
                        "played": row['playedGames'],
                        "points": row['points'],
                        "crest": row['team']['crest']
                    })
                DATA_CACHE['standings'][code] = table
                time.sleep(1)
        except: pass
    DATA_CACHE['last_slow'] = time.time()

def run():
    # print("Running Update Cycle...")
    if os.environ.get("QUICK_RUN") == "1":
        final_json = {
            "meta": {
                "daemon": DAEMON_VERSION,
                "build_time": BUILD_TIME,
                "generated_at": datetime.now().isoformat(),
                "job_id": f"{DAEMON_VERSION}-{int(time.time())}"
            },
            "matches": [],
            "standings": {}
        }
        upload_result = push(json.dumps(final_json, ensure_ascii=False), PATH_DATA)
        try:
            time.sleep(2)
            ts2 = int(time.time())
            check2 = safe_request(f"https://hsapi.xyz/data.json?ts={ts2}")
            meta2 = check2.json().get('meta', {}) if check2 and check2.status_code == 200 else {}
            print(f"PUSH_LOG local_job_id={final_json['meta']['job_id']} upload_target_path={PATH_DATA} upload_result={upload_result}")
            print(f"PUSH_LOG verify_fetch_job_id={meta2.get('job_id')} ts={ts2}")
        except Exception as e:
            print(f"PUSH_LOG local_job_id={final_json['meta']['job_id']} upload_target_path={PATH_DATA} upload_result={upload_result}")
            print(f"PUSH_LOG verify_fetch_job_id=ERROR ts=ERROR error={e}")
        return

    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    
    try:
        r = requests.get(f"{BASE_URL}/matches?dateFrom={yesterday}&dateTo={tomorrow}", headers=HEADERS, timeout=15)
        matches = r.json().get('matches', [])
    except:
        return

    if not DATA_CACHE['standings'] or time.time() - DATA_CACHE['last_slow'] > 3600:
        fetch_standings_slow()

    live_list, up_list, fin_list = [], [], []
    json_data = [] 
    
    for m in matches:
        code = m['competition']['code']
        if code not in ALLOWED: continue
        
        mid = m['id']
        status = m['status']
        
        events, lineups, referees = [], {"home":[], "away":[]}, []
        
        if status in ['IN_PLAY', 'PAUSED', 'HT', 'FINISHED', 'FT']:
            if status != 'FINISHED' or len(fin_list) < 10:
                det = fetch_details(mid)
                if det:
                    for g in det.get('goals', []):
                        scorer = g['scorer']['name'] if g.get('scorer') else "?"
                        events.append({"minute": g['minute'], "type": "goal", "text": {"en": f"Goal: {scorer}", "tc": f"進球: {scorer}", "sc": f"进球: {scorer}"}})
                    for b in det.get('bookings', []):
                        player = b['player']['name']
                        card_en = b['card'].replace('_CARD', '').lower()
                        card_tc = "紅牌" if card_en == 'red' else "黃牌"
                        card_sc = "红牌" if card_en == 'red' else "黄牌"
                        events.append({"minute": b['minute'], "type": "card", "card": card_en, "text": {"en": f"Card: {player}", "tc": f"{card_tc}: {player}", "sc": f"{card_sc}: {player}"}})
                    
                    events.sort(key=lambda x: (x['minute'] or 0), reverse=True)

                    for p in det.get('homeTeam', {}).get('lineup', []): lineups['home'].append(p['name'])
                    for p in det.get('awayTeam', {}).get('lineup', []): lineups['away'].append(p['name'])
                    for r in det.get('referees', []): referees.append(r['name'])

        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        bj_dt = utc_dt + timedelta(hours=8)
        time_str = bj_dt.strftime('%H:%M')
        date_str = bj_dt.strftime('%m/%d')
        
        st_obj = STATUS_MAP.get(status, {"en": status, "tc": status, "sc": status})
        if status == 'IN_PLAY':
            min_txt = f"{m.get('minute', '')}'" if 'minute' in m else "LIVE"
            st_obj = {"en": min_txt, "tc": min_txt, "sc": min_txt}

        home_tri = get_tri(m['homeTeam']['shortName'] or m['homeTeam']['name'])
        away_tri = get_tri(m['awayTeam']['shortName'] or m['awayTeam']['name'])
        lg_tri = get_tri(m['competition']['name'])

        item = {
            'id': mid, 'code': code,
            'league': lg_tri, 'home': home_tri, 'away': away_tri,
            'homeLogo': m['homeTeam']['crest'], 'awayLogo': m['awayTeam']['crest'],
            'score': f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
            'status': st_obj, 'statusRaw': status,
            'time': time_str, 'date': date_str,
            'events': events, 'lineups': lineups, 'referees': referees
        }
        
        json_data.append(item)
        
        if status in ['IN_PLAY', 'PAUSED', 'HT']: live_list.append(item)
        elif status in ['TIMED', 'SCHEDULED']: up_list.append(item)
        elif status in ['FINISHED', 'FT']: fin_list.append(item)

    up_list.sort(key=lambda x: x['time'])
    fin_list.sort(key=lambda x: x['time'], reverse=True) 

    # AI summaries for finished matches (top 10)
    for m in fin_list[:10]:
        summary = generate_ai_summary(m)
        if summary:
            m["ai"] = {"en": summary, "tc": summary, "sc": summary}

    final_json = {
        "meta": {
            "daemon": DAEMON_VERSION, 
            "build_time": BUILD_TIME,
            "generated_at": datetime.now().isoformat(),
            "job_id": f"{DAEMON_VERSION}-{int(time.time())}" # Unique Job ID per run
        },
        "matches": json_data,
        "standings": DATA_CACHE['standings']
    }
    
    # 1. PUSH
    upload_result = push(json.dumps(final_json, ensure_ascii=False), PATH_DATA)

    # 2. VERIFY (Self-Check with Double Read)
    try:
        time.sleep(2) # Wait for write
        
        # Check 1 (no cache)
        ts = int(time.time())
        check1 = safe_request(f"https://hsapi.xyz/data.json?ts={ts}")
        if not check1 or check1.status_code != 200: raise Exception("Check 1 Failed")
        meta1 = check1.json().get('meta', {})
        
        # Check 2 (Double Read)
        time.sleep(1)
        ts2 = int(time.time())
        check2 = safe_request(f"https://hsapi.xyz/data.json?ts={ts2}")
        if not check2 or check2.status_code != 200: raise Exception("Check 2 Failed")
        meta2 = check2.json().get('meta', {})

        # Required push log fields (always emit)
        print(f"PUSH_LOG local_job_id={final_json['meta']['job_id']} upload_target_path={PATH_DATA} upload_result={upload_result}")
        print(f"PUSH_LOG verify_fetch_job_id={meta2.get('job_id')} ts={ts2}")

        if meta1.get('job_id') != final_json['meta']['job_id']: raise Exception("Job ID Mismatch 1")
        if meta2.get('job_id') != final_json['meta']['job_id']: raise Exception("Job ID Mismatch 2")

        # 3. SIGNAL (Debounced)
        # NOTE: Always update remote data.json first, then update latest.json (Mission Control)
        global LAST_SIGNAL_VERSION
        current_signal_key = f"{DAEMON_VERSION}-{BUILD_TIME}"
        
        # Only push if Version or Build Time changed (Code Deploy), not just data update
        if LAST_SIGNAL_VERSION != current_signal_key:
            real_hash = get_git_hash()
            signal_data = {
                "job_id": final_json['meta']['job_id'],
                "generated_at": final_json['meta']['generated_at'],
                "daemon_version": DAEMON_VERSION,
                "source_commit": real_hash,
                "target_url": "https://hsapi.xyz/data.json",
                "status": "deployed_verified",
                "source_repo": "esmatcm/csl-live-site"
            }
            
            with open(TMP_SIGNAL_FILE, 'w', encoding='utf-8') as f:
                json.dump(signal_data, f, indent=2)
            os.replace(TMP_SIGNAL_FILE, SIGNAL_FILE)
            
            subprocess.run(["git", "-C", MISSION_CONTROL_PATH, "add", "DEPLOYS/hsapi/latest.json"], check=True)
            subprocess.run(["git", "-C", MISSION_CONTROL_PATH, "commit", "-m", f"Deploy Signal: {signal_data['job_id']}"], check=True)

            # Pre-push sync to avoid non-fast-forward
            subprocess.run(["git", "-C", MISSION_CONTROL_PATH, "fetch", "origin"], check=True)
            subprocess.run(["git", "-C", MISSION_CONTROL_PATH, "pull", "--rebase", "--autostash", "origin", "main"], check=True)

            # Log HEAD vs origin/main
            head_short = subprocess.check_output(["git", "-C", MISSION_CONTROL_PATH, "rev-parse", "--short", "HEAD"]).strip().decode("utf-8")
            origin_short = subprocess.check_output(["git", "-C", MISSION_CONTROL_PATH, "rev-parse", "--short", "origin/main"]).strip().decode("utf-8")
            print(f"PUSH_LOG git_head={head_short} git_origin_main={origin_short}")

            subprocess.run(["git", "-C", MISSION_CONTROL_PATH, "push", "origin", "main"], check=True)
            
            LAST_SIGNAL_VERSION = current_signal_key
            print(f"Signal Pushed: {current_signal_key}")
        
    except Exception as e:
        print(f"PUSH_LOG local_job_id={final_json['meta']['job_id']} upload_target_path={PATH_DATA} upload_result={upload_result}")
        print(f"PUSH_LOG verify_fetch_job_id=ERROR ts=ERROR error={e}")

    # --- HTML ---
    std_html = '<div class="std-box">'
    first = True
    for code, rows in DATA_CACHE['standings'].items():
        disp = 'block' if first else 'none'; 
        std_html += f'<div id="st-{code}" style="display:{disp}"><table>'
        for r in rows:
            std_html += f'<tr><td>{r["pos"]}</td><td class="team-cell"><img src="{r["crest"]}" width="18"> <span class="lang" data-en="{r["team"]["en"]}" data-tc="{r["team"]["tc"]}" data-sc="{r["team"]["sc"]}">{r["team"]["sc"]}</span></td><td>{r["points"]}</td></tr>'
        std_html += '</table></div>'
        first = False
    std_html += '</div>'

    filters = '<div class="filters"><button class="f-btn active" onclick="f(\'ALL\',this)"><span class="lang" data-en="ALL" data-tc="全部" data-sc="全部">全部</span></button>'
    for lg in LEAGUE_CONF:
        filters += f'<button class="f-btn" onclick="f(\'{lg["code"]}\',this)"><span class="lang" data-en="{lg["name"]["en"]}" data-tc="{lg["name"]["tc"]}" data-sc="{lg["name"]["sc"]}">{lg["name"]["sc"]}</span></button>'
    filters += '</div>'

    def render_section(lst, is_live, is_fin=False):
        if not lst:
            msg_en = "No Matches"
            msg_tc = "暫無賽事"
            msg_sc = "暂无赛事"
            
            if is_live: 
                msg_en = "No Live Matches"
                msg_tc = "暫無進行中賽事"
                msg_sc = "暂无进行中赛事"
            elif is_fin: 
                msg_en = "No Recent Matches"
                msg_tc = "暫無近期完賽記錄"
                msg_sc = "暂无近期完赛记录"
                
            return f'<div class="no-data"><span class="lang" data-en="{msg_en}" data-tc="{msg_tc}" data-sc="{msg_sc}">{msg_sc}</span></div>'
        h = ''
        for m in lst:
            cls = 'live' if is_live else ''
            st_cls = 'fin' if is_fin else ('live' if is_live else '')
            ai_html = ''
            if is_fin and m.get('ai'):
                ai = m['ai']
                ai_html = f'''<div class="ai-note"><div class="ai-label">AI分析</div><div class="ai-text"><span class="lang" data-en="{ai['en']}" data-tc="{ai['tc']}" data-sc="{ai['sc']}">{ai['sc']}</span></div></div>'''
            h += f'''
            <div class="card {cls}" data-lg="{m['code']}" onclick="openModal('{m['id']}')">
                <div class="head">
                    <span class="lang" data-en="{m['league']['en']}" data-tc="{m['league']['tc']}" data-sc="{m['league']['sc']}">{m['league']['sc']}</span>
                    <span class="st {st_cls} lang" data-en="{m['status']['en']}" data-tc="{m['status']['tc']}" data-sc="{m['status']['sc']}">{m['status']['sc']}</span>
                </div>
                <div class="match">
                    <div class="t"><img src="{m['homeLogo']}"><span class="lang" data-en="{m['home']['en']}" data-tc="{m['home']['tc']}" data-sc="{m['home']['sc']}">{m['home']['sc']}</span></div>
                    <div class="s">{m['score'] if is_live or is_fin else 'VS'}</div>
                    <div class="t right"><span class="lang" data-en="{m['away']['en']}" data-tc="{m['away']['tc']}" data-sc="{m['away']['sc']}">{m['away']['sc']}</span><img src="{m['awayLogo']}"></div>
                </div>
                <div class="sub-info">
                    <span class="badge time">{m['time']}</span>
                    <span style="font-size:10px; opacity:0.5; margin-left:5px">北京時間</span>
                    <span style="font-size:10px; opacity:0.5; margin-left:auto">{m['date']}</span>
                </div>
                {ai_html}
            </div>'''
        return h

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>全球 AI 足球開獎網</title>
        <style>
            :root {{ --bg:#0f1218; --card:#1a1f2e; --text:#e2e8f0; --acc:#00f2ea; --dim:#94a3b8; --border:rgba(255,255,255,0.1); }}
            body {{ background:var(--bg); color:var(--text); font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin:0; padding-bottom:80px; -webkit-tap-highlight-color:transparent; }}
            
            /* Footer */
            .footer {{ text-align:center; padding:20px; color:#444; font-size:10px; margin-top:30px; border-top:1px solid var(--border); }}
            
            /* Responsive Container */
            .container {{ max-width:800px; margin:0 auto; padding:15px; }}
            
            /* Nav */
            .nav {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border-bottom:1px solid var(--border); padding-bottom:15px; }}
            .logo-box {{ display:flex; align-items:center; gap:12px; }}
            .logo-svg {{ width:36px; height:36px; fill:var(--acc); filter:drop-shadow(0 0 5px rgba(0,242,234,0.3)); }}
            .site-title-box {{ display:flex; flex-direction:column; justify-content:center; }}
            .site-title-main {{ font-size:20px; font-weight:900; line-height:1; letter-spacing:1px; color:#fff; }}
            .site-title-sub {{ font-size:10px; color:var(--dim); font-weight:500; letter-spacing:0.5px; text-transform:uppercase; margin-top:2px; }}
            
            .lang-box {{ font-size:12px; border:1px solid var(--border); border-radius:20px; display:flex; padding:2px; background:var(--card); }}
            .l-btn {{ padding:4px 10px; cursor:pointer; color:var(--dim); border-radius:16px; transition:0.2s; }}
            .l-btn.active {{ background:var(--acc); color:#000; font-weight:bold; }}
            
            /* Filters */
            .filters {{ overflow-x:auto; white-space:nowrap; margin-bottom:20px; -webkit-overflow-scrolling:touch; padding-bottom:5px; }}
            .f-btn {{ background:var(--card); color:var(--dim); border:1px solid var(--border); padding:6px 14px; border-radius:20px; margin-right:8px; cursor:pointer; font-size:13px; transition:0.2s; }}
            .f-btn.active {{ background:var(--acc); color:#000; font-weight:bold; border-color:var(--acc); }}
            
            /* Tabs - Improved Click Area */
            .tabs {{ display:flex; border-bottom:1px solid var(--border); margin-bottom:20px; }}
            .tab {{ flex:1; text-align:center; padding:15px 5px; cursor:pointer; color:var(--dim); font-size:14px; position:relative; transition:color 0.2s; }}
            .tab:active {{ background:rgba(255,255,255,0.05); }}
            .tab.active {{ color:var(--acc); font-weight:bold; }}
            .tab.active::after {{ content:''; position:absolute; bottom:-1px; left:0; width:100%; height:2px; background:var(--acc); }}
            
            /* Grid & Performance */
            .grid {{ display:grid; grid-template-columns:1fr; gap:12px; }}
            @media (min-width: 600px) {{ .grid {{ grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }} }}
            .view-section.hidden {{ display:none !important; }} /* Performance Fix */
            
            /* Card */
            .card {{ background:var(--card); border:1px solid var(--border); border-radius:16px; padding:16px; cursor:pointer; transition:transform 0.1s; position:relative; overflow:hidden; }}
            .card:active {{ transform:scale(0.98); }}
            .card.live {{ border-color:rgba(0, 242, 234, 0.4); background:linear-gradient(145deg, rgba(0,242,234,0.05), var(--card)); }}
            
            .head {{ display:flex; justify-content:space-between; font-size:12px; color:var(--dim); margin-bottom:15px; letter-spacing:0.5px; }}
            .st {{ font-weight:bold; }} .st.live {{ color:var(--acc); }}
            
            .match {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }}
            .t {{ display:flex; align-items:center; gap:10px; width:40%; font-size:15px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
            .t.right {{ justify-content:flex-end; text-align:right; }}
            .t img {{ width:28px; height:28px; object-fit:contain; flex-shrink:0; }}
            .s {{ font-size:24px; font-weight:700; font-family:monospace; color:var(--text); }}
            .card.live .s {{ color:var(--acc); }}
            
            .sub-info {{ display:flex; align-items:center; gap:8px; margin-top:10px; border-top:1px solid var(--border); padding-top:8px; }}
            .badge {{ background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px; font-size:11px; color:var(--dim); }}
            
            .ai-note {{ margin-top:10px; padding:8px 10px; background:#121826; border:1px solid var(--border); border-radius:10px; }}
            .ai-label {{ font-size:11px; color:var(--acc); margin-bottom:4px; }}
            .ai-text {{ font-size:12px; line-height:1.45; color:var(--text); white-space:pre-line; }}

            .no-data {{ text-align:center; padding:40px; color:var(--dim); font-size:14px; }}
            
            /* Standings */
            .std-box table {{ width:100%; font-size:13px; border-collapse:collapse; }}
            .std-box td {{ padding:10px; border-bottom:1px solid var(--border); text-align:center; }}
            .std-box .team-cell {{ text-align:left; display:flex; align-items:center; gap:8px; font-weight:500; }}
            
            /* Modal */
            .modal {{ display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.8); backdrop-filter:blur(5px); justify-content:center; align-items:end; }}
            @media (min-width: 600px) {{ .modal {{ align-items:center; }} }}
            .modal-content {{ background:var(--card); width:100%; max-width:500px; border-radius:24px 24px 0 0; padding:25px; border-top:1px solid var(--border); max-height:85vh; overflow-y:auto; animation:slideUp 0.3s ease; }}
            @media (min-width: 600px) {{ .modal-content {{ border-radius:24px; border:1px solid var(--border); width:90%; }} }}
            @keyframes slideUp {{ from {{ transform:translateY(100%); }} to {{ transform:translateY(0); }} }}
            
            .m-section {{ margin-bottom:20px; }}
            .m-title {{ font-size:12px; font-weight:bold; color:var(--acc); margin-bottom:10px; text-transform:uppercase; letter-spacing:1px; }}
            .ev-row {{ display:flex; gap:10px; font-size:14px; margin-bottom:8px; align-items:center; }}
            .ev-time {{ font-family:monospace; color:var(--dim); width:30px; }}
            .close-btn {{ width:100%; padding:15px; background:var(--border); color:var(--text); border:none; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <div class="logo-box">
                    <!-- New AI Football Logo -->
                    <svg class="logo-svg" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="5" fill="none"/>
                        <path d="M50 5 L50 95 M5 50 L95 50 M18 18 L82 82 M82 18 L18 82" stroke="currentColor" stroke-width="2" opacity="0.3"/>
                        <circle cx="50" cy="50" r="15" fill="currentColor"/>
                        <circle cx="50" cy="50" r="8" fill="#0f1218"/>
                    </svg>
                    <div class="site-title-box">
                        <div class="site-title-main">AI 足球</div>
                        <div class="site-title-sub">Global AI Football</div>
                    </div>
                </div>
                <div class="lang-box">
                    <div class="l-btn active" onclick="setL('sc',this)">简</div>
                    <div class="l-btn" onclick="setL('tc',this)">繁</div>
                    <div class="l-btn" onclick="setL('en',this)">EN</div>
                </div>
            </div>
            {filters}
            <div class="tabs">
                <div class="tab active" onclick="setTab('live',this)"><span class="lang" data-en="LIVE" data-tc="進行中" data-sc="进行中">进行中</span></div>
                <div class="tab" onclick="setTab('up',this)"><span class="lang" data-en="UPCOMING" data-tc="即將" data-sc="即将">即将</span></div>
                <div class="tab" onclick="setTab('fin',this)"><span class="lang" data-en="FINISHED" data-tc="完賽" data-sc="完赛">完赛</span></div>
                <div class="tab" onclick="setTab('std',this)"><span class="lang" data-en="TABLE" data-tc="積分" data-sc="积分">积分</span></div>
            </div>
            <div id="view-live" class="view-section grid">{render_section(live_list, True)}</div>
            <div id="view-up" class="view-section grid hidden">{render_section(up_list, False)}</div>
            <div id="view-fin" class="view-section grid hidden">{render_section(fin_list, False, True)}</div>
            <div id="view-std" class="view-section hidden">{std_html}</div>
            <div class="footer">
                Version: {DAEMON_VERSION}<br>
                Build: {BUILD_TIME}<br>
                Job: {final_json['meta']['job_id']}<br>
                Updated: {datetime.now().strftime('%H:%M:%S')}
            </div>
        </div>
        <div id="modal" class="modal" onclick="closeModal(event)">
            <div class="modal-content">
                <div id="m-body"></div>
                <button class="close-btn" onclick="document.getElementById('modal').style.display='none'">CLOSE</button>
            </div>
        </div>
        <script>
            // FORCE BUST: {datetime.now().timestamp()}
            const MATCH_DATA = {json.dumps({m['id']: m for m in json_data}, ensure_ascii=False)};
            let L = 'sc';
            
            function setL(l, btn) {{
                L = l;
                document.querySelectorAll('.l-btn').forEach(b=>b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.lang').forEach(el => {{
                    el.innerText = el.getAttribute('data-'+l) || el.innerText;
                }});
                updateModalLang();
            }}
            function f(code, btn) {{
                document.querySelectorAll('.f-btn').forEach(b=>b.classList.remove('active'));
                btn.classList.add('active');
                ['view-live', 'view-up', 'view-fin'].forEach(id => {{
                    document.getElementById(id).querySelectorAll('.card').forEach(c => {{
                        c.style.display = (code==='ALL' || c.dataset.lg===code) ? 'block' : 'none';
                    }});
                }});
            }}
            function setTab(v, btn) {{
                document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.view-section').forEach(d=>d.classList.add('hidden'));
                document.getElementById('view-'+v).classList.remove('hidden');
            }}
            
            let currentModalData = null;
            function openModal(id) {{
                try {{
                    const m = MATCH_DATA[id];
                    if(!m) {{ console.error("No data for ID", id); return; }}
                    
                    const evs = m.events || [];
                    const lines = m.lineups || {{home:[], away:[]}};
                    const refs = m.referees || [];
                    
                    currentModalData = {{ evs, lines, refs, status: m.statusRaw }};
                    renderModal();
                    document.getElementById('modal').style.display = 'flex';
                }} catch(e) {{ console.error(e); alert("Details Error"); }}
            }}
            
            function renderModal() {{
                if(!currentModalData) return;
                const {{ evs, lines, refs, status }} = currentModalData;
                let html = '';
                
                if(evs.length > 0) {{
                    html += '<div class="m-section"><div class="m-title">Events</div>';
                    evs.forEach(e => {{
                        html += `<div class="ev-row"><span class="ev-time">${{e.minute}}'</span><span>${{e.text[L] || e.text.en}}</span></div>`;
                    }});
                    html += '</div>';
                }}
                
                if(lines.home && lines.home.length > 0) {{
                    html += '<div class="m-section"><div class="m-title">Lineups</div>';
                    html += `<div style="display:flex;justify-content:space-between;font-size:12px;color:#999;margin-bottom:5px"><span>HOME</span><span>AWAY</span></div>`;
                    const max = Math.max(lines.home.length, lines.away.length);
                    for(let i=0; i<max; i++) {{
                        html += `<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                            <span>${{lines.home[i] || ''}}</span><span>${{lines.away[i] || ''}}</span>
                        </div>`;
                    }}
                    html += '</div>';
                }}
                
                if(refs.length > 0) {{
                    html += '<div class="m-section"><div class="m-title">Referees</div><div style="font-size:13px;color:#94a3b8">' + refs.join(', ') + '</div></div>';
                }}
                
                if(html === '') {{
                    if(['TIMED','SCHEDULED','UPCOMING'].includes(status)) {{
                        html = '<div style="text-align:center;padding:40px;color:#94a3b8"><div style="font-size:40px;margin-bottom:10px">⏳</div><div>比賽尚未開始<br><span style="font-size:12px;opacity:0.6">Match not started yet</span></div></div>';
                    }} else {{
                        html = '<div style="text-align:center;padding:40px;color:#94a3b8">暫無詳細數據<br><span style="font-size:12px;opacity:0.6">No details from source</span></div>';
                    }}
                }}
                document.getElementById('m-body').innerHTML = html;
            }}
            
            function updateModalLang() {{ if(document.getElementById('modal').style.display === 'flex') renderModal(); }}
            function closeModal(e) {{ if(e.target.id === 'modal') document.getElementById('modal').style.display = 'none'; }}
        </script>
    </body>
    </html>
    """
    push(html, PATH_INDEX)
    
    # T-101 Health Check
    try:
        push("<!DOCTYPE html><html><body>OK</body></html>", PATH_HEALTH)
    except: pass

if __name__ == "__main__":
    # print("Prod Daemon Starting...")
    run()
    while True:
        time.sleep(30)
        run()
