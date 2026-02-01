import requests
import hashlib
import time
import sys
import re

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

PANEL_URL = "http://74.48.191.162:8888"
USER = "gw7htyhf"
PASS = "s6wZnTJfjS"

# We suspect the path might be wrong, so let's try to FIND it first.
# Common paths to check
PATHS_TO_CHECK = [
    "/www/wwwroot/hsapi.xyz/index.html",
    "/www/wwwroot/hsapi/index.html",
    "/www/wwwroot/default/index.html",
    "/www/wwwroot/hsapi.xyz/public/index.html"
]

def login_and_push():
    s = requests.Session()
    
    # 1. Login
    print("Logging in...")
    # Standard Baota Login Flow simulation
    # Usually: POST /login with username, password (md5(md5(pass)+'_bt.cn')), code, token
    
    # Calculate hash
    # md5(md5(pass) + '_bt.cn')
    m5 = hashlib.md5()
    m5.update(PASS.encode('utf-8'))
    p1 = m5.hexdigest()
    
    m5 = hashlib.md5()
    m5.update((p1 + '_bt.cn').encode('utf-8'))
    p_final = m5.hexdigest()
    
    payload = {
        "username": USER,
        "password": p_final,
        "code": "",
        "token": ""
    }
    
    try:
        r = s.post(f"{PANEL_URL}/login", data=payload, timeout=10)
        if r.json().get('status') == True:
            print("Login Success!")
        else:
            print(f"Login Failed: {r.text}")
            # Try raw password fallback
            payload['password'] = PASS
            r = s.post(f"{PANEL_URL}/login", data=payload)
            if r.json().get('status') == True:
                print("Raw Password Login Success!")
            else:
                print("All login attempts failed.")
                return
    except Exception as e:
        print(f"Login Error: {e}")
        return

    # 2. Find Correct Path (GetDir)
    # We list /www/wwwroot to see what's there
    print("Listing directories...")
    try:
        # Web API for files doesn't need signature, just cookie
        r = s.post(f"{PANEL_URL}/files?action=GetDir&tojs=GetFiles&p=1&showRow=200&path=/www/wwwroot")
        data = r.json()
        target_path = ""
        
        if 'DIR' in data:
            print(f"Found Directories: {data['DIR']}")
            # Smart guess: look for 'hsapi'
            for d in data['DIR']:
                d_name = d.split(';')[-1] if ';' in d else d # Baota sometimes returns mode;size;name
                # Actually Baota JSON DIR is usually list of strings "dirname;chmod;owner;..."
                # Let's just print and see.
                pass
        
        # Assume we found it or stick to hsapi.xyz if it exists
        # Let's try to push to /www/wwwroot/hsapi.xyz/index.html via session
        
        print("Pushing to /www/wwwroot/hsapi.xyz/index.html via Session...")
        html = "<html><body><h1>Session Push Success!</h1><p>Time: " + str(time.time()) + "</p></body></html>"
        
        payload_file = {
            'path': '/www/wwwroot/hsapi.xyz/index.html',
            'data': html,
            'encoding': 'utf-8'
        }
        r = s.post(f"{PANEL_URL}/files?action=SaveFileBody", data=payload_file)
        print(f"Push Response: {r.text}")
        
    except Exception as e:
        print(f"File Op Error: {e}")

if __name__ == "__main__":
    login_and_push()
