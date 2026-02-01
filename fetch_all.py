import requests
import json
import os
import re
from datetime import datetime

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4"

def fetch_sina_news_content():
    print("正在抓取並本地化新聞內容...")
    list_url = "https://sports.sina.com.cn/global/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(list_url, headers=headers)
        res.encoding = 'utf-8'
        matches = re.findall(r'<a href="(https://sports\.sina\.com\.cn/g/[^"]+)"[^>]*>([^<]+)</a>', res.text)
        
        news_data = []
        for i, (href, title) in enumerate(matches[:8]):
            # 抓取正文
            try:
                detail_res = requests.get(href, headers=headers)
                detail_res.encoding = 'utf-8'
                # 簡單抓取段落
                body_matches = re.findall(r'<p>(.*?)</p>', detail_res.text)
                body = "<br><br>".join([b for b in body_matches if len(b) > 20 and '<' not in b][:5])
                
                news_data.append({
                    "id": i,
                    "tag": "足球",
                    "title": title.strip(),
                    "body": body if body else "點擊查看詳情..."
                })
            except:
                continue
        return news_data
    except:
        return []

def fetch_fixtures():
    print("正在抓取未來賽程...")
    # 獲取未來7天所有比賽
    headers = {'X-Auth-Token': API_KEY}
    fixtures = {}
    # 免費版支持的聯賽代碼
    leagues = ['PL', 'PD', 'SA', 'BL1', 'FL1']
    
    for league in leagues:
        try:
            res = requests.get(f"{BASE_URL}/competitions/{league}/matches?status=SCHEDULED", headers=headers)
            data = res.json()
            league_fixtures = []
            for m in data.get('matches', [])[:3]: # 每個聯賽取3場
                league_fixtures.append({
                    "date": m['utcDate'].split('T')[0],
                    "time": m['utcDate'].split('T')[1][:5],
                    "home": m['homeTeam']['shortName'],
                    "away": m['awayTeam']['shortName'],
                    "venue": m.get('venue', '體育場')
                })
            fixtures[league] = league_fixtures
        except:
            fixtures[league] = []
    
    # 手動加入中超賽程 (模擬)
    fixtures['CSL'] = [
        {"date": "2026-03-06", "time": "19:35", "home": "上海海港", "away": "北京國安", "venue": "上汽浦東足球場"},
        {"date": "2026-03-07", "time": "19:35", "home": "成都蓉城", "away": "山東泰山", "venue": "鳳凰山體育公園"}
    ]
    return fixtures

def update_site():
    news = fetch_sina_news_content()
    fixtures = fetch_fixtures()
    
    index_path = 'csl-live-site/index.html'
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 注入數據
    content = re.sub(r'const newsData = \[.*?\];', f'const newsData = {json.dumps(news, ensure_ascii=False)};', content, flags=re.DOTALL)
    content = re.sub(r'const fixtureData = \{.*?\};', f'const fixtureData = {json.dumps(fixtures, ensure_ascii=False)};', content, flags=re.DOTALL)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("網站本地化數據更新完成")

if __name__ == "__main__":
    update_site()
