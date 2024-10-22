import requests
import pandas as pd
import re

# DataFrame 불러오기
df_news = pd.read_csv('./241022.csv')

API_KEY = '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'
MODEL = "gpt-4o-mini"

# OpenRouter API 설정
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def classify_location(location):
    """
    지역명을 받아 대분류 및 세부 지역명을 결정하는 함수.
    """
    seoul_districts = [
        '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구',
        '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구',
        '용산구', '은평구', '종로구', '중구', '중랑구'
    ]
    seoul_neighborhoods = re.compile(r'.{2,5}동$')  # 2~5글자로 끝이 '동'인 경우

    if any(district == location for district in seoul_districts):
        return "서울", location
    elif seoul_neighborhoods.match(location):
        return "서울", location
    elif '서울' == location:
        return "서울", location
    elif location == "해외":
        return "해외", location
    else:
        return "서울 외", location

def get_key_location(article_content):
    """
    기사 내용에서 가장 중요한 지역명을 추출하는 함수.
    """
    try:
        # 프롬프트 수정: 오직 지역명만 출력하도록 지시
        prompt = f"""
        다음 한국어 기사에서 가장 중요한 **지역명 하나만** 추출하고, 다음 형식에 따라 출력하세요.

        - **오직 지역명만** 한글로 출력하고, 다른 텍스트는 포함하지 마세요.
        - 지역명은 아래와 같은 형태로만 출력하세요:
          - 서울특별시의 구나 동: "[구 이름]", "[동 이름]" (예: "강남구", "송파동")
          - 서울특별시 전체: "서울"
          - 서울특별시 외의 국내 지역: "[지역 이름]" (예: "부산", "제주", "경기도")
          - 해외 지역: "[해외 지역 이름]" (예: "중국", "미국", "일본")
        - **출력은 한 줄로 하며, 줄바꿈이나 공백, 추가 문자 없이 지역명만 포함해야 합니다.**
        - **유사한 이름을 혼동하지 마세요. 예를 들어, "중국"과 "중구"는 다릅니다.**
        - 해당하는 지역명이 없으면 "N/A"를 출력하세요.

        또한, 다음 규칙에 따라 추가 필드를 출력하세요:
        - 서울특별시 내의 구나 동이 나올 경우, Key_Location 필드에 해당 구나 동 이름을 출력하고, Location_Category 필드에 "서울"을 출력하세요.
        - 서울특별시 전체가 나올 경우, Key_Location 필드에 "서울"을 출력하고, Location_Category 필드에 "서울"을 출력하세요.
        - 서울특별시 외의 국내 지역이 나올 경우, Key_Location 필드에 해당 지역 이름을 출력하고, Location_Category 필드에 "서울 외 국내"를 출력하세요.
        - 해외 지역이 나올 경우, Key_Location 필드에 해당 지역 이름을 출력하고, Location_Category 필드에 "해외"를 출력하세요.
        - 해당 지역명이 없으면, Key_Location 필드에 "N/A"를 출력하고, Location_Category 필드에 "N/A"를 출력하세요.

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

# 'Key_Location' 및 'Location_Category' 컬럼 추가
key_locations = []
location_categories = []
for content in df_news['Content']:  # 전체 기사에 대해 적용
    key_location = get_key_location(content)
    key_locations.append(key_location)
    category, detailed_location = classify_location(key_location)
    location_categories.append(category)

# 데이터프레임에 값 추가
df_news['Key_Location'] = key_locations
df_news['Location_Category'] = location_categories

# 결과를 CSV 파일로 저장
df_news.to_csv(f'./241022_{MODEL}.csv', encoding='utf-8-sig', index=False)

print("Location extraction and classification complete. DataFrame saved.")
