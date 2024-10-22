import requests
import pandas as pd

API_KEY = "a37371ce58e94e428609"  # 인증키
token = '68b273f7-7886-485e-9da0-c066c0bec9ea'  # 토큰
YEAR = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022']  # 연도
GENDER = ['1', '2']  # 성별: 전체, 남성, 여성
ADM_CD = ['11', '21', '22', '23', '24', '25', '26', '29', '31', '32', '33', '34', '35', '36', '37', '38', '39']
AGE_TYPE = ['31', '32', '33', '34', '35', '36', '40']  # 연령 구분 - 10대 / 20대 / 30대 / 40대 / 50대 / 60대 / 70대 이상

data = []  # 수집할 데이터 리스트 초기화

# API 호출
url = f"https://sgisapi.kostat.go.kr/OpenAPI3/stats/searchpopulation.json"
for i in range(len(YEAR)):  # 원하는 대로 df를 만들기 위한 for문
    print(i)
    for j in range(len(AGE_TYPE)):
        for p in range(2):  # 남성, 여성만 사용
            for q in range(len(ADM_CD)):

                params = {  # 넣을 params
                    'year': YEAR[i],
                    'gender': GENDER[p],
                    'adm_cd': ADM_CD[q],
                    'low_search': '0',
                    'age_type': AGE_TYPE[j],
                    'accessToken': token
                }

                response = requests.get(url, params=params)

                if response.status_code == 200:
                    ret = response.json()

                    if 'result' in ret:                    # 성공적으로 데이터를 수집한 경우
                        for result in ret['result']:
                            data.append({                            # 수집된 데이터를 리스트에 저장
                                'year': params['year'],
                                'gender': params['gender'],
                                'age_type': params['age_type'],
                                'adm_nm': result['adm_nm'],
                                'population': result['population']
                            })

                else:
                    print(f"오류 발생: 상태 코드 {response.status_code}")
                    print("응답 내용:", response.content)

df = pd.DataFrame(data)  # 데이터를 DataFrame으로 변환
df['gender'] = df['gender'].replace({'1': '남성', '2': '여성'})  # 성별을 '남성', '여성'으로 변환

# 인구 증감 계산 (이전 연도와 비교)
df['population'] = df['population'].astype(int)
df['year'] = df['year'].astype(int)
df = df.sort_values(by=['adm_nm', 'gender', 'age_type', 'year'])  # 데이터 정렬
df['population_diff'] = df.groupby(['adm_nm', 'gender', 'age_type'])['population'].diff()  # 이전 연도와의 인구 차이 계산
df.to_csv('population_data_with_differences.csv', index=False, encoding='utf-8-sig')  # 결과 출력

print('finished!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')