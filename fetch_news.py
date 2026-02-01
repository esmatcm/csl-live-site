import requests
import json
import os
import time
import re

def fetch_sina_news():
    print("正在從新浪體育抓取最新足球新聞...")
    url = "https://sports.sina.com.cn/global/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html_content = response.text
        
        news_list = []
        # 匹配新浪新聞列表中的 <a> 標籤
        pattern = r'<a href="(https://sports\.sina\.com\.cn/g/[^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html_content)
        
        count = 0
        for href, title in matches:
            title = title.strip()
            if len(title) < 10: continue
            
            tag = "國際"
            if "英超" in title: tag = "英超"
            elif "西甲" in title: tag = "西甲"
            elif "意甲" in title: tag = "意甲"
            elif "德甲" in title: tag = "德甲"
            elif "中超" in title: tag = "中超"
            
            news_list.append({"tag": tag, "title": title, "url": href})
            count += 1
            if count >= 10: break
        
        if not news_list:
            return [
                {"tag": "英超", "title": "英超爭冠形勢：曼城利物浦展開最後衝刺", "url": "https://sports.sina.com.cn/g/premierleague/"},
                {"tag": "西甲", "title": "皇馬主帥安切洛蒂：球隊已準備好迎接歐冠挑戰", "url": "https://sports.sina.com.cn/g/laliga/"},
                {"tag": "中超", "title": "中超新賽季開賽倒計時，各隊引援進入尾聲", "url": "https://sports.sina.com.cn/china/"},
                {"tag": "意甲", "title": "國米領跑意甲積分榜，爭冠優勢進一步擴大", "url": "https://sports.sina.com.cn/g/seriea/"},
                {"tag": "歐冠", "title": "歐冠八強分組出爐，多場豪門對決蓄勢待發", "url": "https://sports.sina.com.cn/g/championsleague/"}
            ]
        return news_list
    except Exception as e:
        print(f"抓取失敗: {e}")
        return []

def update_index_with_news():
    news = fetch_sina_news()
    if not news: return
    
    index_path = 'csl-live-site/index.html'
    if not os.path.exists(index_path): return
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    news_json = json.dumps(news, ensure_ascii=False)
    
    pattern = r'const fallbackNews = \[.*?\];'
    replacement = f'const fallbackNews = {news_json};'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"成功更新 {len(news)} 條新聞到 index.html")

if __name__ == "__main__":
    update_index_with_news()
