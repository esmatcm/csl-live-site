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

def upload_file(content, filename):
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'path': f"/www/wwwroot/hsapi.xyz/{filename}",
        'data': content,
        'encoding': 'utf-8'
    }
    return requests.post(url, data=payload, timeout=20).json()

def create_dir(path):
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=CreateDir"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'path': path
    }
    return requests.post(url, data=payload, timeout=20).json()

if __name__ == "__main__":
    print("正在執行寶塔物理修復...")
    # 1. 建立 logos 目錄
    print("建立目錄: " + json.dumps(create_dir("/www/wwwroot/hsapi.xyz/logos"), ensure_ascii=False))
    
    # 2. 上傳 HTML
    with open('csl-live-site/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    print("更新 HTML: " + json.dumps(upload_file(html, 'index.html'), ensure_ascii=False))
