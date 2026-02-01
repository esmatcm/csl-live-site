import requests
try:
    r = requests.get("https://hsapi.xyz/bata.html")
    content = r.text
    if "m.home[CURRENT_LANG]" in content:
        print("PASS: JS Logic is Correct")
    else:
        print("FAIL: JS Logic is OLD")
        # Print a snippet to see what's there
        print(content[:500])
except Exception as e:
    print(e)
