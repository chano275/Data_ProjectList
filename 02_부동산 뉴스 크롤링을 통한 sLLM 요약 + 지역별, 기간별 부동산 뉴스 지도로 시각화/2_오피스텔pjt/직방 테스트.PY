import pandas as pd
import geohash2
import requests

# 동이름으로 위도 경도 구하기
addr = "망원동"
url = f"https://apis.zigbang.com/v2/search?leaseYn=N&q={addr}&serviceType=원룸"
response = requests.get(url)

if response.status_code == 200:
    data = response.json().get("items", [])
    if data:
        lat, lng = data[0]["lat"], data[0]["lng"]  # 위도, 경도
        print(f"위도: {lat}, 경도: {lng}")
    else:
        print("검색 결과가 없습니다.")
else:
    print(f"위도 경도 가져오기 실패: {response.status_code}")
    print(f"응답 내용: {response.text}")

# 위도 경도로 geohash 알아내기 / precision이 커질수록 영역이 작아짐
geohash = geohash2.encode(lat, lng, precision=5)
print(f"Geohash: {geohash}")

# geohash로 매물 아이디 가져오기
url = f"https://apis.zigbang.com/v2/items?deposit_gteq=0&domain=zigbang\
&geohash={geohash}&needHasNoFiltered=true&rent_gteq=0&sales_type_in=전세|월세\
&service_type_eq=원룸"
response = requests.get(url)

if response.status_code == 200:
    datas = response.json().get("items", [])
    if datas:
        ids = [data["item_id"] for data in datas]  # item_id 추출
        print(f"매물 ID 개수: {len(ids)}")
        print(f"첫 5개 ID: {ids[:5]}")
    else:
        print("해당 지역에서 매물을 찾을 수 없습니다.")
else:
    print(f"매물 ID 가져오기 실패: {response.status_code}")
    print(f"응답 내용: {response.text}")

# 매물 ID가 존재하는지 확인 후 진행
if 'ids' in locals() and ids:
    # 매물 아이디로 매물 정보 가져오기
    url = "https://apis.zigbang.com/v2/items/list"
    # params가 아닌 json 키워드를 사용해서 데이터를 전달
    data = {
        "domain": "zigbang",
        "withCoalition": False,  # 불리언 값으로 올바르게 전달됨
        "item_ids": ids
    }
    response = requests.post(url, json=data)  # json 키워드를 사용하여 데이터 전송
    
    # 상태 코드 및 응답 내용 확인
    if response.status_code == 200:
        try:
            datas = response.json().get("items", [])
            if not datas:
                print("매물 데이터를 찾을 수 없습니다.")
            else:
                print(f"총 {len(datas)}개의 매물을 찾았습니다.")
                df = pd.DataFrame(datas)
                print(df.tail(2))
        except ValueError:
            print("응답 데이터를 JSON으로 변환할 수 없습니다.")
    else:
        print(f"매물 정보 가져오기 실패: {response.status_code}")
        print(f"응답 내용: {response.text}")
else:
    print("매물 ID가 존재하지 않아서 요청을 진행할 수 없습니다.")
