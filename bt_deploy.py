import requests
import json
import time
import hashlib

# 醫生提供的伺服器資訊
BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    # 寶塔 API 需要計算 md5(timestamp + md5(api_key))
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def test_connection():
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/system?action=GetSystemTotal"
    payload = {
        'request_time': now_time,
        'request_token': token
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        # 確保以 utf-8 處理
        return response.json()
    except Exception as e:
        return {"status": False, "msg": str(e)}

if __name__ == "__main__":
    import sys
    # 強制輸出為 utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    result = test_connection()
    print(json.dumps(result, ensure_ascii=False))
