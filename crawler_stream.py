import requests
import re

def search_stream(team_name):
    print(f"Searching stream for: {team_name}")
    
    # Strategy 1: Search common aggregators (Simulated for safety/speed first)
    # Real scraping logic would go to specific sites.
    # For this prototype, I will verify if I can reach a known source index.
    
    # Example: Reddit Soccer Streams (fake url for demo logic)
    # url = f"https://soccerstreams.com/search/{team_name}"
    
    # Strategy 2: DQD / Leisu Web Page scraping
    # This is more reliable for Chinese users.
    
    # Let's try to fetch a DQD match page and look for "live_url"
    # This requires knowing the DQD Match ID.
    
    streams = []
    
    # Mocking the result of a successful crawl for now to prove UI integration
    # In real deployment, this function will contain requests + BeautifulSoup
    
    streams.append({"name": "源線路 1 (中文)", "url": "http://sample.com/live.m3u8"})
    streams.append({"name": "Source 2 (English)", "url": "http://sample.com/live2.m3u8"})
    
    return streams

if __name__ == "__main__":
    print(search_stream("Liverpool"))
