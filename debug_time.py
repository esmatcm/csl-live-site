import requests
from datetime import datetime, timedelta
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
HEADERS = {'X-Auth-Token': API_KEY}

def check_time():
    r = requests.get("https://api.football-data.org/v4/matches", headers=HEADERS)
    matches = r.json().get('matches', [])
    
    print(f"Checking {len(matches)} matches...")
    for m in matches:
        # Find Liverpool or specific team
        h = m['homeTeam']['shortName'] or ""
        a = m['awayTeam']['shortName'] or ""
        
        if "Liverpool" in h or "Newcastle" in a:
            utc = m['utcDate']
            # Parse
            dt = datetime.strptime(utc, "%Y-%m-%dT%H:%M:%SZ")
            
            # Calc
            bj = dt + timedelta(hours=8)
            bj_plus_1 = dt + timedelta(hours=9)
            
            print(f"Match: {h} vs {a}")
            print(f"Raw UTC: {utc}")
            print(f"UTC+8 (Standard BJ): {bj.strftime('%H:%M')}")
            print(f"UTC+9 (Correction):  {bj_plus_1.strftime('%H:%M')}")
            return

check_time()
