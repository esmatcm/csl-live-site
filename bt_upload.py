import requests
import json
import time
import hashlib
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
    
    try:
        response = requests.post(url, data=payload, timeout=20)
        return response.json()
    except Exception as e:
        return {"status": False, "msg": str(e)}

if __name__ == "__main__":
    with open('csl-live-site/index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("正在上傳專業版 HTML...")
    result = upload_file(html_content, 'index.html')
    print(json.dumps(result, ensure_ascii=False))
