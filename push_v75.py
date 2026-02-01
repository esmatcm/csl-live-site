import requests
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

def push_v75():
    print("Pushing V75 FIXED HTML...")
    try:
        with open('csl-live-site/index_v75.html', 'r', encoding='utf-8') as f:
            content = f.read()
            
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': "/www/wwwroot/hsapi.xyz/index.html", 'data': content, 'encoding': 'utf-8'}
        
        r = requests.post(url, data=payload, timeout=10)
        print(f"Status: {r.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    push_v75()
