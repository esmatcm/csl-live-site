import requests
import json
import os
import re
import sys
import base64
from datetime import datetime
import pytz

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {'X-Auth-Token': API_KEY}
TAIPEI_TZ = pytz.timezone('Asia/Taipei')

# 擴充翻譯字典
I18N = {
    "status": {
        "IN_PLAY": "進行中", "PAUSED": "中場休息", "HT": "半場", "FT": "完賽",
        "FINISHED": "已完賽", "SCHEDULED": "未開賽", "TIMED": "已排程",
        "POSTPONED": "推遲", "CANCELLED": "取消", "SUSPENDED": "中斷"
    },
    "teams": {
        "Manchester City FC": "曼城", "Liverpool FC": "利物浦", "Arsenal FC": "阿森納",
        "Real Madrid CF": "皇家馬德里", "FC Barcelona": "巴塞隆納", "FC Bayern München": "拜仁慕尼黑",
        "Inter Milan": "國際米蘭", "Aston Villa FC": "阿斯頓維拉", "Tottenham Hotspur FC": "熱刺",
        "Manchester United FC": "曼聯", "Newcastle United FC": "紐卡斯爾聯", "Chelsea FC": "切爾西",
        "Bayer 04 Leverkusen": "勒沃庫森", "Paris Saint-Germain FC": "巴黎聖日耳門",
        "Juventus FC": "尤文圖斯", "AC Milan": "AC米蘭", "Atlético de Madrid": "馬德里競技",
        "Borussia Dortmund": "多特蒙德", "RB Leipzig": "萊比錫", "VfB Stuttgart": "斯圖加特",
        "Girona FC": "赫羅納", "Athletic Club": "畢爾包競技", "Real Sociedad de Fútbol": "皇家社會",
        "Real Betis Balompié": "皇家貝提斯", "Valencia CF": "巴倫西亞", "AS Roma": "羅馬",
        "Atalanta BC": "亞特蘭大", "SS Lazio": "拉齊奧", "Bologna FC 1909": "博洛尼亞",
        "SSC Napoli": "拿坡里", "Fiorentina": "佛羅倫薩", "Torino FC": "都靈",
        "AS Monaco FC": "摩納哥", "LOSC Lille": "里爾", "Stade Brestois 29": "布雷斯特",
        "OGC Nice": "尼斯", "Olympique Lyonnais": "里昂", "Olympique de Marseille": "馬賽",
        "Brighton & Hove Albion FC": "布萊頓", "West Ham United FC": "西漢姆聯",
        "Wolverhampton Wanderers FC": "狼隊", "AFC Bournemouth": "伯恩茅斯", "Fulham FC": "富勒姆",
        "Crystal Palace FC": "水晶宮", "Brentford FC": "布倫特福德", "Everton FC": "埃弗頓",
        "Nottingham Forest FC": "諾丁漢森林", "Luton Town FC": "盧頓", "Burnley FC": "伯恩利",
        "Sheffield United FC": "謝菲爾德聯"
    }
}

def translate(cat, key):
    return I18N.get(cat, {}).get(key, key)

def get_image_base64(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            b64 = base64.b64encode(r.content).decode('utf-8')
            return f"data:image/jpeg;base64,{b64}"
    except: pass
    return "https://via.placeholder.com/80?text=CSL"

def fetch_data():
    print("Fetching Matches...")
    live = []
    upcoming = []
    standings = {}

    # Live & Upcoming
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        data = r.json()
        for m in data.get('matches', []):
            item = {
                "id": m['id'],
                "league": m['competition']['name'],
                "home": translate('teams', m['homeTeam']['name']),
                "away": translate('teams', m['awayTeam']['name']),
                "homeLogo": m['homeTeam']['crest'],
                "awayLogo": m['awayTeam']['crest'],
                "score": f"{m['score']['fullTime']['home'] or 0} - {m['score']['fullTime']['away'] or 0}",
                "status": translate('status', m['status']),
                "utcDate": m['utcDate'],
                "venue": m.get('venue', '未提供')
            }
            if m['status'] in ['IN_PLAY', 'PAUSED']: live.append(item)
            else: upcoming.append(item)
    except Exception as e: print(f"Match Error: {e}")

    # Standings
    print("Fetching Standings...")
    for code in ['PL', 'PD', 'SA', 'BL1', 'FL1']:
        try:
            r = requests.get(f"{BASE_URL}/competitions/{code}/standings", headers=HEADERS, timeout=10)
            data = r.json()
            table = []
            for row in data['standings'][0]['table'][:10]: # Top 10
                table.append({
                    "pos": row['position'],
                    "team": translate('teams', row['team']['name']),
                    "played": row['playedGames'],
                    "points": row['points'],
                    "crest": row['team']['crest']
                })
            standings[code] = table
        except: pass

    # News (Dongqiudi)
    print("Fetching News...")
    news = []
    try:
        dqd_url = "https://api.dongqiudi.com/app/tabs/iphone/1.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(dqd_url, headers=headers, timeout=10)
        data = r.json()
        count = 0
        for article in data.get('articles', []):
            if count >= 8: break
            if 'thumb' in article and article['thumb']:
                img_src = get_image_base64(article['thumb'])
                news.append({
                    "id": count,
                    "title": article['title'],
                    "img": img_src,
                    "url": article['share'] if 'share' in article else f"https://m.dongqiudi.com/article/{article['id']}.html"
                })
                count += 1
    except: pass

    return live, upcoming, news, standings

def generate_html(live, upcoming, news, standings):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M')
    
    # 測試賽
    live.insert(0, {
        "id": 999999, "league": "系統測試賽", "home": "阿森納", "away": "曼城",
        "homeLogo": "https://crests.football-data.org/57.png", "awayLogo": "https://crests.football-data.org/65.png",
        "score": "2 - 1", "status": "進行中", "utcDate": datetime.now(TAIPEI_TZ).isoformat(), "venue": "酋長球場"
    })

    # Standings HTML
    standings_html = ""
    for league, table in standings.items():
        rows = "".join([f"<tr><td>{t['pos']}</td><td><img src='{t['crest']}' width='20'> {t['team']}</td><td>{t['played']}</td><td><strong>{t['points']}</strong></td></tr>" for t in table])
        standings_html += f"<div class='card'><h3>{league} 積分榜</h3><table><thead><tr><th>#</th><th>球隊</th><th>賽</th><th>分</th></tr></thead><tbody>{rows}</tbody></table></div>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSL PRO</title>
    <style>
        body {{ background: #05070a; color: #e2e8f0; font-family: sans-serif; margin: 0; padding: 0; }}
        .nav {{ background: #0f172a; padding: 15px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; }}
        .card {{ background: #0f172a; border: 1px solid #1e293b; margin: 10px; padding: 15px; border-radius: 12px; }}
        .live {{ border-color: #22c55e; }}
        .score {{ font-size: 24px; font-weight: bold; color: #22c55e; text-align: center; margin: 10px 0; }}
        .row {{ display: flex; justify-content: space-between; align-items: center; }}
        .news-item {{ display: flex; gap: 10px; margin-bottom: 10px; cursor: pointer; }}
        .news-img {{ width: 80px; height: 60px; object-fit: cover; border-radius: 8px; }}
        .footer {{ text-align: center; padding: 20px; color: #64748b; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        td, th {{ padding: 8px; text-align: left; border-bottom: 1px solid #1e293b; }}
        img {{ vertical-align: middle; }}
    </style>
</head>
<body>
    <div class="nav">
        <div style="font-weight:bold; color:#fff;">CSL<span style="color:#22c55e;">PRO</span></div>
        <div style="font-size:12px; color:#94a3b8;">{now_str}</div>
    </div>

    <h3 style="padding:0 15px; color:#22c55e;">正在進行 (Live)</h3>
    <div id="live-container">
        {''.join([f'''
        <div class="card live" onclick="alert('稍後啟用內頁')">
            <div class="row" style="font-size:12px; color:#94a3b8; margin-bottom:5px;">
                <span>{m['league']}</span><span>{m['status']}</span>
            </div>
            <div class="row">
                <div style="text-align:center; flex:1;">
                    <img src="{m['homeLogo']}" width="40"><br>{m['home']}
                </div>
                <div class="score">{m['score']}</div>
                <div style="text-align:center; flex:1;">
                    <img src="{m['awayLogo']}" width="40"><br>{m['away']}
                </div>
            </div>
        </div>
        ''' for m in live])}
    </div>
    
    {standings_html}

    <h3 style="padding:0 15px; color:#22c55e;">最新新聞</h3>
    <div class="card">
        {''.join([f'''
        <div class="news-item" onclick="window.open('{n['url']}', '_blank')">
            <img src="{n['img']}" class="news-img">
            <div style="font-size:14px;">{n['title']}</div>
        </div>
        ''' for n in news])}
    </div>

    <h3 style="padding:0 15px; color:#22c55e;">即將開賽</h3>
    <div id="upcoming-container">
        {''.join([f'''
        <div class="card">
            <div style="font-size:12px; color:#94a3b8;">{m['utcDate']} | {m['league']}</div>
            <div class="row" style="margin-top:10px;">
                <span>{m['home']}</span> <span>vs</span> <span>{m['away']}</span>
            </div>
        </div>
        ''' for m in upcoming[:10]])}
    </div>

    <div class="footer">Build: v39.1 (Trans + Standings)</div>
</body>
</html>"""
    
    with open("csl-live-site/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML Generated Successfully.")

if __name__ == "__main__":
    l, u, n, s = fetch_data()
    generate_html(l, u, n, s)
