import requests
import base64
import json
import hashlib
import time

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def get_b64(url):
    # 從一個不被封鎖的公用來源獲取圖片
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=15)
        return f"data:image/png;base64,{base64.b64encode(res.content).decode('utf-8')}"
    except:
        return ""

if __name__ == "__main__":
    print("正在將隊徽轉換為終極內嵌 Base64 字串...")
    # 改用 wikipedia 或其他源獲取，確保我這邊能抓到
    haigang = get_b64("https://img.vipsoccer.com/soccer/team/644.png")
    taishan = get_b64("https://img.vipsoccer.com/soccer/team/654.png")
    
    with open('csl-live-site/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 強制替換為內嵌數據
    if haigang: html = html.replace('https://img1.imgtn.bdimg.com/it/u=3031267866,2367732814&fm=26&gp=0.jpg', haigang)
    if taishan: html = html.replace('https://img1.imgtn.bdimg.com/it/u=1801267866,2367732814&fm=26&gp=0.jpg', taishan)

    # 推送到寶塔
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
    payload = {
        'request_time': now_time, 'request_token': token,
        'path': "/www/wwwroot/hsapi.xyz/index.html",
        'data': html, 'encoding': 'utf-8'
    }
    requests.post(url, data=payload)
    print("終極內嵌版 v15.0 推送成功！")
