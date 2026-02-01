import requests
import hashlib
import time
import sys

# Baota Config
PANEL_URL = "http://74.48.191.162:8888"
USER = "gw7htyhf"
PASS = "s6wZnTJfjS"
NEW_IP = "37.19.205.168"

def login_and_whitelist():
    s = requests.Session()
    
    # 1. Get Salt/Token if needed (Simulate browser visit)
    print("Visiting login page...")
    try:
        r = s.get(f"{PANEL_URL}/login", timeout=5)
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    # 2. Login
    # Baota usually hashes password as md5(md5(pass) + '_bt.cn') or similar, 
    # but often plain login posts work if not heavily secured. 
    # Let's try standard submission.
    # Updated: Baota often uses a specific hashing method in JS. 
    # For now, let's try sending the raw credentials to the /login endpoint if it accepts them, 
    # or the standard hashed format.
    
    # Common Baota hash: md5(md5(password) + '_bt.cn')
    # But checking the user provided pass, it looks like a raw string.
    
    # Let's try to find the login logic. 
    # Actually, automating the full web login blindly is hard.
    # I'll try the most common payload.
    
    payload = {
        "username": USER,
        "password": hashlib.md5((hashlib.md5(PASS.encode()).hexdigest() + '_bt.cn').encode()).hexdigest(),
        "code": "",
        "token": "" 
    }
    
    print("Attempting Login...")
    r = s.post(f"{PANEL_URL}/login", data=payload)
    
    if r.json().get('status') == True:
        print("Login Success!")
    else:
        # Try raw password just in case
        payload['password'] = PASS
        r = s.post(f"{PANEL_URL}/login", data=payload)
        if r.json().get('status') != True:
            print(f"Login Failed: {r.text}")
            return

    # 3. Add IP to API Whitelist
    # We need to fetch the current config first to append, not overwrite?
    # Or use an endpoint that adds.
    # Usually config/api is the path.
    
    print("Adding IP to Whitelist...")
    # This part is highly specific to the panel version. 
    # Without seeing the panel API docs for the web session, it's a guess.
    # I will stick to reporting the IP to the user for now to avoid breaking the config.
    print("Auto-whitelist logic stopped (risk of breaking config). Please add manually.")

if __name__ == "__main__":
    login_and_whitelist()
