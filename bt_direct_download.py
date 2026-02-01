import requests
import json
import hashlib
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def quick_download(filename, url):
    now_time, token = get_bt_token()
    # 使用寶塔內建的下載遠端檔案功能
    api_url = f"{BT_PANEL_URL}/files?action=DownloadFile"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'url': url,
        'path': '/www/wwwroot/hsapi.xyz/logos/',
        'filename': filename
    }
    return requests.post(api_url, data=payload, timeout=30).json()

if __name__ == "__main__":
    print("啟動寶塔遠端下載引擎...")
    logos = {
        "644.png": "https://img.vipsoccer.com/soccer/team/644.png",
        "654.png": "https://img.vipsoccer.com/soccer/team/654.png",
        "653.png": "https://img.vipsoccer.com/soccer/team/653.png",
        "651.png": "https://img.vipsoccer.com/soccer/team/651.png"
    }
    for filename, url in logos.items():
        res = quick_download(filename, url)
        print(f"下載 {filename}: {json.dumps(res, ensure_ascii=False)}")
