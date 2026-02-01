import requests
import json
import hashlib
import time
import sys
import base64

sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def upload_binary(content, filename):
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'path': f"/www/wwwroot/hsapi.xyz/logos/{filename}",
        'data': content,
        'encoding': 'utf-8'
    }
    return requests.post(url, data=payload, timeout=30).json()

# 由於無法直接讀取二進位，我先嘗試用 curl 讓伺服器自己抓，這次加上完整 User-Agent 避免 403
def server_download(img_url, filename):
    now_time, token = get_bt_token()
    shell_cmd = f"curl -L -A 'Mozilla/5.0' -o /www/wwwroot/hsapi.xyz/logos/{filename} {img_url}"
    url = f"{BT_PANEL_URL}/system?action=RunShell"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'shell': shell_cmd
    }
    return requests.post(url, data=payload).json()

if __name__ == "__main__":
    print("正在執行圖片傳輸任務...")
    logos = {
        "644.png": "https://img.vipsoccer.com/soccer/team/644.png",
        "654.png": "https://img.vipsoccer.com/soccer/team/654.png",
        "653.png": "https://img.vipsoccer.com/soccer/team/653.png",
        "651.png": "https://img.vipsoccer.com/soccer/team/651.png"
    }
    for filename, url in logos.items():
        res = server_download(url, filename)
        print(f"上傳 {filename}: {json.dumps(res, ensure_ascii=False)}")
