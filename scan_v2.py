import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}

# Current Dictionary (From v54.1)
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
    }
}

def check():
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS)
        matches = r.json().get('matches', [])
    except: return

    missing = set()
    for m in matches:
        h = m['homeTeam']['shortName'] or m['homeTeam']['name']
        a = m['awayTeam']['shortName'] or m['awayTeam']['name']
        
        # Check Home
        if h not in I18N['teams']:
            found = False
            for k in I18N['teams']:
                if k in h: found = True; break
            if not found: missing.add(h)
            
        # Check Away
        if a not in I18N['teams']:
            found = False
            for k in I18N['teams']:
                if k in a: found = True; break
            if not found: missing.add(a)
            
    print("Missing:")
    for m in sorted(list(missing)):
        print(f'"{m}": "",')

check()
