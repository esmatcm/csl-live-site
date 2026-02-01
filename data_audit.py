import requests
import json
import time

API_KEY = '735d0b4e485a431db7867a42b0dda855'
HEADERS = {'X-Auth-Token': API_KEY}
BASE_URL = "https://api.football-data.org/v4"

def audit_data():
    report = {}
    
    print("1. 測試 Football-Data API (Matches)...")
    try:
        r = requests.get(f"{BASE_URL}/matches", headers=HEADERS, timeout=10)
        data = r.json()
        matches = data.get('matches', [])
        report['match_count'] = len(matches)
        
        if matches:
            sample = matches[0]
            # 檢查詳細欄位是否存在
            report['sample_match'] = {
                'id': sample['id'],
                'status': sample['status'],
                'has_score': 'fullTime' in sample['score'],
                'has_referees': len(sample.get('referees', [])) > 0,
                # 關鍵檢查點
                'has_lineups': 'lineups' in sample and len(sample['lineups']) > 0, 
                'has_stats': 'statistics' in sample and len(sample['statistics']) > 0,
                'has_goals': 'goals' in sample and len(sample['goals']) > 0,
                'area': sample['area']['name'],
                'competition': sample['competition']['name']
            }
        else:
            report['sample_match'] = "No matches found today"
            
    except Exception as e:
        report['match_api_error'] = str(e)

    print("2. 測試 Football-Data API (Detail Mock)...")
    # 嘗試抓取一個已結束的比賽 (例如上次的測試 ID) 看是否有更多細節
    try:
        # 使用一個已知的英超比賽 ID (假設) 或者直接看剛剛抓到的 ID
        if matches:
             test_id = matches[0]['id']
             r = requests.get(f"{BASE_URL}/matches/{test_id}", headers=HEADERS, timeout=10)
             detail = r.json()
             report['detail_api_check'] = {
                 'match_id': test_id,
                 'has_lineups': len(detail.get('lineups', [])) > 0,
                 'has_stats': len(detail.get('statistics', [])) > 0,
                 'has_events': len(detail.get('goals', [])) > 0, # 免費版通常只有 goals
                 'raw_keys': list(detail.keys())
             }
    except Exception as e:
        report['detail_api_error'] = str(e)

    print("3. 測試 News API (Dongqiudi)...")
    try:
        dqd_url = "https://api.dongqiudi.com/app/tabs/iphone/1.json"
        r = requests.get(dqd_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        news = r.json()
        articles = news.get('articles', [])
        report['news_count'] = len(articles)
        if articles:
            sample_news = articles[0]
            report['sample_news'] = {
                'title': sample_news.get('title'),
                'has_thumb': bool(sample_news.get('thumb')),
                'has_description': bool(sample_news.get('description')),
                'share_url': sample_news.get('share'),
                'raw_keys': list(sample_news.keys())
            }
    except Exception as e:
        report['news_api_error'] = str(e)

    print("\n====== DATA AUDIT REPORT ======")
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    audit_data()
