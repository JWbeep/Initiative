import re
import json
import requests
from bs4 import BeautifulSoup

def get_place_info_from_url(url):
    """
    네이버 지도 URL에서 장소의 주차, 영업시간, 전화번호를 추출합니다.
    (실패 시 None을 반환하거나 부분 데이터를 반환합니다)
    """
    # 1. URL에서 장소 ID 추출
    match = re.search(r'/place/(\d+)', url)
    if not match:
        return {"error": "URL에서 장소 ID를 찾을 수 없습니다."}
    
    place_id = match.group(1)
    req_url = f"https://m.place.naver.com/restaurant/{place_id}/home"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        response = requests.get(req_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"네이버 페이지 요청 실패 (상태 코드: {response.status_code})"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Apollo State 추출 (정적 데이터)
        apollo_state_json = None
        for s in soup.find_all('script'):
            if s.string and 'window.__APOLLO_STATE__' in s.string:
                m = re.search(r'window\.__APOLLO_STATE__\s*=\s*({.*?});', s.string)
                if m:
                    apollo_state_json = m.group(1)
                    break
        
        if not apollo_state_json:
            return {"error": "페이지 내장 데이터를 찾을 수 없습니다."}
        
        data = json.loads(apollo_state_json)
        
        # 'PlaceDetailBase'로 시작하는 키에서 정보 추출
        base_key = f"PlaceDetailBase:{place_id}"
        base_data = data.get(base_key)
        
        # 만약 카테고리가 달라서 키가 다르게 저장되어 있을 경우 대비 (예: PlaceDetailBase, HairshopDetailBase 등)
        if not base_data:
            for k in data.keys():
                if k.endswith(f":{place_id}") and "DetailBase" in k:
                    base_data = data[k]
                    break
                    
        if not base_data:
            return {"error": f"장소({place_id}) 상세 데이터를 파싱할 수 없습니다."}

        # --- 정보 추출 ---
        # 1. 전화번호
        phone = base_data.get('virtualPhone') or base_data.get('phone') or ""
        
        # 2. 주차 및 찾아가는길 상세 정보
        conveniences = base_data.get('conveniences') or []
        parking_info_arr = []
        if "주차" in conveniences:
            parking_info_arr.append("주차 가능")
            
        parking_support = base_data.get('parkingSupport')
        if parking_support:
            parking_info_arr.append(f"주차 지원: {parking_support}")
            
        road_desc = base_data.get('road')
        if road_desc:
            parking_info_arr.append(f"찾아가는 길/주차 안내: {road_desc}")
            
        parking = "\n".join(parking_info_arr) if parking_info_arr else "정보 없음"
        
        # 3. 영업시간 (BusinessHours) - 다양한 형태 대비
        biz_hour = "정보 없음"
        biz_hour_list = []
        
        # ROOT_QUERY.placeDetail.newBusinessHours 파싱 (최신 네이버 지도 구조)
        root_query = data.get("ROOT_QUERY", {})
        for k, v in root_query.items():
            if isinstance(v, dict) and k.startswith("placeDetail"):
                for sub_k, sub_v in v.items():
                    if sub_k.startswith("newBusinessHours") and isinstance(sub_v, list):
                        for cat in sub_v:
                            cat_name = cat.get("name")
                            days = cat.get("businessHours", [])
                            for day_info in days:
                                day = day_info.get("day", "")
                                hours = day_info.get("businessHours", {})
                                if not hours: continue
                                start = hours.get("start", "")
                                end = hours.get("end", "")
                                
                                b_str = ""
                                breaks = day_info.get("breakHours", [])
                                if breaks:
                                    b_str = f" (휴게시간 {breaks[0].get('start', '')}~{breaks[0].get('end', '')})"
                                    
                                l_str = ""
                                last_orders = day_info.get("lastOrderTimes", [])
                                if last_orders and isinstance(last_orders, list):
                                    l_times = [l.get('time') for l in last_orders if l.get('time')]
                                    if l_times:
                                        l_str = f" ({', '.join(l_times)} 라스트오더)"
                                    
                                if cat_name:
                                    biz_hour_list.append(f"[{cat_name}] {day} {start}~{end}{b_str}{l_str}")
                                else:
                                    biz_hour_list.append(f"{day} {start}~{end}{b_str}{l_str}")

        if biz_hour_list:
            biz_hour = ", ".join(biz_hour_list)
        elif base_data.get('businessHours'):
            biz_hour = str(base_data.get('businessHours'))
        
        return {
            "parking": parking,
            "bizHour": biz_hour,
            "phone": phone
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"네트워크 요청 오류 발생: {str(e)}"}
    except Exception as e:
        return {"error": f"파싱 중 오류 발생: {str(e)}"}
