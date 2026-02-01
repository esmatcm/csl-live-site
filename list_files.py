import requests
import hashlib
import time
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def list_dir(path):
    print(f"Listing {path}...")
    try:
        now_time, token = get_bt_token()
        url = f"{BT_PANEL_URL}/files?action=GetDir&tojs=GetFiles&p=1&showRow=200&path={path}"
        payload = {'request_time': now_time, 'request_token': token}
        
        r = requests.post(url, data=payload, timeout=10)
        data = r.json()
        
        if 'DIR' in data or 'FILES' in data:
            print("--- Directories ---")
            for d in data.get('DIR', []): 
                # DIR is list of strings like "name;size;time;..."
                print(d.split(';')[0]) 
            print("--- Files ---")
            for f in data.get('FILES', []):
                print(f.split(';')[0])
        else:
            print(f"Raw: {data}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_dir("/www/wwwroot/hsapi.xyz")
