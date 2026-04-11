import json
import urllib.request
import re
import bs4

def get_apollo_state(place_id):
    req_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
    req = urllib.request.Request(req_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac)'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    soup = bs4.BeautifulSoup(html, 'html.parser')
    for s in soup.find_all('script'):
        if s.string and '__APOLLO_STATE__' in s.string:
            m = re.search(r'window\.__APOLLO_STATE__\s*=\s*({.*?});', s.string)
            if m:
                return json.loads(m.group(1))
    return None

data = get_apollo_state("2024395337")

root_query = data.get("ROOT_QUERY", {})
for k, v in root_query.items():
    if isinstance(v, dict) and k.startswith("placeDetail"):
        for sub_k, sub_v in v.items():
            if sub_k.startswith("newBusinessHours") and isinstance(sub_v, list):
                for cat in sub_v:
                    days = cat.get("businessHours", [])
                    for day_info in days:
                        if day_info.get("day") == "월":
                            print("MONDAY INFO:")
                            print(json.dumps(day_info, indent=2, ensure_ascii=True))

