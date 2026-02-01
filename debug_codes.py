import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = '735d0b4e485a431db7867a42b0dda855'
BASE_URL = "https://api.football-data.org/v4/matches"
HEADERS = {'X-Auth-Token': API_KEY}

def check():
    try:
        r = requests.get(BASE_URL, headers=HEADERS)
        matches = r.json().get('matches', [])
        print(f"Total Matches Found: {len(matches)}")
        
        codes = set()
        for m in matches:
            c = m['competition']['code']
            n = m['competition']['name']
            codes.add(f"{c} ({n})")
            
        print("Available League Codes:", codes)
        
    except Exception as e:
        print(e)

check()
