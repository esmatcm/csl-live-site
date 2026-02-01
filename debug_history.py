import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_history():
    try:
        r = requests.get("https://hsapi.xyz/data_v60.json?t=" + str(time.time()))
        data = r.json()
        
        print("Checking HISTORY matches...")
        count = 0
        for m in data:
            if m['statusRaw'] in ['FINISHED', 'FT']:
                # Check if translation exists (i.e. tc != en)
                home_en = m['home']['en']
                home_tc = m['home']['tc']
                
                if home_en == home_tc:
                    print(f"[MISSING TRANSLATION] {home_en}")
                else:
                    # print(f"[OK] {home_tc}")
                    pass
                count += 1
                
        print(f"Checked {count} finished matches.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import time
    check_history()
