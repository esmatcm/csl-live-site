import requests
import json
import time
from datetime import datetime

API_KEY = '735d0b4e485a431db7867a42b0dda855'
HEADERS = {'X-Auth-Token': API_KEY}
BASE_URL = "https://api.football-data.org/v4"

# P0 Cache & Rate Limit Engine
MATCH_CACHE = {}
IN_FLIGHT = {}
CALL_LOG = []
LAST_API_CALL = 0

def fetch_match_detail_p0(match_id):
    global LAST_API_CALL
    now = time.time()
    
    # 1. 檢查快取 (TTL 15s for Live)
    if match_id in MATCH_CACHE:
        cache_data, timestamp = MATCH_CACHE[match_id]
        if now - timestamp < 15:
            print(f"DEBUG: matchId={match_id} | from_cache=true")
            return cache_data

    # 2. 合併請求 (Request Coalescing)
    if match_id in IN_FLIGHT:
        print(f"DEBUG: matchId={match_id} | coalescing=true")
        while match_id in IN_FLIGHT:
            time.sleep(0.5)
        return MATCH_CACHE.get(match_id, ({}, 0))[0]

    # 3. 100/min 限流控制 (最小間隔 0.6s)
    if now - LAST_API_CALL < 0.6:
        time.sleep(0.6)

    IN_FLIGHT[match_id] = True
    start_time = time.time()
    try:
        print(f"DEBUG: matchId={match_id} | endpoint=matches/{match_id} | status=FETCHING")
        r = requests.get(f"{BASE_URL}/matches/{match_id}", headers=HEADERS, timeout=10)
        LAST_API_CALL = time.time()
        
        status_code = r.status_code
        duration = round(time.time() - start_time, 2)
        
        if status_code == 200:
            data = r.json()
            # 構建聚合 JSON
            detail = {
                "basic": {
                    "home": data['homeTeam']['shortName'],
                    "away": data['awayTeam']['shortName'],
                    "score": f"{data['score']['fullTime']['home']} - {data['score']['fullTime']['away']}",
                    "status": data['status'],
                    "venue": data.get('venue', '未知')
                },
                "events": data.get('goals', []),
                "lineups": {"data": None, "reason": "Tier 1 Limit"},
                "stats": {"data": None, "reason": "Tier 1 Limit"},
                "last_updated_at": datetime.now().isoformat()
            }
            MATCH_CACHE[match_id] = (detail, time.time())
            print(f"LOG: matchId={match_id} | status={status_code} | dur={duration}s | from_cache=false")
            return detail
        elif status_code == 429:
            print(f"LOG: matchId={match_id} | status=429 | dur={duration}s | msg=RATE_LIMITED")
            return {"error": "RATE_LIMITED", "basic": None}
        else:
            return {"error": f"API_ERROR_{status_code}", "basic": None}
            
    finally:
        del IN_FLIGHT[match_id]

# 模擬測試脚本
if __name__ == "__main__":
    # 測試連點 5 次
    test_id = 552694
    print("--- 模擬連點 5 次測試 ---")
    for i in range(5):
        res = fetch_match_detail_p0(test_id)
        print(f"請求 {i+1} 完成，狀態: {res.get('basic', {}).get('status') if res.get('basic') else 'ERR'}")
