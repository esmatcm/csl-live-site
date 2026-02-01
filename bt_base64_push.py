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

def get_base64_img(url):
    res = requests.get(url, timeout=10)
    return f"data:image/png;base64,{base64.b64encode(res.content).decode('utf-8')}"

if __name__ == "__main__":
    print("正在將所有隊徽轉換為 Base64 內嵌字串...")
    haigang = get_base64_img("https://img.vipsoccer.com/soccer/team/644.png")
    taishan = get_base64_img("https://img.vipsoccer.com/soccer/team/654.png")
    
    with open('csl-live-site/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 強制內嵌 Base64，徹底解決 404 問題
    html = html.replace('src="./logos/644.png"', f'src="{haigang}"')
    html = html.replace('src="./logos/654.png"', f'src="{taishan}"')
    html = html.replace('src="https://img.vipsoccer.com/soccer/team/644.png"', f'src="{haigang}"')
    html = html.replace('src="https://img.vipsoccer.com/soccer/team/654.png"', f'src="{taishan}"')

    # 推送到寶塔
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
    payload = {
        'request_time': now_time, 'request_token': token,
        'path': "/www/wwwroot/hsapi.xyz/index.html",
        'data': html, 'encoding': 'utf-8'
    }
    res = requests.post(url, data=payload).json()
    print(f"終極代碼推送成功: {json.dumps(res, ensure_ascii=False)}")
