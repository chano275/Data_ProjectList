import requests
import pandas as pd
import re
import difflib

# DataFrame 불러오기
df_news = pd.read_csv('./241022.csv')

# API 설정
API_KEY = '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'  # 실제 OpenAI API 키로 교체하세요.
MODEL = "gpt-3.5-turbo"

# OpenAI API 설정
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_key_location(article_content):
    """
    기사 내용에서 가장 중요한 지역명을 추출하는 함수.
    GPT-3.5와 GPT-4를 혼합하여 사용하여 정확도를 높입니다.
    """
    for model in ["gpt-3.5-turbo", "gpt-4"]:
        try:
            # 프롬프트 작성 (영어로 작성하여 모델의 지침 이해를 높임)
            prompt = f"""
From the following Korean news article, extract only the most important **location name** mentioned.

- Output **only the location name** in Korean, with no additional text.
- The location name should be in one of the following formats:
  - District or neighborhood in Seoul: "강남구", "송파동"
  - City of Seoul: "서울"
  - Other regions in Korea: "부산", "제주"
  - Foreign countries: "중국", "미국"
- If there is no relevant location, output "N/A".

News article:
{article_content[:500]}
"""

            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 5,
                "temperature": 0.0
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            location = response.json()['choices'][0]['message']['content'].strip()

            # 결과가 유효한 경우 반환
            if location:
                return location
        except Exception as e:
            print(f"Error with model {model}: {e}")
            continue
    return "N/A"

def classify_location(location):
    """
    지역명을 받아 대분류 및 세부 지역명을 결정하는 함수.
    """
    location = location.strip()
    if location == "N/A":
        return "N/A", "N/A"

    seoul_districts = [
        '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구',
        '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구',
        '용산구', '은평구', '종로구', '중구', '중랑구'
    ]
    seoul_neighborhoods = re.compile(r'.{2,5}동$')  # 2~5글자로 끝이 '동'인 경우
    overseas_countries = ['미국', '일본', '중국', '독일', '프랑스', '홍콩']

    # 문자열 유사도 측정으로 오탈자 보정
    possible_locations = ['서울'] + seoul_districts + overseas_countries
    match = difflib.get_close_matches(location, possible_locations, n=1, cutoff=0.8)
    if match:
        location = match[0]

    if location in seoul_districts or seoul_neighborhoods.match(location):
        return "서울", location
    elif location == "서울":
        return "서울", location
    elif location in overseas_countries:
        return "해외", location
    else:
        return "서울 외", location

# 'Key_Location' 및 'Location_Category' 컬럼 추가
key_locations = []
location_categories = []
for content in df_news['Content']:
    key_location = get_key_location(content)
    key_locations.append(key_location)
    category, detailed_location = classify_location(key_location)
    location_categories.append(category)

# 데이터프레임에 값 추가
df_news['Key_Location'] = key_locations
df_news['Location_Category'] = location_categories

# 결과를 CSV 파일로 저장
df_news.to_csv(f'./241022___{MODEL}.csv', encoding='utf-8-sig', index=False)

print("Location extraction and classification complete. DataFrame saved.")
