import requests
import xml.etree.ElementTree as ET
import pandas as pd

# API 기본 설정 / 발급받은 API 키 / API 엔드포인트
API_KEY = '발급받은 API_KEY를 입력하세요'
ENDPOINT = 'https://apis.data.go.kr/1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade'

# 서울특별시의 모든 구에 대한 LAWD_CD 목록
seoul_gu_codes = [
    '11110',  # 종로구
    '11140',  # 중구
    '11170',  # 용산구
    '11200',  # 성동구
    '11215',  # 광진구
    '11230',  # 동대문구
    '11260',  # 중랑구
    '11290',  # 성북구
    '11305',  # 강북구
    '11320',  # 도봉구
    '11350',  # 노원구
    '11380',  # 은평구
    '11410',  # 서대문구
    '11440',  # 마포구
    '11470',  # 양천구
    '11500',  # 강서구
    '11530',  # 구로구
    '11545',  # 금천구
    '11560',  # 영등포구
    '11590',  # 동작구
    '11620',  # 관악구
    '11650',  # 서초구
    '11680',  # 강남구
    '11710',  # 송파구
    '11740',  # 강동구
]

# 요청 파라미터 기본 설정
params = {
    'DEAL_YMD': '202308',  # 거래 연월 (예: 2023년 8월)
    'serviceKey': API_KEY,  # API 키
    'numOfRows': 1000,  # 한 페이지당 가져올 데이터 수 (최대 1000)
    'pageNo': 1  # 페이지 번호
}

# 모든 데이터를 저장할 리스트 초기화
all_data = []

# 각 구의 데이터를 조회하여 수집
for lawd_cd in seoul_gu_codes:
    params['LAWD_CD'] = lawd_cd  # 현재 구의 LAWD_CD 설정
    params['pageNo'] = 1  # 페이지 번호 초기화

    while True:
        # API 요청
        response = requests.get(ENDPOINT, params=params)

        # 응답 데이터 확인
        if response.status_code == 200:
            try:
                # XML 데이터를 파싱
                root = ET.fromstring(response.content)

                # 오류 메시지 확인
                result_code = root.find('.//resultCode').text
                if result_code != '00':
                    result_msg = root.find('.//resultMsg').text
                    print(f"오류 발생 (LAWD_CD: {lawd_cd}): {result_msg}")
                    break

                # 총 건수와 페이지당 건수 확인
                totalCount = int(root.find('.//totalCount').text)
                numOfRows = int(root.find('.//numOfRows').text)
                pageNo = int(root.find('.//pageNo').text)

                # 각 item 요소를 순회하며 데이터 추출
                items = root.findall('.//item')
                for item in items:
                    item_data = {}
                    for child in item:
                        item_data[child.tag] = child.text
                    all_data.append(item_data)

                # 모든 페이지를 다 읽었는지 확인
                if numOfRows * pageNo >= totalCount:
                    break
                else:
                    params['pageNo'] += 1  # 다음 페이지로 이동

            except ET.ParseError as e:
                print(f"XML 파싱 에러 (LAWD_CD: {lawd_cd}):", e)
                break
        else:
            print(f"API 요청 실패 (LAWD_CD: {lawd_cd}): {response.status_code}")
            print(f"응답 내용: {response.text}")
            break

# DataFrame 생성
df = pd.DataFrame(all_data)

# 필요한 열만 선택 (필요에 따라 조정 가능)
df = df[['dealYear', 'dealMonth', 'dealDay', 'dealAmount', 'offiNm', 'excluUseAr', 'floor', 'umdNm', 'sggNm']]

# 데이터 타입 변환 및 전처리
df['dealAmount'] = df['dealAmount'].str.replace(',', '').astype(int)  # 거래 금액을 숫자형으로 변환
df['excluUseAr'] = df['excluUseAr'].astype(float)  # 전용면적을 실수형으로 변환
df['floor'] = df['floor'].astype(int)  # 층수를 정수형으로 변환

# CSV 파일로 저장
df.to_csv('./서울_실거래가_example.csv', encoding='utf-8-sig', index=False)

# DataFrame 출력
print(df)
