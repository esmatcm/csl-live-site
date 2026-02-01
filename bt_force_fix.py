import requests
import json
import hashlib
import time
import sys

# 確保輸出編碼
sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def run_shell(shell_cmd):
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/system?action=RunShell"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'shell': shell_cmd
    }
    try:
        response = requests.post(url, data=payload, timeout=30)
        return response.json()
    except Exception as e:
        return {"status": False, "msg": str(e)}

if __name__ == "__main__":
    print("正在強制修復伺服器目錄結構與圖片權限...")
    # 強制建立目錄並下載圖片
    results = []
    results.append(run_shell("mkdir -pv /www/wwwroot/hsapi.xyz/logos"))
    results.append(run_shell("curl -L -o /www/wwwroot/hsapi.xyz/logos/644.png https://img.vipsoccer.com/soccer/team/644.png"))
    results.append(run_shell("curl -L -o /www/wwwroot/hsapi.xyz/logos/654.png https://img.vipsoccer.com/soccer/team/654.png"))
    results.append(run_shell("curl -L -o /www/wwwroot/hsapi.xyz/logos/653.png https://img.vipsoccer.com/soccer/team/653.png"))
    results.append(run_shell("curl -L -o /www/wwwroot/hsapi.xyz/logos/651.png https://img.vipsoccer.com/soccer/team/651.png"))
    results.append(run_shell("chmod -R 755 /www/wwwroot/hsapi.xyz/logos"))
    results.append(run_shell("chown -R www:www /www/wwwroot/hsapi.xyz/logos"))
    
    for r in results:
        print(json.dumps(r, ensure_ascii=False))
