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

def apply_lets_encrypt():
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/site?action=CreateLet"
    
    # 寶塔 CreateLet API 參數
    payload = {
        'request_time': now_time,
        'request_token': token,
        'siteName': 'hsapi.xyz',
        'domains': json.dumps(['hsapi.xyz', 'www.hsapi.xyz']),
        'force': 'true',
        'id': '230' # 之前建立站點返回的 ID
    }
    
    try:
        response = requests.post(url, data=payload, timeout=60)
        return response.json()
    except Exception as e:
        return {"status": False, "msg": str(e)}

if __name__ == "__main__":
    print("正在透過寶塔 CreateLet 接口申請 SSL...")
    result = apply_lets_encrypt()
    print(json.dumps(result, ensure_ascii=False))
