import requests
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

def push_test(filename):
    print(f"Pushing test to {filename}...")
    try:
        now_time, token = get_bt_token()
        path = f"/www/wwwroot/hsapi.xyz/{filename}"
        content = f"<html><body><h1>Test {filename}</h1><p>{time.time()}</p></body></html>"
        if filename.endswith('.json'): content = '{"status": "ok"}'
        
        url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
        payload = {'request_time': now_time, 'request_token': token, 'path': path, 'data': content, 'encoding': 'utf-8'}
        
        r = requests.post(url, data=payload, timeout=10)
        print(f"Status: {r.status_code}, Response: {r.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    push_test("full.html")
    push_test("api.json")
