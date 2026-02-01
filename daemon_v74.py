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

PATH_DATA = "/www/wwwroot/hsapi.xyz/data.json"

# --- CONFIG ---
ALLOWED = ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']
LEAGUE_PRIORITY = {'PL':1, 'PD':2, 'SA':3, 'BL1':4, 'FL1':5, 'CL':0}

# --- I18N (Full Dictionary) ---
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
    "Zhibo8": "直播吧", "88Kanqiu": "88看球"
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
    "紐卡斯爾聯": "纽卡斯尔联", "謝菲爾德聯": "谢菲尔德联", "諾丁漢森林": "诺丁汉森林",
    "凱澤斯劳滕": "凯泽斯劳滕", "漢諾威96": "汉诺威96", "紐倫堡": "纽伦堡", "奧斯納布呂克": "奥斯纳布吕克",
    "布倫瑞克": "布伦瑞克", "羅斯托克": "罗斯托克", "沙爾克04": "沙尔克04",
    "薩勒尼塔納": "萨勒尼塔纳", "弗羅西諾內": "弗罗西诺内", "薩索洛": "萨索洛", "克雷莫納": "克雷莫纳",
    "桑普多利亞": "桑普多利亚", "南蒂羅爾": "南蒂罗尔", "斯佩齊亞": "斯佩齐亚",
    "直播吧": "直播8", "Google搜尋": "Google搜索"
}

# CACHE
DATA_CACHE = {"standings": {}, "last_slow": 0}

def get_trilingual(text_en):
    if not text_en: return {"en": "", "tc": "", "sc": ""}
    clean = text_en.replace(" FC", "").replace(" AFC", "").replace(" CF", "").strip()
    tc = text_en
    if text_en in I18N_TC: tc = I18N_TC[text_en]
    elif clean in I18N_TC: tc = I18N_TC[clean]
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

def fetch_standings():
    st_data = {}
    print("Fetching Standings...")
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = requests.get(f"{BASE_URL}/competitions/{code}/standings", headers=HEADERS, timeout=5)
            if r.status_code == 200:
                table = []
                for row in r.json()['standings'][0]['table'][:15]: # Top 15
                    team_name = row['team']['shortName'] or row['team']['name']
                    table.append({
                        "pos": row['position'],
                        "team": get_trilingual(team_name),
                        "played": row['playedGames'],
                        "points": row['points'],
                        "crest": row['team']['crest']
                    })
                st_data[code] = table
                time.sleep(1) 
        except: pass
    return st_data

def run():
    # 1. Fetch Matches (Range: Past 7 Days -> Future 7 Days)
    # WIDER RANGE to ensure data is never empty
    today = datetime.now()
    past_days = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    future_days = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        r = requests.get(f"{BASE_URL}/matches?dateFrom={past_days}&dateTo={future_days}", headers=HEADERS, timeout=15)
        matches = r.json().get('matches', [])
    except Exception as e:
        print(f"Match Fetch Error: {e}")
        return # STOP HERE. Do NOT push empty data.

    # SAFETY LOCK: If API returns empty list (but no error), double check before pushing
    # Or just push, because maybe there really are no matches?
    # No, with 14 days window, impossible to have 0 matches in Top 5 leagues.
    if len(matches) == 0:
        print("API returned 0 matches. Aborting push to protect data.")
        return

    # 2. Fetch Standings (Force if empty)
    if not DATA_CACHE.get('standings') or time.time() - DATA_CACHE.get('last_slow', 0) > 3600:
        new_st = fetch_standings()
        if new_st:
            DATA_CACHE['standings'] = new_st
            DATA_CACHE['last_slow'] = time.time()

    data_all = []
    
    for m in matches:
        code = m['competition']['code']
        # Filter: Only Top 5 + CL
        if code not in ALLOWED: continue

        status = m['status']
        mid = m['id']
        
        events, lineups, referees, coach = [], {"home":[], "away":[]}, [], {}

        # Basic Fields
        home_tri = get_trilingual(m['homeTeam']['shortName'] or m['homeTeam']['name'])
        away_tri = get_trilingual(m['awayTeam']['shortName'] or m['awayTeam']['name'])
        lg_tri = get_trilingual(m['competition']['name'])
        
        # Time UTC+9
        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        bj_dt = utc_dt + timedelta(hours=9)
        time_str = bj_dt.strftime('%H:%M')
        date_str = bj_dt.strftime('%m/%d')
        
        # Status Map
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

        # Item Construction
        item = {
            "id": m['id'], "league": lg_tri, "code": code,
            "priority": LEAGUE_PRIORITY.get(code, 99),
            "home": home_tri, "away": away_tri,
            "homeLogo": m['homeTeam']['crest'], "awayLogo": m['awayTeam']['crest'],
            "score": f"{m['score']['fullTime']['home'] or 0}-{m['score']['fullTime']['away'] or 0}",
            "status": st_obj, "statusRaw": status,
            "time": time_str, "date": date_str,
            "events": events, "lineups": lineups, "referees": referees,
            "streams": []
        }
        
        # Streams
        if status in ['IN_PLAY', 'TIMED', 'SCHEDULED']:
            item['streams'] = [
                {"name": {"en": "Zhibo8", "tc": "直播吧", "sc": "直播吧"}, "url": f"https://www.zhibo8.com/search/?k={item['home']['sc']}"},
                {"name": {"en": "88Kanqiu", "tc": "88看球", "sc": "88看球"}, "url": f"http://www.88kanqiu.one"},
                {"name": {"en": "Google", "tc": "Google", "sc": "Google"}, "url": f"https://www.google.com/search?q={item['home']['tc']}+直播"}
            ]

        data_all.append(item)

    # FINAL CHECK: If data_all is empty (all filtered out?), abort.
    if len(data_all) == 0:
        print("Filtered data is empty. Aborting.")
        with open('csl-live-site/daemon_status.txt', 'w') as f:
            f.write(f"Last Run: {datetime.now()}\nStatus: EMPTY_DATA_ABORT\nMatches: 0\nStandings: {len(DATA_CACHE['standings'])}")
        return

    # Construct Final JSON
    final_json = {
        "matches": data_all,
        "standings": DATA_CACHE['standings']
    }

    # PUSH SAFE
    push(json.dumps(final_json, ensure_ascii=False), PATH_DATA)
    print(f"Pushed {len(data_all)} matches.")
    
    with open('csl-live-site/daemon_status.txt', 'w') as f:
        f.write(f"Last Run: {datetime.now()}\nStatus: SUCCESS\nMatches: {len(data_all)}\nStandings: {len(DATA_CACHE['standings'])}")

if __name__ == "__main__":
    run()
    while True:
        time.sleep(30)
        run()
