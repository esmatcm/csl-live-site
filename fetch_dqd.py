import requests
import json
import time

# Dongqiudi API (Mobile Interface)
BASE_URL = "https://api.dongqiudi.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Referer': 'https://m.dongqiudi.com/'
}

def fetch_match_detail(match_id_dqd):
    # This ID must be mapped from our FD match ID.
    # For now, we search by team names to find the DQD ID.
    # This is the tricky part: Mapping FD ID -> DQD ID.
    pass

def search_match(home_name, away_name, date_str):
    # Search DQD for matches on this day
    # API: https://api.dongqiudi.com/data/tab/new/important?date=2024-02-01
    try:
        url = f"{BASE_URL}/data/tab/new/important?date={date_str}"
        r = requests.get(url, headers=HEADERS, timeout=5)
        data = r.json()
        
        for match in data.get('list', []):
            h = match['home_team_name']
            a = match['away_team_name']
            # Fuzzy match logic
            if (home_name in h or h in home_name) and (away_name in a or a in away_name):
                return {
                    "id": match['match_id'],
                    "home_score": match['fs_h'],
                    "away_score": match['fs_a'],
                    "status": match['status'],
                    "minute": match.get('minute'),
                    "events": [] # We would fetch events from detail endpoint next
                }
    except Exception as e:
        print(f"DQD Search Error: {e}")
    return None

# Test Run
if __name__ == "__main__":
    # Test searching for a known match (e.g. Liverpool vs Newcastle today/tomorrow)
    # Note: DQD uses Beijing Time for dates usually.
    today = time.strftime("%Y-%m-%d")
    print(f"Searching matches for {today}...")
    res = search_match("利物浦", "纽卡斯尔", today) # Use Simplified Chinese for search
    print(res)
