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

def apply_ssl():
    now_time, token = get_bt_token()
    # 寶塔一鍵申請 Let's Encrypt 證書 API
    url = f"{BT_PANEL_URL}/site?action=HttpToHttps"
    
    # 首先確保開啟 80 強制跳轉 443
    payload = {
        'request_time': now_time,
        'request_token': token,
        'siteName': 'hsapi.xyz'
    }
    
    try:
        # 申請證書的 API 通常是 SetSSL
        cert_url = f"{BT_PANEL_URL}/site?action=SetSSL"
        cert_payload = {
            'request_time': now_time,
            'request_token': token,
            'type': '1', # 1 代表 Let's Encrypt
            'siteName': 'hsapi.xyz',
            'domain': 'hsapi.xyz',
            'auth_type': 'pc' # 面板驗證
        }
        response = requests.post(cert_url, data=cert_payload, timeout=60)
        return response.json()
    except Exception as e:
        return {"status": False, "msg": str(e)}

if __name__ == "__main__":
    print("正在透過寶塔申請 SSL 憑證並配置 HTTPS...")
    result = apply_ssl()
    print(json.dumps(result, ensure_ascii=False))
