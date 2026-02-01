import requests
import json
import time

BASE_URL = "https://api.dongqiudi.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
}

def debug_dqd():
    # Use yesterday/today to ensure matches exist
    date_str = time.strftime("%Y-%m-%d")
    url = f"{BASE_URL}/data/tab/new/important?date={date_str}&start=2026-02-01%2016:00:00" 
    # DQD API often needs 'start' param or just date. Let's try basic schedule.
    
    # Better endpoint: /schedule/index
    url = f"https://api.dongqiudi.com/data/tab/league/new/schedule?competition=8&date={date_str}" # 8 is Premier League ID usually
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        print(f"Status: {r.status_code}")
        # Print first match structure
        data = r.json()
        if 'list' in data and len(data['list']) > 0:
            print(json.dumps(data['list'][0], ensure_ascii=False, indent=2))
        else:
            print("No matches found in list, dumping keys:", data.keys())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_dqd()
