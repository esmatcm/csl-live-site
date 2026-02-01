import requests
import json
import hashlib
import time
import os
import base64
import sys

sys.stdout.reconfigure(encoding='utf-8')

BT_PANEL_URL = "http://74.48.191.162:8888"
BT_API_KEY = "se5DF3esy9dV8if8cvThChs0wlp5yMRa"
SITE_ROOT = "/www/wwwroot/hsapi.xyz"

def get_bt_token():
    now_time = int(time.time())
    token_str = str(now_time) + hashlib.md5(BT_API_KEY.encode('utf-8')).hexdigest()
    token = hashlib.md5(token_str.encode('utf-8')).hexdigest()
    return now_time, token

def run_shell(cmd):
    now_time, token = get_bt_token()
    url = f"{BT_PANEL_URL}/system?action=RunShell"
    payload = {
        'request_time': now_time,
        'request_token': token,
        'shell': cmd
    }
    return requests.post(url, data=payload, timeout=30).json()

def deploy_images():
    print("🚀 開始部署實體圖片到伺服器...")
    
    # 1. 確保目錄存在
    run_shell(f"mkdir -p {SITE_ROOT}/img_cache")
    
    local_dir = "csl-live-site/img_cache"
    if not os.path.exists(local_dir):
        print("本地無圖片緩存")
        return

    files = [f for f in os.listdir(local_dir) if f.endswith(".jpg")]
    print(f"找到 {len(files)} 張圖片，開始上傳...")

    for fname in files:
        file_path = os.path.join(local_dir, fname)
        with open(file_path, "rb") as f:
            b64_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 2. 使用 Shell 還原圖片
        # 注意：分塊寫入以避免 Shell 指令過長
        # 這裡簡化為直接覆蓋，假設圖片不超過 CMD 長度限制 (通常 128KB 沒問題)
        server_path = f"{SITE_ROOT}/img_cache/{fname}"
        cmd = f"echo \"{b64_data}\" | base64 -d > {server_path}"
        
        res = run_shell(cmd)
        if res.get('status'):
            print(f"✅ {fname} 上傳成功")
        else:
            print(f"❌ {fname} 上傳失敗: {res.get('msg')}")

    print("圖片部署完成。")

if __name__ == "__main__":
    deploy_images()
