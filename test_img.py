import requests
import os

def test_download():
    url = "https://n.sinaimg.cn/sports/transform/233/w650h383/20250608/e753-1579d460e53a793c14d93021f158586d.jpg" # Example from a real Sina article
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://sports.sina.com.cn/'
    }
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}, Length: {len(r.content)}")
    with open("csl-live-site/img_cache/test_real.jpg", "wb") as f:
        f.write(r.content)

if __name__ == "__main__":
    test_download()
