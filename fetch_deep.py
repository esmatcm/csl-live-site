import requests
import re
import json
import os
import sys

# 強制使用 UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fetch_sina_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://sports.sina.com.cn/'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        html = res.text
        
        # 1. 精準抓取圖片 (針對新浪新聞正文圖片的常見標籤)
        # 尋找含有 data-src 或 src 的 <img> 標籤，通常在 id="artibody" 內
        img_url = "https://via.placeholder.com/400x200?text=CSL+PRO"
        
        # 先定位正文區域以縮小範圍
        body_area = re.search(r'id="artibody"[^>]*>(.*?)<!--', html, flags=re.DOTALL)
        if not body_area:
            body_area = re.search(r'class="article"[^>]*>(.*?)<div', html, flags=re.DOTALL)
        
        search_html = body_area.group(1) if body_area else html
        
        # 匹配常見的新浪圖片格式
        img_matches = re.findall(r'src="(//n\.sinaimg\.cn/[^"]+\.(?:jpg|png|jpeg|gif))"', search_html)
        if not img_matches:
            img_matches = re.findall(r'data-src="(//n\.sinaimg\.cn/[^"]+\.(?:jpg|png|jpeg|gif))"', search_html)
        
        if img_matches:
            # 過濾掉一些小圖示（如果有的話）
            for m in img_matches:
                if "thumb" not in m: # 優先選大圖
                    img_url = "https:" + m
                    break
        
        # 2. 抓取正文
        body = ""
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', search_html, flags=re.DOTALL)
        valid_p = []
        for p in paragraphs:
            # 清洗標籤
            p_text = re.sub(r'<[^>]+>', '', p).strip()
            if len(p_text) > 25 and "點擊" not in p_text and "掃描二維碼" not in p_text:
                valid_p.append(f"<p style='margin-bottom:15px; color:#cbd5e1;'>{p_text}</p>")
        
        body = "".join(valid_p[:10])
        return img_url, body if body else "<p>暫無內容摘要，請點擊原文查看。</p>"
    except Exception as e:
        return "", f"抓取失敗: {str(e)}"

def update_all():
    print("Fetching global news list...")
    list_url = "https://sports.sina.com.cn/global/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(list_url, headers=headers)
        res.encoding = 'utf-8'
        # 抓取新聞標題和鏈接
        matches = re.findall(r'<a href="(https://sports\.sina\.com\.cn/g/[^"]+)"[^>]*>([^<]+)</a>', res.text)
        
        processed_news = []
        seen_titles = set()
        count = 0
        for href, title in matches:
            if count >= 8: break
            title = title.strip()
            if len(title) < 12 or title in seen_titles: continue
            seen_titles.add(title)
            
            print(f"Processing ({count+1}/8): {title[:20]}")
            img, body = fetch_sina_article(href)
            
            tag = "國際"
            if "英超" in title: tag = "英超"
            elif "中超" in title: tag = "中超"
            elif "西甲" in title: tag = "西甲"
            elif "意甲" in title: tag = "意甲"
            
            processed_news.append({
                "id": count,
                "tag": tag,
                "title": title,
                "img": img,
                "body": body,
                "url": href
            })
            count += 1
            
        index_path = 'csl-live-site/index.html'
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        news_json = json.dumps(processed_news, ensure_ascii=False)
        content = re.sub(r'const newsData = \[.*?\];', f'const newsData = {news_json};', content, flags=re.DOTALL)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Success: News and images updated.")
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    update_all()
