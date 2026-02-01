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

# v55 MEGA DICTIONARY
I18N = {
    "teams": {
        # --- England ---
        "Man City": "曼城", "Manchester City": "曼城", "Liverpool": "利物浦", "Arsenal": "阿森納",
        "Chelsea": "切爾西", "Man United": "曼聯", "Tottenham": "熱刺", "Newcastle": "紐卡斯爾聯",
        "Aston Villa": "阿斯頓維拉", "West Ham": "西漢姆聯", "Everton": "艾弗頓", "Wolves": "狼隊",
        "Brighton": "布萊頓", "Fulham": "富勒姆", "Brentford": "布倫特福德", "Crystal Palace": "水晶宮",
        "Nottm Forest": "諾丁漢森林", "Nottingham": "諾丁漢森林", "Bournemouth": "伯恩茅斯",
        "Luton": "卢顿", "Burnley": "伯恩利", "Sheff Utd": "謝菲爾德聯", "Leeds": "里茲聯",
        "Leicester": "萊斯特城", "Southampton": "南安普頓", "Ipswich": "伊普斯維奇", "Norwich": "諾維奇",
        "West Brom": "西布朗", "Hull City": "赫爾城", "Coventry": "考文垂", "Preston": "普雷斯頓",
        "Middlesbrough": "米德尔斯堡", "Cardiff": "卡迪夫城", "Sunderland": "桑德蘭", "Bristol City": "布里斯托城",
        "Swansea": "斯旺西", "Watford": "沃特福德", "Millwall": "米爾沃爾", "Stoke": "斯托克城",
        "QPR": "女王公園巡遊者", "Blackburn": "布萊克本", "Plymouth": "普利茅斯", "Birmingham": "伯明翰",
        "Huddersfield": "哈德斯菲爾德", "Rotherham": "羅瑟勒姆", "Derby": "德比郡", "Portsmouth": "樸茨茅斯",
        "Bolton": "博爾頓", "Peterborough": "彼得堡聯", "Oxford Utd": "牛津聯", "Wrexham": "雷克斯漢姆",
        "AFC Wimbledon": "溫布頓", "Celtic": "凱爾特人", "Rangers": "流浪者", "Hibernian": "希伯尼安",
        "Aberdeen": "阿伯丁", "Hearts": "哈茨", "Dundee United": "登地聯", "Kilmarnock": "基爾馬諾克",
        "St. Mirren": "聖米倫", "Motherwell": "馬瑟韋爾", "Livingston": "利文斯頓", "Ross County": "羅斯郡",
        
        # --- Spain ---
        "Real Madrid": "皇家馬德里", "Barcelona": "巴塞隆納", "Barça": "巴塞隆納", "Girona": "赫羅納",
        "Atletico": "馬德里競技", "Atleti": "馬德里競技", "Athletic Club": "畢爾包", "Athletic": "畢爾包",
        "Real Sociedad": "皇家社會", "Betis": "貝蒂斯", "Valencia": "瓦倫西亞", "Villarreal": "比利亚雷亚尔",
        "Getafe": "赫塔費", "Las Palmas": "拉斯帕爾馬斯", "Alavés": "阿拉維斯", "Osasuna": "奧薩蘇納",
        "Rayo Vallecano": "巴列卡諾", "Mallorca": "馬略卡", "Sevilla": "塞維利亞", "Celta": "塞爾塔",
        "Cadiz": "加的斯", "Granada": "格拉納達", "Almeria": "阿爾梅里亞", "Almería": "阿爾梅里亞",
        "Leganés": "雷加利斯", "Espanyol": "西班牙人", "Valladolid": "瓦拉多利德", "Eibar": "埃瓦爾",
        "Sporting Gijon": "希洪體育", "Gijón": "希洪體育", "Real Oviedo": "奧維耶多", "Racing Santander": "桑坦德競技",
        "Santander": "桑坦德競技", "Elche": "埃爾切", "Levante": "萊萬特", "Burgos": "布爾戈斯",
        "Racing Ferrol": "費羅爾競技", "Tenerife": "特內里費", "Albacete": "阿爾瓦塞特", "Zaragoza": "薩拉戈薩",
        "Huesca": "韋斯卡", "Cartagena": "卡塔赫納", "Alcorcon": "阿爾科爾孔", "Andorra": "安道爾",
        "Castellón": "卡斯特利翁", "Eldense": "埃爾登塞", "Mirandes": "米蘭德斯", "Amorebieta": "阿莫雷比耶塔",
        "Cádiz CF": "加的斯", "Córdoba": "科爾多瓦",
        
        # --- Germany ---
        "Leverkusen": "勒沃庫森", "Bayern": "拜仁慕尼黑", "Bayern Munich": "拜仁慕尼黑", "Stuttgart": "斯圖加特",
        "Dortmund": "多特蒙德", "Leipzig": "萊比錫", "Frankfurt": "法蘭克福", "Hoffenheim": "霍芬海姆",
        "Freiburg": "弗賴堡", "Heidenheim": "海登海姆", "Augsburg": "奧格斯堡", "Werder": "不萊梅",
        "Wolfsburg": "沃爾夫斯堡", "Gladbach": "門興", "M'gladbach": "門興", "Union Berlin": "柏林聯",
        "Bochum": "波鴻", "Mainz": "美因茨", "Köln": "科隆", "Darmstadt": "達姆施塔特",
        "St. Pauli": "聖保利", "Holstein Kiel": "基爾", "Dusseldorf": "杜塞爾多夫", "Düsseldorf": "杜塞爾多夫",
        "HSV": "漢堡", "Hamburg": "漢堡", "Hannover": "漢諾威96", "Paderborn": "帕德博恩",
        "SC Paderborn": "帕德博恩", "Karlsruhe": "卡爾斯魯厄", "Hertha": "柏林赫塔", "Hertha BSC": "柏林赫塔",
        "Greuther Fürth": "菲爾特", "Elversberg": "埃爾弗斯貝格", "Magdeburg": "馬格德堡", "Nurnberg": "紐倫堡",
        "Schalke": "沙爾克04", "Kaiserslautern": "凱澤斯劳滕", "Wehen": "韋恩", "Rostock": "羅斯托克",
        "Braunschweig": "布倫瑞克", "Osnabrück": "奧斯納布呂克", "Duisburg": "杜伊斯堡",
        "Dynamo Dresden": "德累斯頓", "Bielefeld": "比勒費爾德", "SSV Ulm": "烏爾姆",
        "Regensburg": "雷根斯堡", "Münster": "明斯特", "RW Essen": "埃森", "Verl": "維爾",
        "Saarbrücken": "薩爾布呂肯", "1860 München": "慕尼黑1860", "Cottbus": "科特布斯",
        
        # --- Italy ---
        "Inter": "國際米蘭", "Milan": "AC米蘭", "Juventus": "尤文圖斯", "Bologna": "博洛尼亞",
        "Roma": "羅馬", "Atalanta": "亞特蘭大", "Napoli": "拿坡里", "Fiorentina": "佛羅倫薩",
        "Lazio": "拉齊奧", "Torino": "都靈", "Monza": "蒙扎", "Genoa": "熱那亞", "Lecce": "萊切",
        "Udinese": "烏迪內斯", "Empoli": "恩波利", "Verona": "維羅納", "Cagliari": "卡利亞里",
        "Frosinone": "弗羅西諾內", "Sassuolo": "薩索洛", "Salernitana": "薩勒尼塔納", "Parma": "帕爾馬",
        "Como": "科莫", "Como 1907": "科莫", "Venezia": "威尼斯", "Cremonese": "克雷莫納",
        "Catanzaro": "卡坦扎羅", "Palermo": "巴勒莫", "Sampdoria": "桑普多利亞", "Brescia": "布雷西亞",
        "Sudtirol": "南蒂羅爾", "Cittadella": "奇塔代拉", "Pisa": "比薩", "AC Pisa": "比薩",
        "Reggiana": "雷吉亞納", "Modena": "摩德納", "Cosenza": "科森扎", "Bari": "巴里",
        "Spezia": "斯佩齊亞", "Spezia Calcio": "斯佩齊亞", "Ascoli": "阿斯科利", "Ternana": "特爾納納",
        "Feralpisalo": "費拉爾皮沙洛", "Lecco": "萊科", "Juve Stabia": "斯塔比亞", "Mantova": "曼托瓦",
        "Cesena": "切塞納", "Carrarese": "卡拉雷塞", "Avellino": "阿韋利諾", "Padova": "帕多瓦",
        "Vicenza": "維琴察", "Triestina": "特里斯蒂納",
        
        # --- France ---
        "PSG": "巴黎聖日耳門", "Paris SG": "巴黎聖日耳門", "Monaco": "摩納哥", "Brest": "布雷斯特",
        "Lille": "里爾", "Nice": "尼斯", "Lens": "朗斯", "Marseille": "馬賽", "Lyon": "里昂",
        "Rennes": "雷恩", "Reims": "蘭斯", "Toulouse": "圖盧茲", "Strasbourg": "斯特拉斯堡",
        "Montpellier": "蒙彼利埃", "Nantes": "南特", "Le Havre": "勒阿弗爾", "Metz": "梅斯",
        "FC Metz": "梅斯", "Lorient": "洛里昂", "Clermont": "克萊蒙", "Auxerre": "歐塞尔",
        "Angers": "昂熱", "Angers SCO": "昂熱", "St Etienne": "聖埃蒂安", "Saint-Étienne": "聖埃蒂安",
        "Rodez": "羅德茲", "Paris FC": "巴黎FC", "Caen": "卡昂", "Laval": "拉瓦勒",
        "Guingamp": "甘岡", "Pau": "波城", "Grenoble": "格勒諾布爾", "Bastia": "巴斯蒂亞",
        "Amiens": "亞眠", "Ajaccio": "阿雅克肖", "Dunkerque": "登克爾克", "Bordeaux": "波爾多",
        "Annecy": "安錫", "Troyes": "特魯瓦", "Concarneau": "孔卡爾諾", "Quevilly": "克維伊",
        "Valenciennes": "瓦朗謝訥", "Red Star": "紅星", "Martigues": "馬提格",
        
        # --- Rest of World ---
        "Galatasaray": "加拉塔薩雷", "Fenerbahce": "費內巴切", "Besiktas": "貝西克塔斯",
        "Trabzonspor": "特拉布宗", "PSV": "PSV埃因霍溫", "Feyenoord": "費耶諾德", "Twente": "特溫特",
        "AZ": "阿爾克馬爾", "Ajax": "阿賈克斯", "NEC": "奈梅亨", "Utrecht": "烏德勒支",
        "Go Ahead": "前進之鷹", "Sparta": "斯巴達", "Excelsior": "埃克塞爾西奧", "Heerenveen": "海倫芬",
        "Zwolle": "茲沃勒", "Almere": "阿爾梅勒", "Vitesse": "維特斯", "Volendam": "沃倫丹",
        "Heracles": "赫拉克勒斯", "Waalwijk": "瓦爾韋克", "Sittard": "錫塔德", "Groningen": "格羅寧根",
        "Willem II": "威廉二世", "NAC Breda": "布雷達", "Roda": "羅達JC", "Dordrecht": "多德勒支",
        "ADO Den Haag": "海牙", "De Graafschap": "格拉夫夏普", "Emmen": "埃門", "Cambuur": "坎布爾",
        "Sporting CP": "葡萄牙體育", "Benfica": "本菲卡", "Porto": "波爾圖", "Braga": "布拉加",
        "Vitoria": "吉馬良斯", "Arouca": "阿羅卡", "Moreirense": "摩里倫斯", "Famalicao": "法馬利康",
        "Famalicão": "法馬利康", "Boavista": "博阿維斯塔", "Gil Vicente": "吉爾維森特",
        "Estoril": "埃斯托里爾", "Rio Ave": "里奧阿維", "Farense": "法倫斯", "Portimonense": "波爾蒂莫嫩塞",
        "Casa Pia": "卡薩皮亞", "Vizela": "維澤拉", "Chaves": "查維斯", "Estrela": "阿馬多拉之星",
        "Nacional": "國民隊", "CD Nacional": "國民隊", "Santa Clara": "聖克拉拉", "AVS": "阿維斯",
        "Tondela": "通德拉", "Maritimo": "馬里迪莫", "Feirense": "費倫斯", "Leiria": "萊里亞",
        "Young Boys": "年輕人", "Servette": "塞爾維特", "Lugano": "盧加諾", "Zurich": "蘇黎世",
        "FC Zürich": "蘇黎世", "Winterthur": "溫特圖爾", "St. Gallen": "聖加侖", "Luzern": "盧塞恩",
        "Lausanne": "洛桑", "Yverdon": "伊韋爾東", "Basel": "巴塞爾", "Grasshoppers": "草蜢",
        "Sion": "錫永", "Thun": "圖恩", "Aarau": "阿勞", "Vaduz": "瓦杜茲",
        "Salzburg": "薩爾茨堡", "Sturm Graz": "格拉茨風暴", "LASK": "林茨", "Rapid Wien": "維也納迅速",
        "Hartberg": "哈特貝格", "Klagenfurt": "克拉根福", "Wolfsberg": "沃爾夫斯貝格",
        "Austria Wien": "維也納奧地利", "BW Linz": "藍白林茨", "Altach": "阿爾塔赫",
        "Tirol": "提洛爾", "Lustenau": "盧斯特瑙", "GAK": "格拉茨AK", "Ried": "里德",
        "Shakhtar": "礦工", "Dynamo Kyiv": "基輔迪納摩", "Olympiacos": "奧林匹亞科斯",
        "PAOK": "PAOK薩洛尼卡", "AEK": "AEK雅典", "Panathinaikos": "帕納辛奈科斯",
        "Club Brugge": "布魯日", "Union SG": "聖吉羅斯", "Anderlecht": "安德萊赫特",
        "Antwerp": "安特衛普", "Genk": "亨克", "Gent": "根特", "Cercle Brugge": "色格拉布魯日",
        "Mechelen": "梅赫倫", "KV Mechelen": "梅赫倫", "St. Truiden": "聖圖爾登",
        "Standard Liège": "標準列日", "Charleroi": "夏勒羅伊", "Westerlo": "韋斯特洛",
        "Leuven": "魯汶", "OH Leuven": "魯汶", "Kortrijk": "科特賴克", "Eupen": "歐本",
        "RWDM": "莫倫貝克", "Beerschot": "比爾肖特", "Dender": "登德爾", "FCV Dender": "登德爾",
        "Copenhagen": "哥本哈根", "Midtjylland": "中日德蘭", "Brondby": "布隆德比",
        "Nordsjaelland": "北西蘭", "AGF": "奧胡斯", "Silkeborg": "席爾克堡", "Randers": "蘭德斯",
        "Viborg": "維堡", "Odense": "歐登塞", "Lyngby": "靈比", "Vejle": "維埃勒", "Hvidovre": "維兹奧勒",
        "Sonderjyske": "桑德捷斯基", "Aalborg": "奧爾堡", "Malmo": "馬爾默", "Elfsborg": "埃爾夫斯堡",
        "Hacken": "赫根", "Djurgarden": "尤爾加登", "Varnamo": "瓦納默", "Kalmar": "卡爾馬",
        "Hammarby": "哈馬比", "Sirius": "希里斯", "Norrkoping": "諾雪平", "Mjallby": "米亞爾比",
        "AIK": "AIK索爾納", "Halmstad": "哈爾姆斯塔德", "Goteborg": "哥德堡", "Brommapojkarna": "布洛馬波卡納",
        "Degerfors": "迪加史福斯", "Varbergs": "瓦爾貝里", "Vasteras": "韋斯特羅斯", "GAIS": "蓋斯",
        "Bodo/Glimt": "博多格林特", "Brann": "布蘭", "Tromso": "特羅姆瑟", "Viking": "維京",
        "Molde": "莫爾德", "Lillestrom": "利勒斯特羅姆", "Stromsgodset": "斯特羅姆加斯特",
        "Sarpsborg": "薩爾普斯堡", "Rosenborg": "羅森博格", "Odd": "奧德", "HamKam": "漢坎",
        "Haugesund": "海于格松", "Sandefjord": "桑德菲傑", "Valerenga": "瓦勒倫加",
        "Stabaek": "斯塔貝克", "Aalesund": "奧勒松", "Fredrikstad": "弗雷德里克斯塔", "KFUM": "KFUM奧斯陸",
        "Sparta Praha": "布拉格斯巴達", "Slavia Praha": "布拉格斯拉維亞", "Plzen": "比爾森",
        "Ferencvaros": "費倫茨瓦羅斯", "Paks": "保克什", "Paksi FC": "保克什",
        "Puskas": "普斯卡什", "Debrecen": "德布勒森", "Fehervar": "費赫瓦爾",
        "Diosgyor": "迪歐斯捷爾", "Diósgyőri": "迪歐斯捷爾", "MTK": "MTK布達佩斯",
        "Zalaegerszeg": "佐洛埃格塞格", "Kecskemet": "凱奇凱梅特", "Ujpest": "烏伊佩斯特",
        "Mezokovesd": "邁澤凱韋什德", "Kisvarda": "基斯瓦爾達", "Gyor": "傑爾", "ETO Győr": "傑爾",
        "Nyiregyhaza": "尼雷吉哈佐", "Dinamo Zagreb": "薩格勒布戴拿模", "Rijeka": "里耶卡",
        "Hajduk Split": "海杜克", "Osijek": "奧西耶克", "Lokomotiva": "薩格勒布火車頭",
        "Varazdin": "瓦拉日丁", "Gorica": "戈里察", "Istra 1961": "伊斯特拉",
        "Slaven Belupo": "斯拉文", "Rudes": "魯德斯", "Sibenik": "希貝尼克", "Zrinski": "茲林斯基",
        "Crvena Zvezda": "紅星", "Partizan": "游擊隊", "TSC": "托波拉", "Cukaricki": "切卡里基",
        "Vojvodina": "沃伊沃迪納", "Novi Pazar": "諾維帕扎爾", "Mladost": "盧卡尼", "Radnicki 1923": "拉德尼基",
        "Napredak": "納普里達克", "Spartak": "斯巴達克蘇博蒂察", "IMT": "IMT貝爾格萊德",
        "Javor": "伊萬尼察", "Zeleznicar": "潘切沃", "Vozdovac": "沃日多瓦茨", "Radnik": "蘇爾杜利察",
        "OFK Beograd": "OFK貝爾格萊德", "Jedinstvo": "烏布", "Tekstilac": "奧扎奇",
        "FCSB": "布加勒斯特星", "CFR Cluj": "克盧日", "Univ. Craiova": "克拉約瓦大學",
        "Farul": "法魯爾", "Sepsi": "聖喬治", "Rapid 1923": "布加勒斯特快速",
        "UTA Arad": "阿拉德", "Otelul": "加拉茨", "Hermannstadt": "赫曼施塔特",
        "U Cluj": "克盧日大學", "Petrolul": "普羅耶什蒂", "Poli Iasi": "雅西理工",
        "Dinamo": "布加勒斯特迪納摩", "Botosani": "博托沙尼", "Voluntari": "沃倫塔里",
        "FCU 1948": "克拉約瓦", "Unirea Slobozia": "斯洛博齊亞", "Gloria Buzau": "布澤烏",
        "Slobozia": "斯洛博齊亞", "Uni Craiova": "克拉約瓦大學", "FC Rapid": "布加勒斯特快速",
        "FC UTA Arad": "阿拉德", "FCU Cluj": "克盧日大學",
        "Galatasaray": "加拉塔薩雷", "Fenerbahce": "費內巴切", "Trabzonspor": "特拉布宗",
        "Besiktas": "貝西克塔斯", "Basaksehir": "巴薩克賽爾", "Kasimpasa": "卡斯帕薩",
        "Sivasspor": "錫瓦斯", "Alanyaspor": "阿拉尼亞", "Rizespor": "里澤",
        "Antalyaspor": "安塔利亞", "Gaziantep": "加濟安泰普", "Adana Demirspor": "阿達納",
        "Samsunspor": "薩姆松", "Kayserispor": "凱塞里", "Hatayspor": "哈塔伊",
        "Konyaspor": "科尼亞", "Ankaragucu": "安卡拉", "Karagumruk": "卡拉古拉克",
        "Pendikspor": "彭迪克", "Istanbulspor": "伊斯坦布爾", "Eyupspor": "埃於普",
        "Goztepe": "哥茲塔比", "Bodrum": "波德魯姆", "Gaziantep FK": "加濟安泰普",
        "Göztepe SK": "哥茲塔比", "Başakşehir": "巴薩克賽爾", "Karagümrük": "卡拉古拉克",
        # --- South America ---
        "River Plate": "河床", "Boca Juniors": "博卡青年", "Talleres": "塔勒瑞斯", "Estudiantes": "學生隊",
        "San Lorenzo": "聖洛倫索", "Racing Club": "競賽會", "Independiente": "獨立隊",
        "Velez": "薩斯菲爾德", "Vélez": "薩斯菲爾德", "Argentinos": "阿根廷青年", "Lanus": "拉努斯",
        "Defensa": "國防與司法", "Godoy Cruz": "戈多伊克魯斯", "Rosario": "羅薩里奧",
        "Newell's": "紐維爾老男孩", "Newell's OB": "紐維爾老男孩", "Belgrano": "貝爾格拉諾",
        "Instituto": "科爾多瓦", "Atletico Tucuman": "圖庫曼競技", "Tucumán": "圖庫曼競技",
        "Huracan": "颶風", "Huracán BA": "颶風", "Banfield": "班菲爾德", "Gimnasia": "體操擊劍",
        "Central Cordoba": "中央科爾多瓦", "Union": "聖塔菲聯", "Platense": "普拉滕斯",
        "Sarmiento": "薩米恩托", "Barracas": "巴拉卡斯", "Riestra": "列斯特拉", "CD Riestra": "列斯特拉",
        "Independiente Rivadavia": "里瓦達維亞獨立", "Flamengo": "弗拉門戈", "Palmeiras": "帕爾梅拉斯",
        "Botafogo": "博塔弗戈", "Atletico Mineiro": "米內羅競技", "Gremio": "格雷米奧",
        "Bragantino": "布拉甘蒂諾", "Fluminense": "弗魯米嫩塞", "Athletico Paranaense": "帕拉尼恩斯",
        "Internacional": "國際體育", "Fortaleza": "福塔雷薩", "Sao Paulo": "聖保羅",
        "Cuiaba": "庫亞巴", "Corinthians": "科林蒂安", "Cruzeiro": "克魯塞羅", "Vasco da Gama": "瓦斯科達伽馬",
        "Bahia": "巴伊亞", "Vitoria": "維多利亞", "Juventude": "尤文圖德", "Criciuma": "克里西烏馬",
        "Atletico Goianiense": "亞戈尼恩斯", "Santos": "桑托斯",
        "Colo Colo": "科洛科洛", "Colo-Colo": "科洛科洛", "Univ de Chile": "智利大學", "Palestino": "帕萊斯蒂諾",
        "Coquimbo": "科金博", "Coquimbo Unido": "科金博", "Everton CD": "埃弗頓(智)", "Union Espanola": "西班牙聯合",
        "Iquique": "伊基克", "Univ Catolica": "天主教大學", "Univ Católica": "天主教大學",
        "Huachipato": "瓦奇巴托", "Cobresal": "科布雷薩爾", "Audax Italiano": "奧達克斯",
        "O'Higgins": "奧伊金斯", "Nublense": "努布倫斯", "Union La Calera": "拉卡萊拉",
        "Cobreloa": "科布雷洛亞", "Copiapo": "科皮亞波", "Limache": "利馬切",
        "Rangers de Talca": "塔爾卡流浪者", "La Serena": "拉塞雷納", "Magallanes": "麥哲倫",
        "Santiago Wanderers": "聖地亞哥漫遊者", "Antofagasta": "安托法加斯塔", "Temuco": "泰莫庫",
        "San Luis": "聖路易斯", "Santa Cruz": "聖克魯斯", "Barnechea": "巴內切亞",
        "Univ de Concepcion": "康塞普西翁大學", "U Concepción": "康塞普西翁大學",
        "Recoleta": "雷科萊塔", "Santiago Morning": "聖地亞哥早晨", "Curico Unido": "庫里科",
        "Universitario": "大學隊", "Sporting Cristal": "水晶體育", "Cristal": "水晶體育",
        "Melgar": "梅爾加", "FBC Melgar": "梅爾加", "Alianza Lima": "利馬聯", "Cusco": "庫斯科",
        "ADT": "塔爾馬", "Asociación Deportiva Tarma": "塔爾馬", "Cienciano": "西恩夏諾",
        "Deportivo Garcilaso": "加西拉索", "Huancayo": "萬卡約", "Cesar Vallejo": "塞薩爾瓦列霍",
        "Chankas": "錢卡斯", "Los Chankas": "錢卡斯", "UTC": "卡哈馬卡", "FC Cajamarca": "卡哈馬卡",
        "Grau": "格勞競技", "Sport Boys": "體育男孩", "Mannucci": "曼努西", "Alianza Atletico": "阿里安薩",
        "Alianza Atl.": "阿里安薩", "Comerciantes Unidos": "商隊聯", "Union Comercio": "商業聯",
        "Club America": "美洲隊", "América": "美洲隊", "Cruz Azul": "藍十字", "Monterrey": "蒙特雷",
        "Tigres": "老虎隊", "Tigres UANL": "老虎隊", "Toluca": "托盧卡", "Chivas": "瓜達拉哈拉",
        "Guadalajara": "瓜達拉哈拉", "Pachuca": "帕丘卡", "Pumas": "普馬斯", "Pumas UNAM": "普馬斯",
        "Leon": "萊昂", "Club León": "萊昂", "Queretaro": "克雷塔羅", "Querétaro": "克雷塔羅",
        "Necaxa": "內卡哈", "Santos Laguna": "桑托斯拉古納", "Mazatlan": "馬薩特蘭", "Mazatlán": "馬薩特蘭",
        "Tijuana": "蒂華納", "Club Tijuana": "蒂華納", "Atlas": "阿特拉斯", "Juarez": "華雷斯",
        "Juárez": "華雷斯", "San Luis": "聖路易斯", "Puebla": "普埃布拉",
        # --- Australia ---
        "Melbourne City": "墨爾本城", "Central Coast": "中央海岸", "CC Mariners": "中央海岸",
        "Adelaide United": "阿德萊德聯", "Wellington Phoenix": "威靈頓鳳凰", "Sydney FC": "雪梨FC",
        "WS Wanderers": "西雪梨流浪者", "Melbourne Victory": "墨爾本勝利", "Melb Victory": "墨爾本勝利",
        "Macarthur": "麥克阿瑟", "Western United": "西部聯", "Perth Glory": "柏斯光榮",
        "Brisbane Roar": "布里斯班獅吼", "Newcastle Jets": "紐卡斯爾噴氣機", "Auckland FC": "奧克蘭FC"
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
