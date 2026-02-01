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
        "Bayer 04 Leverkusen": "勒沃庫森", "Paris Saint-Germain FC": "巴黎聖日耳門"
    }
}

def translate(cat, key):
    return I18N.get(cat, {}).get(key, key)

def get_image_base64(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://sports.sina.com.cn/'}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            b64 = base64.b64encode(r.content).decode('utf-8')
            return f"data:image/jpeg;base64,{b64}"
    except: pass
    return "https://via.placeholder.com/80?text=No+Img"

def fetch_data():
    print("Fetching Matches...")
    live = []
    upcoming = []
    
    live.append({
        "id": 999999,
        "league": "系統測試賽",
        "home": "阿森納", "away": "曼城",
        "homeLogo": "https://crests.football-data.org/57.png",
        "awayLogo": "https://crests.football-data.org/65.png",
        "score": "2 - 1",
        "status": "進行中",
        "utcDate": datetime.now(TAIPEI_TZ).isoformat(),
        "venue": "酋長球場"
    })

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
    except Exception as e:
        print(f"Match Error: {e}")

    print("Fetching News & Converting Images...")
    news = []
    try:
        res = requests.get("https://sports.sina.com.cn/global/", timeout=10)
        res.encoding = 'utf-8'
        matches = re.findall(r'<a href="(https://sports\.sina\.com\.cn/g/[^"]+)"[^>]*>([^<]+)</a>', res.text)
        
        for i, (href, title) in enumerate(matches[:8]):
            # 嘗試找圖片 URL
            try:
                detail = requests.get(href, timeout=5)
                detail.encoding = 'utf-8'
                img_m = re.search(r'src="(//n\.sinaimg\.cn/[^"]+\.(?:jpg|png|jpeg))"', detail.text)
                img_url = "https:" + img_m.group(1) if img_m else ""
                
                # 轉 Base64
                img_src = get_image_base64(img_url) if img_url else "https://via.placeholder.com/80"
                
                news.append({"id": i, "title": title.strip(), "img": img_src, "url": href})
            except: continue
    except: pass

    return live, upcoming, news

def generate_html(live, upcoming, news):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y/%m/%d %H:%M')
    
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
        <div class="card live">
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
            <div style="text-align:center; margin-top:10px; font-size:12px; color:#cbd5e1;">📍 {m['venue']}</div>
        </div>
        ''' for m in live])}
    </div>

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

    <div class="footer">Build: v36.1 (Static Base64 Images)</div>
</body>
</html>"""
    
    with open("csl-live-site/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML Generated Successfully.")

if __name__ == "__main__":
    l, u, n = fetch_data()
    generate_html(l, u, n)
