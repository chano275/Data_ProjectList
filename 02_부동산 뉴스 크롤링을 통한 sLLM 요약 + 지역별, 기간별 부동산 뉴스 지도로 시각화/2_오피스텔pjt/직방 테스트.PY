import pandas as pd
import geohash2
import requests

# 동이름으로 위도 경도 구하기
addr = "망원동"
url = "https://apis.zigbang.com/v2/search"
params = {
    "leaseYn": "N",
    "q": addr,
    "serviceType": "원룸"
}
response = requests.get(url, params=params)

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
url = "https://apis.zigbang.com/v2/items"
params = {
    "deposit_gteq": 0,
    "domain": "zigbang",
    "geohash": geohash,
    "needHasNoFiltered": "true",
    "rent_gteq": 0,
    "sales_type_in": "전세|월세",
    "service_type_eq": "원룸"
}
response = requests.get(url, params=params)

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
    # 아이템 ID를 100개씩 분할하는 함수
    def chunk_list(lst, n):
        """리스트를 n개씩 분할"""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    all_datas = []
    chunk_size = 100  # 한 번에 요청할 아이템 수
    for chunk in chunk_list(ids, chunk_size):
        # 매물 아이디로 매물 정보 가져오기
        url = "https://apis.zigbang.com/v2/items/list"
        data = {
            "domain": "zigbang",
            "withCoalition": False,
            "item_ids": chunk
        }
        response = requests.post(url, json=data)

        # 상태 코드 및 응답 내용 확인
        if response.status_code == 200:
            try:
                datas = response.json().get("items", [])
                if not datas:
                    print("매물 데이터를 찾을 수 없습니다.")
                else:
                    print(f"총 {len(datas)}개의 매물을 찾았습니다.")
                    all_datas.extend(datas)
            except ValueError:
                print("응답 데이터를 JSON으로 변환할 수 없습니다.")
        else:
            print(f"매물 정보 가져오기 실패: {response.status_code}")
            print(f"응답 내용: {response.text}")

    # 모든 데이터를 DataFrame으로 변환
    if all_datas:
        df = pd.DataFrame(all_datas)
        print(df.tail(2))
    else:
        print("수집된 매물 데이터가 없습니다.")
else:
    print("매물 ID가 존재하지 않아서 요청을 진행할 수 없습니다.")
