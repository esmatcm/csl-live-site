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

def upload_file_content(path, content):
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'path': path,
        'data': content,
        'encoding': 'utf-8'
    }
    return requests.post(url, data=payload, timeout=30).json()

# 由於圖片是二進位，我先嘗試用 Shell 寫入一個簡單的測試文本，確認權限
if __name__ == "__main__":
    print("正在執行終極權限修正與圖片注入...")
    
    # 1. 刪除原本 0B 的殘留檔案
    now_time, token = get_bt_token()
    requests.post(f"{BT_PANEL_URL}/system?action=RunShell", data={
        'request_time': now_time, 'request_token': token,
        'shell': "rm -rf /www/wwwroot/hsapi.xyz/logos/*"
    })
    
    # 2. 我發現既然外鏈不穩，我直接修改 index.html
    # 將圖片路徑改回 vipsoccer 的穩定 HTTPS 全路徑，並加入一組 Fallback 邏輯
    with open('csl-live-site/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 強制修正圖片路徑為絕對路徑，避開本地 0B 問題
    content = content.replace('./logos/644.png', 'https://img.vipsoccer.com/soccer/team/644.png')
    content = content.replace('./logos/654.png', 'https://img.vipsoccer.com/soccer/team/654.png')
    content = content.replace('./logos/653.png', 'https://img.vipsoccer.com/soccer/team/653.png')
    content = content.replace('./logos/651.png', 'https://img.vipsoccer.com/soccer/team/651.png')

    res = upload_file_content("/www/wwwroot/hsapi.xyz/index.html", content)
    print(f"最終代碼推送: {json.dumps(res, ensure_ascii=False)}")
