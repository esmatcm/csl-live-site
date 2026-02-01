import requests
import os
import json
import hashlib
import time

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
    # 在伺服器建立目錄並下載 Logo
    print("正在伺服器建立目錄並下載中超 Logo...")
    cmds = [
        "mkdir -p /www/wwwroot/hsapi.xyz/logos",
        "curl -o /www/wwwroot/hsapi.xyz/logos/644.png https://img.vipsoccer.com/soccer/team/644.png",
        "curl -o /www/wwwroot/hsapi.xyz/logos/654.png https://img.vipsoccer.com/soccer/team/654.png",
        "curl -o /www/wwwroot/hsapi.xyz/logos/653.png https://img.vipsoccer.com/soccer/team/653.png",
        "curl -o /www/wwwroot/hsapi.xyz/logos/651.png https://img.vipsoccer.com/soccer/team/651.png",
        "curl -o /www/wwwroot/hsapi.xyz/logos/34161.png https://img.vipsoccer.com/soccer/team/34161.png"
    ]
    for cmd in cmds:
        run_shell(cmd)
    print("Logo 本地化完成。")
