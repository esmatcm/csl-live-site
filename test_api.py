import requests

def test_api():
    token = "735d0b4e485a431db7867a42b0dda855"
    headers = {"X-Auth-Token": token}
    leagues = ["PL", "PD", "SA", "BL1", "FL1"]
    
    for lg in leagues:
        url = f"https://api.football-data.org/v4/competitions/{lg}/standings"
        try:
            r = requests.get(url, headers=headers)
            print(f"League {lg}: Status {r.status_code}")
            if r.status_code != 200:
                print(f"Response: {r.text}")
        except Exception as e:
            print(f"Error {lg}: {e}")

if __name__ == "__main__":
    test_api()
