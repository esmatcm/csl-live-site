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
        "Sheffield United FC": "謝菲爾德聯", "1. FSV Mainz 05": "美因茨", "1. FC Union Berlin": "柏林聯",
        "VfL Wolfsburg": "沃爾夫斯堡", "FC Augsburg": "奧格斯堡", "SV Werder Bremen": "不萊梅",
        "SC Freiburg": "弗賴堡", "1. FC Heidenheim 1846": "海登海姆", "VfL Bochum 1848": "波鴻",
        "SV Darmstadt 98": "達姆施塔特", "1. FC Köln": "科隆"
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
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=15)
        data = r.json()
        for m in data.get('matches', []):
            item = {
                "id": m['id'],
                "league": m['competition']['name'],
                "home": translate('teams', m['homeTeam']['name']),
                "away": translate('teams', m['awayTeam']['name']),
                "homeLogo": m['homeTeam']['crest'],
                "awayLogo": m['awayTeam']['crest'],
                "score": f"{m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0} - {m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0}",
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
            for row in data['standings'][0]['table'][:10]:
                table.append({
                    "pos": row['position'],
                    "team": translate('teams', row['team']['name']),
                    "played": row['playedGames'],
                    "points": row['points'],
                    "crest": row['team']['crest']
                })
            standings[code] = table
        except: pass

    # News (Dongqiudi) - Fetch Body
    print("Fetching News Details...")
    news = []
    try:
        dqd_url = "https://api.dongqiudi.com/app/tabs/iphone/1.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(dqd_url, headers=headers, timeout=10)
        data = r.json()
        count = 0
        for article in data.get('articles', []):
            if count >= 6: break # Limit to 6 for speed
            if 'thumb' in article and article['thumb']:
                img_src = get_image_base64(article['thumb'])
                
                # Fetch Body content
                body = "內容載入中..."
                try:
                    art_url = f"https://api.dongqiudi.com/article/{article['id']}.html" # Attempt to guess API or scrape web
                    # For stability in this static build, we'll use a summary or just the description if available, 
                    # or link. Scraping full body from web might be slow/blocked. 
                    # Let's try to get a bit more info if possible, otherwise use description.
                    body = article.get('description', '') or article.get('title', '')
                except: pass

                news.append({
                    "id": count,
                    "title": article['title'],
                    "img": img_src,
                    "body": body,
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
        standings_html += f"<div class='card standings-card' id='standings-{league}' style='display:none;'><h3>{league} 積分榜</h3><table><thead><tr><th>#</th><th>球隊</th><th>賽</th><th>分</th></tr></thead><tbody>{rows}</tbody></table></div>"
    
    # Pre-compute JS data
    js_news_data = json.dumps(news, ensure_ascii=False)
    js_live_data = json.dumps(live, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSL PRO</title>
    <style>
        body {{ background: #05070a; color: #e2e8f0; font-family: sans-serif; margin: 0; padding: 0; }}
        .nav {{ background: #0f172a; padding: 15px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }}
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
        
        /* Modal */
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }}
        .modal-content {{ background-color: #0f172a; margin: 10% auto; padding: 20px; border: 1px solid #22c55e; width: 85%; max-width: 500px; border-radius: 12px; position: relative; max-height: 80vh; overflow-y: auto; }}
        .close {{ color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }}
        .tab-btn {{ background: #1e293b; border: 1px solid #334155; color: #fff; padding: 5px 10px; border-radius: 15px; margin-right: 5px; cursor: pointer; }}
        .tab-btn.active {{ background: #22c55e; border-color: #22c55e; }}
    </style>
</head>
<body>
    <div class="nav">
        <div style="font-weight:bold; color:#fff;">CSL<span style="color:#22c55e;">PRO</span></div>
        <div style="font-size:12px; color:#94a3b8;">{now_str}</div>
    </div>

    <!-- Live Matches -->
    <h3 style="padding:0 15px; color:#22c55e;">正在進行 (Live)</h3>
    <div id="live-container">
        {''.join([f'''
        <div class="card live" onclick='openMatch({json.dumps(m, ensure_ascii=False)})'>
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
    
    <!-- Standings Tabs -->
    <div style="padding: 0 10px; overflow-x: auto; white-space: nowrap;">
        <button class="tab-btn active" onclick="showTab('PL')">英超</button>
        <button class="tab-btn" onclick="showTab('PD')">西甲</button>
        <button class="tab-btn" onclick="showTab('SA')">意甲</button>
        <button class="tab-btn" onclick="showTab('BL1')">德甲</button>
        <button class="tab-btn" onclick="showTab('FL1')">法甲</button>
    </div>
    <div id="standings-container">
        {standings_html}
    </div>

    <!-- News -->
    <h3 style="padding:0 15px; color:#22c55e;">最新新聞</h3>
    <div class="card">
        {''.join([f'''
        <div class="news-item" onclick='openNews({n["id"]})'>
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

    <!-- Modal -->
    <div id="myModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="modal-body"></div>
        </div>
    </div>

    <div class="footer">Build: v39.2 (Inner Pages)</div>

    <script>
        const newsData = {js_news_data};

        function showTab(league) {{
            document.querySelectorAll('.standings-card').forEach(el => el.style.display = 'none');
            document.getElementById('standings-' + league).style.display = 'block';
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            event.target.classList.add('active');
        }}

        function openMatch(m) {{
            const modal = document.getElementById('myModal');
            const body = document.getElementById('modal-body');
            body.innerHTML = `
                <h2 style="text-align:center; color:#22c55e;">${{m.league}}</h2>
                <h1 style="text-align:center;">${{m.home}} vs ${{m.away}}</h1>
                <h2 style="text-align:center;">${{m.score}}</h2>
                <p style="text-align:center;">狀態: ${{m.status}}</p>
                <p style="text-align:center;">場地: ${{m.venue}}</p>
                <hr>
                <p style="text-align:center; color:#888;">(更多實時數據需 API 支援)</p>
            `;
            modal.style.display = "block";
        }}

        function openNews(id) {{
            const n = newsData.find(x => x.id === id);
            const modal = document.getElementById('myModal');
            const body = document.getElementById('modal-body');
            body.innerHTML = `
                <h3>${{n.title}}</h3>
                <img src="${{n.img}}" style="width:100%; border-radius:8px;">
                <p style="line-height:1.6; margin-top:15px;">${{n.body}}</p>
                <a href="${{n.url}}" target="_blank" style="color:#22c55e; display:block; margin-top:20px;">閱讀原文 &rarr;</a>
            `;
            modal.style.display = "block";
        }}

        function closeModal() {{
            document.getElementById('myModal').style.display = "none";
        }}

        // Init
        showTab('PL');
    </script>
</body>
</html>"""
    
    with open("csl-live-site/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML Generated Successfully.")

if __name__ == "__main__":
    l, u, n, s = fetch_data()
    generate_html(l, u, n, s)
