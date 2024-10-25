import requests
import pandas as pd
import re
from datetime import datetime
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os


def get_unique_filename(filename):  # 파일명이 이미 존재하면 '_'를 추가하는 함수
    base, extension = os.path.splitext(filename)
    while os.path.exists(filename):
        base += '_'
        filename = base + extension
    return filename


def get_key_location(article_content):
    """    기사 내용에서 가장 중요한 지역명을 추출하는 함수.    """
    try:
        prompt = f"""
        다음 한국어 기사에서 가장 중요한 **지역명 하나만** 추출하고, 다음 형식에 따라 출력하세요.

        - **오직 지역명만** 한글로 출력하고, 다른 텍스트는 포함하지 마세요.
        - 지역명은 아래와 같은 형태로만 출력하세요:
          - 서울특별시의 구나 동: 구 이름, 동 이름 (예: 강남구, 송파동)
          - 서울특별시 전체: 서울
          - 서울특별시 외의 국내 지역: 지역 이름 (예: 부산, 제주, 경기도)
          - 해외 지역: 해외 지역 이름 (예: 중국, 미국, 일본)
        - **출력은 한 줄로 하며, 줄바꿈이나 공백, 추가 문자 없이 지역명만 포함해야 합니다.**
        - **유사한 이름을 혼동하지 마세요. 예를 들어, "중국"과 "중구"는 다릅니다.**
        - 해당하는 지역명이 없으면 "N/A"를 출력하세요.

        기사 내용:
        {article_content[:500]}
        """

        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 5,  # 응답을 짧게 제한
            "temperature": 0  # 응답의 일관성을 높이기 위해 온도 낮춤
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()  # 응답이 오류인 경우 예외 발생

        # 응답에서 텍스트 추출
        location = response.json()['choices'][0]['message']['content'].strip()
        return location
    except Exception as e:
        print(f"Error extracting location: {e}")
        return "N/A"


#############################################################################################################

geolocator = Nominatim(user_agent="geoapiExercises")                                    # 지오코더 초기화
today = datetime.now().strftime("%y%m%d")                                               # 오늘 날짜를 6글자로 가져오기 (YYMMDD 형식)
df_news = pd.read_csv(f'./{today}.csv')


API_KEY = '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'
MODEL = "gpt-4o-mini"
SAVE_LINK = f'./{today}_{MODEL}.csv'                                                    # 저장할 파일명 설정
SAVE_LINK = get_unique_filename(SAVE_LINK)                                              # SAVE_LINK 업데이트

headers = {  # OpenRouter API 설정
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

seoul_districts = [  # 서울특별시 구 리스트와 동 이름에 대한 패턴을 글로벌 스코프로 이동
    '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구',
    '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구',
    '용산구', '은평구', '종로구', '중구', '중랑구'
]
seoul_neighborhoods = re.compile(r'.{2,5}동$')  # 2~5글자로 끝이 '동'인 경우

locations_cache = {}  # 위치 정보 캐시를 위한 딕셔너리 초기화
key_locations, latitudes, longitudes = [], [], []  # 'Key_Location' 및 위도, 경도 컬럼 추가

for content in df_news['Content']:  # 전체 기사에 대해 적용
    key_location = get_key_location(content)
    key_locations.append(key_location)

    # 위도와 경도 가져오기
    if key_location != "N/A":
        if key_location in locations_cache:  latitude, longitude = locations_cache[key_location]           # 캐시에서 위치 정보 가져오기
        else:
            try:  # 주소 생성
                address = key_location
                if key_location in seoul_districts:             address += ', 서울특별시, 대한민국'
                elif seoul_neighborhoods.match(key_location):   address += ', 서울특별시, 대한민국'
                elif key_location == '서울':                     address = '서울특별시, 대한민국'
                else:                                           address += ', 대한민국'

                location = geolocator.geocode(address, timeout=10)                                         # 위치 정보 가져오기

                if location:
                    latitude, longitude = location.latitude, location.longitude
                    locations_cache[key_location] = (latitude, longitude)                                  # 캐시에 저장
                else:
                    print(f"Location not found for: {key_location}")
                    latitude, longitude = '', ''
            except GeocoderTimedOut:
                print(f"Geocoding timed out for location: {key_location}")
                latitude, longitude = '', ''
            except Exception as e:
                print(f"Error geocoding location {key_location}: {e}")
                latitude, longitude = '', ''
            time.sleep(1)                                                                                  # API 요청 사이에 딜레이 추가
    else:
        latitude, longitude = '', ''

    latitudes.append(latitude)
    longitudes.append(longitude)

df_news['Key_Location'], df_news['latitude'], df_news['longitude'] = key_locations, latitudes, longitudes  # 데이터프레임에 값 추가
df_news.to_csv(SAVE_LINK, encoding='utf-8-sig', index=False)                                               # 결과를 CSV 파일로 저장
print("Location extraction and geocoding complete. DataFrame saved as:", SAVE_LINK)
