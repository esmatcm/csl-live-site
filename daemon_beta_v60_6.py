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

PATH_HTML = "/www/wwwroot/hsapi.xyz/full.html"
PATH_HTML_TYPO = "/www/wwwroot/hsapi.xyz/bata.html"
PATH_DATA = "/www/wwwroot/hsapi.xyz/data_v60.json"

# --- I18N DATA ---
# This is the "Master Dictionary"
I18N_TC = {
    # Top Teams
    "Man City": "曼城", "Manchester City": "曼城", "Liverpool": "利物浦", "Arsenal": "阿森納",
    "Chelsea": "切爾西", "Man United": "曼聯", "Manchester United": "曼聯", "Tottenham": "熱刺", "Tottenham Hotspur": "熱刺",
    "Newcastle": "紐卡斯爾聯", "Newcastle United": "紐卡斯爾聯", "Aston Villa": "阿斯頓維拉",
    "West Ham": "西漢姆聯", "Everton": "艾弗頓", "Wolves": "狼隊", "Wolverhampton": "狼隊",
    "Brighton": "布萊頓", "Fulham": "富勒姆", "Brentford": "布倫特福德", "Crystal Palace": "水晶宮",
    "Nottm Forest": "諾丁漢森林", "Nottingham": "諾丁漢森林", "Bournemouth": "伯恩茅斯", "Luton": "卢顿",
    "Burnley": "伯恩利", "Sheff Utd": "謝菲爾德聯", "Sheffield United": "謝菲爾德聯", "Sheffield Wed": "謝菲爾德星期三",
    "Leeds": "里茲聯", "Leicester": "萊斯特城", "Southampton": "南安普頓", "Ipswich": "伊普斯維奇",
    "Norwich": "諾維奇", "West Brom": "西布朗", "Hull": "赫爾城", "Hull City": "赫爾城", "Coventry": "考文垂",
    "Preston": "普雷斯頓", "Middlesbrough": "米德尔斯堡", "Cardiff": "卡迪夫城", "Sunderland": "桑德蘭",
    "Bristol City": "布里斯托城", "Swansea": "斯旺西", "Watford": "沃特福德", "Millwall": "米爾沃爾",
    "Stoke": "斯托克城", "QPR": "女王公園巡遊者", "Blackburn": "布萊克本", "Plymouth": "普利茅斯",
    "Birmingham": "伯明翰", "Huddersfield": "哈德斯菲爾德", "Rotherham": "羅瑟勒姆", "Derby": "德比郡",
    "Portsmouth": "樸茨茅斯", "Bolton": "博爾頓", "Peterborough": "彼得堡聯", "Oxford": "牛津聯",
    
    # Spain
    "Real Madrid": "皇家馬德里", "Barcelona": "巴塞隆納", "Barça": "巴塞隆納", "Girona": "赫羅納",
    "Atletico": "馬德里競技", "Atleti": "馬德里競技", "Athletic Club": "畢爾包", "Athletic": "畢爾包",
    "Real Sociedad": "皇家社會", "Betis": "貝蒂斯", "Valencia": "瓦倫西亞", "Villarreal": "比利亚雷亚尔",
    "Getafe": "赫塔費", "Las Palmas": "拉斯帕爾馬斯", "Alavés": "阿拉維斯", "Osasuna": "奧薩蘇納",
    "Rayo Vallecano": "巴列卡諾", "Mallorca": "馬略卡", "Sevilla": "塞維利亞", "Celta": "塞爾塔",
    "Cadiz": "加的斯", "Granada": "格拉納達", "Almeria": "阿爾梅里亞", "Leganés": "雷加利斯",
    "Espanyol": "西班牙人", "Valladolid": "瓦拉多利德", "Eibar": "埃瓦爾", "Sporting Gijon": "希洪體育",
    "Real Oviedo": "奧維耶多", "Racing Santander": "桑坦德競技", "Elche": "埃爾切", "Levante": "萊萬特",
    "Burgos": "布爾戈斯", "Racing Ferrol": "費羅爾競技", "Tenerife": "特內里費", "Albacete": "阿爾瓦塞特",
    "Zaragoza": "薩拉戈薩", "Huesca": "韋斯卡", "Cartagena": "卡塔赫納", "Alcorcon": "阿爾科爾孔",
    "Andorra": "安道爾", "Castellon": "卡斯特利翁", "Eldense": "埃爾登塞",
    
    # Germany
    "Leverkusen": "勒沃庫森", "Bayern": "拜仁慕尼黑", "Bayern Munich": "拜仁慕尼黑", "Stuttgart": "斯圖加特",
    "Dortmund": "多特蒙德", "Leipzig": "萊比錫", "Frankfurt": "法蘭克福", "Hoffenheim": "霍芬海姆",
    "Freiburg": "弗賴堡", "Heidenheim": "海登海姆", "Augsburg": "奧格斯堡", "Werder": "不萊梅",
    "Wolfsburg": "沃爾夫斯堡", "Gladbach": "門興", "M'gladbach": "門興", "Union Berlin": "柏林聯",
    "Bochum": "波鴻", "Mainz": "美因茨", "Köln": "科隆", "Darmstadt": "達姆施塔特",
    "St. Pauli": "聖保利", "Holstein Kiel": "基爾", "Dusseldorf": "杜塞爾多夫", "HSV": "漢堡",
    "Hamburg": "漢堡", "Hannover": "漢諾威96", "Paderborn": "帕德博恩", "Karlsruhe": "卡爾斯魯厄",
    "Hertha": "柏林赫塔", "Greuther Fürth": "菲爾特", "Elversberg": "埃爾弗斯貝格", "Magdeburg": "馬格德堡",
    "Nurnberg": "紐倫堡", "Schalke": "沙爾克04", "Kaiserslautern": "凱澤斯劳滕",
    
    # Italy
    "Inter": "國際米蘭", "Milan": "AC米蘭", "Juventus": "尤文圖斯", "Bologna": "博洛尼亞",
    "Roma": "羅馬", "Atalanta": "亞特蘭大", "Napoli": "拿坡里", "Fiorentina": "佛羅倫薩",
    "Lazio": "拉齊奧", "Torino": "都靈", "Monza": "蒙扎", "Genoa": "熱那亞", "Lecce": "萊切",
    "Udinese": "烏迪內斯", "Empoli": "恩波利", "Verona": "維羅納", "Cagliari": "卡利亞里",
    "Frosinone": "弗羅西諾內", "Sassuolo": "薩索洛", "Salernitana": "薩勒尼塔納", "Parma": "帕爾馬",
    "Como": "科莫", "Venezia": "威尼斯", "Cremonese": "克雷莫納", "Catanzaro": "卡坦扎羅",
    "Palermo": "巴勒莫", "Sampdoria": "桑普多利亞", "Brescia": "布雷西亞", "Sudtirol": "南蒂羅爾",
    "Cittadella": "奇塔代拉", "Pisa": "比薩", "AC Pisa": "比薩", "Reggiana": "雷吉亞納",
    "Modena": "摩德納", "Cosenza": "科森扎", "Bari": "巴里", "Spezia": "斯佩齊亞",
    
    # France
    "PSG": "巴黎聖日耳門", "Paris SG": "巴黎聖日耳門", "Monaco": "摩納哥", "Brest": "布雷斯特",
    "Lille": "里爾", "Nice": "尼斯", "Lens": "朗斯", "Marseille": "馬賽", "Lyon": "里昂",
    "Rennes": "雷恩", "Reims": "蘭斯", "Toulouse": "圖盧茲", "Strasbourg": "斯特拉斯堡",
    "Montpellier": "蒙彼利埃", "Nantes": "南特", "Le Havre": "勒阿弗爾", "Metz": "梅斯",
    "Lorient": "洛里昂", "Clermont": "克萊蒙", "Auxerre": "歐塞尔", "Angers": "昂熱",
    "St Etienne": "聖埃蒂安", "Saint-Étienne": "聖埃蒂安", "Rodez": "羅德茲", "Paris FC": "巴黎FC",
    "Caen": "卡昂", "Laval": "拉瓦勒", "Guingamp": "甘岡", "Pau": "波城", "Grenoble": "格勒諾布爾",
    "Bastia": "巴斯蒂亞", "Amiens": "亞眠", "Ajaccio": "阿雅克肖", "Dunkerque": "登克爾克",
    "Bordeaux": "波爾多", "Annecy": "安錫", "Troyes": "特魯瓦",
    
    # Other
    "Sporting CP": "葡萄牙體育", "Benfica": "本菲卡", "Porto": "波爾圖", "Ajax": "阿賈克斯",
    "PSV": "PSV埃因霍溫", "Feyenoord": "費耶諾德", "Galatasaray": "加拉塔薩雷", "Fenerbahce": "費內巴切",
    "Besiktas": "貝西克塔斯", "Celtic": "凱爾特人", "Rangers": "流浪者"
}

I18N_SC = {
    # Basic Mapping
    "阿森納": "阿森纳", "貝蒂斯": "贝蒂斯", "瓦倫西亞": "瓦伦西亚", "塞維利亞": "塞维利亚",
    "勒沃庫森": "勒沃库森", "拜仁慕尼黑": "拜仁慕尼黑", "多特蒙德": "多特蒙德", "萊比錫": "莱比锡",
    "國際米蘭": "国际米兰", "AC米蘭": "AC米兰", "尤文圖斯": "尤文图斯", "博洛尼亞": "博洛尼亚",
    "羅馬": "罗马", "亞特蘭大": "亚特兰大", "拿坡里": "那不勒斯", "拉齊奧": "拉齐奥",
    "巴黎聖日耳門": "巴黎圣日耳曼", "摩納哥": "摩纳哥", "布雷斯特": "布雷斯特", "里爾": "里尔",
    "尼斯": "尼斯", "朗斯": "朗斯", "馬賽": "马赛", "里昂": "里昂", "葡萄牙體育": "葡萄牙体育",
    "本菲卡": "本菲卡", "波爾圖": "波尔图", "阿賈克斯": "阿贾克斯", "PSV埃因霍溫": "PSV埃因霍温",
    "費耶諾德": "费耶诺德", "加拉塔薩雷": "加拉塔萨雷", "費內巴切": "费内巴切", "貝西克塔斯": "贝西克塔斯",
    "紐卡斯爾聯": "纽卡斯尔联", "謝菲爾德聯": "谢菲尔德联", "諾丁漢森林": "诺丁汉森林",
    "凱澤斯劳滕": "凯泽斯劳滕", "漢諾威96": "汉诺威96", "紐倫堡": "纽伦堡", "奧斯納布呂克": "奥斯纳布吕克",
    "布倫瑞克": "布伦瑞克", "羅斯托克": "罗斯托克", "沙爾克04": "沙尔克04",
    "薩勒尼塔納": "萨勒尼塔纳", "弗羅西諾內": "弗罗西诺内", "薩索洛": "萨索洛", "克雷莫納": "克雷莫纳",
    "桑普多利亞": "桑普多利亚", "南蒂羅爾": "南蒂罗尔", "斯佩齊亞": "斯佩齐亚"
}

def get_trilingual(text_en):
    if not text_en: return {"en": "", "tc": "", "sc": ""}
    
    # Normalize: Remove FC, AFC, etc for matching
    clean_text = text_en.replace(" FC", "").replace(" AFC", "").replace(" CF", "").strip()
    
    tc = text_en # Default
    
    # 1. Exact Match
    if text_en in I18N_TC: 
        tc = I18N_TC[text_en]
    elif clean_text in I18N_TC:
        tc = I18N_TC[clean_text]
    else:
        # 2. Partial Match (Search dictionary keys IN name, or name IN dictionary keys)
        for k, v in I18N_TC.items():
            if k in text_en: 
                tc = v; break
    
    # 3. SC
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
    # Fetch Data
    today = datetime.now()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (today + timedelta(days=2)).strftime('%Y-%m-%d')
    url = f"{BASE_URL}/matches?dateFrom={yesterday}&dateTo={tomorrow}"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        matches = r.json().get('matches', [])
    except: return

    data_out = []
    
    for m in matches:
        # STRICT FILTER (v61 Logic)
        code = m['competition']['code']
        if code not in ['PL', 'PD', 'SA', 'BL1', 'FL1', 'CL']: continue

        mid = m['id']
        status = m['status']
        
        events = []
        lineups = {"home": [], "away": [], "bench_home": [], "bench_away": []}
        referees = []
        coach = {"home": "", "away": ""}

        # Tier 3 Details
        if status in ['IN_PLAY', 'PAUSED', 'FINISHED']:
            details = fetch_match_details(mid)
            if details:
                # Events
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
                
                # Lineups
                for p in details.get('homeTeam', {}).get('lineup', []):
                    lineups['home'].append(p['name'])
                for p in details.get('awayTeam', {}).get('lineup', []):
                    lineups['away'].append(p['name'])
                
                # Referees
                for r in details.get('referees', []):
                    referees.append(r['name'])

        # Time UTC+9
        utc_dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        local_dt = utc_dt + timedelta(hours=9)
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
            "coach": coach
        }
        data_out.append(item)

    # Force Inject Dummy if No LIVE matches (USER REQUEST)
    has_live = any(x['statusRaw'] in ['IN_PLAY', 'PAUSED'] for x in data_out)
    if not has_live:
        dummy = {
            "id": 888888,
            "league": {"en": "Premier League", "tc": "英超", "sc": "英超"},
            "home": {"en": "Man City", "tc": "曼城", "sc": "曼城"},
            "away": {"en": "Liverpool", "tc": "利物浦", "sc": "利物浦"},
            "homeLogo": "https://crests.football-data.org/65.png",
            "awayLogo": "https://crests.football-data.org/64.png",
            "score": "2-2",
            "status": {"en": "LIVE", "tc": "進行中", "sc": "进行中"},
            "statusRaw": "IN_PLAY",
            "time": "NOW",
            "date": "02/01",
            "events": [
                {"minute": 88, "type": "goal", "text": {"en": "Goal: Haaland", "tc": "進球: 哈蘭德", "sc": "进球: 哈兰德"}},
                {"minute": 45, "type": "card", "card": "yellow", "text": {"en": "Yellow: Rodri", "tc": "黃牌: 羅德里", "sc": "黄牌: 罗德里"}}
            ],
            "lineups": {"home": ["Ederson", "Walker"], "away": ["Alisson", "Salah"]},
            "referees": ["Michael Oliver"],
            "coach": {"home": "Pep", "away": "Klopp"}
        }
        data_out.insert(0, dummy)

    push(json.dumps(data_out, ensure_ascii=False), PATH_DATA)
    
    try:
        with open('csl-live-site/index_quantum_fixed.html', 'r', encoding='utf-8') as f:
            html = f.read()
        push(html, PATH_HTML)
        push(html, PATH_HTML_TYPO)
    except: pass

if __name__ == "__main__":
    run()
    while True:
        time.sleep(30)
        run()
