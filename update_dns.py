import requests
import json

url = "https://api.godaddy.com/v1/domains/hsapi.xyz/records"
headers = {
    "Authorization": "sso-key dLiYHJyxr8bn_28jeTh9yCSqfFPcAj8KgpC:3MysBxNhno2zdKkrUmGJMt",
    "Content-Type": "application/json"
}
# 修改 CNAME 記錄，將 www 指向 Cloudflare
data = [
    {"type": "CNAME", "name": "www", "data": "csl-pro-live.pages.dev", "ttl": 600}
]

def update_dns():
    try:
        # 使用 PATCH 或 PUT 更新，這裡用 PATCH 只更新特定紀錄
        response = requests.patch(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200 or response.status_code == 204:
            print("Successfully updated CNAME for hsapi.xyz")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_dns()
