import requests
import hashlib
import time
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def test_connection():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    
    url = f"{BT_PANEL_URL}/files?action=GetDir&tojs=GetFiles&p=1&showRow=10&path=/www/wwwroot"
    payload = {'request_time': now_time, 'request_token': token}
    
    try:
        r = requests.post(url, data=payload, timeout=5)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text[:200]}") # Print first 200 chars
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_connection()
