import requests
import json
import hashlib
import time
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def upload_file_content(path, content):
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/files?action=SaveFileBody"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'path': path,
        'data': content,
        'encoding': 'utf-8'
    }
    return requests.post(url, data=payload, timeout=30).json()

def run_shell(shell):
    now_time, token = get_bt_token()
    return requests.post(
        f"{BT_PANEL_URL}/system?action=RunShell",
        data={'request_time': now_time, 'request_token': token, 'shell': shell},
        timeout=30
    ).json()

if __name__ == "__main__":
    print("🔥 THIS IS NEW VERSION")
    print("開始部署...")

    # ====== 路徑：用「腳本所在資料夾」當基準，避免你之前那個 csl-live-site/index.html 的相對路徑地獄 ======
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    local_index_path = os.path.join(BASE_DIR, "index.html")
    local_health_path = os.path.join(BASE_DIR, "health.html")

    # 1) 推送 index.html（維持你原本邏輯）
    with open(local_index_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace('./logos/644.png', 'https://img.vipsoccer.com/soccer/team/644.png')
    content = content.replace('./logos/654.png', 'https://img.vipsoccer.com/soccer/team/654.png')
    content = content.replace('./logos/653.png', 'https://img.vipsoccer.com/soccer/team/653.png')
    content = content.replace('./logos/651.png', 'https://img.vipsoccer.com/soccer/team/651.png')

    res_index = upload_file_content("/www/wwwroot/hsapi.xyz/index.html", content)
    print("Index:", json.dumps(res_index, ensure_ascii=False))

    # 2) 推送 health.html（✅只新增：先在伺服器端建立檔案，不然 SaveFileBody 會回：指定文件不存在）
    #    你本機 health.html 已存在（你 dir 看到了 43 bytes），所以只差伺服器端建檔
    #    這裡只做 touch + chmod，不會影響其他檔案
    shell_cmd = (
        "mkdir -p /www/wwwroot/hsapi.xyz && "
        "test -f /www/wwwroot/hsapi.xyz/health.html || echo OK > /www/wwwroot/hsapi.xyz/health.html && "
        "chmod 644 /www/wwwroot/hsapi.xyz/health.html"
    )
    _ = run_shell(shell_cmd)

    with open(local_health_path, "r", encoding="utf-8") as f:
        health_content = f.read()

    res_health = upload_file_content("/www/wwwroot/hsapi.xyz/health.html", health_content)
    print("Health:", json.dumps(res_health, ensure_ascii=False))
