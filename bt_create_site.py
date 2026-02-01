import requests
import json
import time
import hashlib
import sys

# 設置輸出編碼
sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def create_site():
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/site?action=AddSite"
    
    # 建立站點數據
    web_data = {
        "webname": '{"domain":"hsapi.xyz","domainlist":["www.hsapi.xyz"],"count":0}',
        "path": "/www/wwwroot/hsapi.xyz",
        "type": "PHP", # 即使是靜態/Node，寶塔通常也需要一個類型初始化
        "version": "00",
        "port": "80",
        "ps": "中超即時開獎網官方站",
        "ftp": "false",
        "sql": "false"
    }
    
    payload = {
        'request_time': now_time,
        'request_token': token,
        **web_data
    }
    
    try:
        response = requests.post(url, data=payload, timeout=15)
        return response.json()
    except Exception as e:
        return {"status": False, "msg": str(e)}

if __name__ == "__main__":
    print("正在寶塔建立站點...")
    result = create_site()
    print(json.dumps(result, ensure_ascii=False))
