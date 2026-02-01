import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}

# Current Dictionary (Simplified for checking)
I18N = {
    "Manchester City": "曼城", "Liverpool": "利物浦", "Arsenal": "阿森納",
    "Real Madrid": "皇家馬德里", "Barcelona": "巴塞隆納", "Bayern Munich": "拜仁慕尼黑",
    "Inter": "國際米蘭", "Milan": "AC米蘭", "Juventus": "尤文圖斯",
    "Paris Saint-Germain": "巴黎聖日耳門", "Chelsea": "切爾西", "Man United": "曼聯",
    "Tottenham": "熱刺", "Newcastle United": "紐卡斯爾聯", "Newcastle": "紐卡斯爾聯",
    "Aston Villa": "阿斯頓維拉", "West Ham": "西漢姆聯", "Everton": "艾弗頓",
    "Wolves": "狼隊", "Wolverhampton": "狼隊", "Brighton": "布萊頓", "Fulham": "富勒姆",
    "Brentford": "布倫特福德", "Crystal Palace": "水晶宮", "Nottm Forest": "諾丁漢森林",
    "Bournemouth": "伯恩茅斯", "Luton": "卢顿", "Burnley": "伯恩利", "Sheff Utd": "謝菲爾德聯",
    "Ipswich": "伊普斯維奇", "Ipswich Town": "伊普斯維奇", "Leicester": "萊斯特城", "Leicester City": "萊斯特城",
    "Southampton": "南安普頓", "Leeds": "里茲聯", "Leeds United": "里茲聯",
    "Girona": "赫羅納", "Real Sociedad": "皇家社會", "Betis": "貝蒂斯",
    "Athletic": "畢爾包", "Athletic Club": "畢爾包", "Valencia": "瓦倫西亞",
    "Villarreal": "比利亚雷亚尔", "Sevilla": "塞維利亞", "Osasuna": "奧薩蘇納",
    "Getafe": "赫塔費", "Celta": "塞爾塔", "Mallorca": "馬略卡", "Rayo Vallecano": "巴列卡諾",
    "Las Palmas": "拉斯帕爾馬斯", "Alavés": "阿拉維斯", "Leganés": "雷加利斯",
    "Valladolid": "瓦拉多利德", "Espanyol": "西班牙人",
    "Napoli": "拿坡里", "Lazio": "拉齊奧", "Roma": "羅馬", "Atalanta": "亞特蘭大",
    "Bologna": "博洛尼亞", "Fiorentina": "佛羅倫薩", "Torino": "都靈", "Monza": "蒙扎",
    "Genoa": "熱那亞", "Udinese": "烏迪內斯", "Lecce": "萊切", "Empoli": "恩波利",
    "Verona": "維羅納", "Cagliari": "卡利亞里", "Parma": "帕爾馬", "Como": "科莫",
    "Venezia": "威尼斯", "Leverkusen": "勒沃庫森", "Dortmund": "多特蒙德", "Leipzig": "萊比錫",
    "Stuttgart": "斯圖加特", "Frankfurt": "法蘭克福", "Hoffenheim": "霍芬海姆",
    "Freiburg": "弗賴堡", "Heidenheim": "海登海姆", "Werder Bremen": "不萊梅",
    "Augsburg": "奧格斯堡", "Wolfsburg": "沃爾夫斯堡", "M'gladbach": "門興",
    "Union Berlin": "柏林聯", "Bochum": "波鴻", "Mainz": "美因茨", "St. Pauli": "聖保利",
    "Holstein Kiel": "基爾", "Lyon": "里昂", "Marseille": "馬賽", "Monaco": "摩納哥",
    "Brest": "布雷斯特", "Lille": "里爾", "Lens": "朗斯", "Rennes": "雷恩", "Nice": "尼斯",
    "Reims": "蘭斯", "Toulouse": "圖盧茲", "Montpellier": "蒙彼利埃", "Strasbourg": "斯特拉斯堡",
    "Nantes": "南特", "Le Havre": "勒阿弗爾", "Auxerre": "歐塞尔", "Angers": "昂熱",
    "Saint-Étienne": "聖埃蒂安", "Sporting CP": "葡萄牙體育", "Benfica": "本菲卡",
    "Porto": "波爾圖", "PSV": "PSV埃因霍溫", "Feyenoord": "費耶諾德", "Celtic": "凱爾特人",
    "Club Brugge": "布魯日", "Shakhtar": "礦工", "Salzburg": "薩爾茨堡", "Young Boys": "年輕人",
    "Sparta Praha": "布拉格斯巴達", "Sturm Graz": "格拉茨風暴", "Crvena Zvezda": "紅星",
    "Slovan Bratislava": "布拉提斯拉瓦", "Dinamo Zagreb": "薩格勒布戴拿模"
}

def check_missing():
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS)
        matches = r.json().get('matches', [])
    except:
        print("API Error")
        return

    missing = set()
    for m in matches:
        # Check Home
        h = m['homeTeam']['shortName'] or m['homeTeam']['name']
        if h not in I18N and h not in I18N.values():
            # Check partial
            found = False
            for k in I18N:
                if k in h: found = True; break
            if not found: missing.add(h)
            
        # Check Away
        a = m['awayTeam']['shortName'] or m['awayTeam']['name']
        if a not in I18N and a not in I18N.values():
            found = False
            for k in I18N:
                if k in a: found = True; break
            if not found: missing.add(a)
            
    print("Missing Translations:")
    for name in sorted(list(missing)):
        print(f"- {name}")

check_missing()
