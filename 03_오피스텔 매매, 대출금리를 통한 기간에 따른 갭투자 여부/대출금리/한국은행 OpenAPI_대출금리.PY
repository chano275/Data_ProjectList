# 각 연도별 여러 대출금리 받아와 csv 파일로 저장 => 이걸 다른 파일에서 read 해서 사용해야

import requests
import xml.etree.ElementTree as ET
import pandas as pd

# API 요청 정보 설정
auth_key = 'ZHLBINPYMZ7YYV6CXG6I'  # 발급받은 인증키로 대체하세요
stat_code = '722Y001'  # 대출금리 통계코드로 대체하세요

# 주기 설정: A(연간), Q(분기), M(월간)
freq = 'Q'  # 분기별 데이터 조회

# 시작일자와 종료일자 설정
if freq == 'Q':
    start_period = '2010Q1'
    end_period = '2024Q4'
elif freq == 'M':
    start_period = '201001'
    end_period = '202412'
else:
    start_period = '2010'
    end_period = '2024'

url = f'https://ecos.bok.or.kr/api/StatisticSearch/{auth_key}/xml/kr/1/10000/{stat_code}/{freq}/{start_period}/{end_period}'

response = requests.get(url)

if response.status_code == 200:
    try:
        contents = response.text
        root = ET.fromstring(contents)

        # 오류 확인
        result_code = root.find('.//CODE')
        if result_code is not None and result_code.text != '0000':
            result_message = root.find('.//MESSAGE').text
            print(f'오류 발생: {result_message}')
        else:
            # 데이터 파싱 및 DataFrame으로 저장
            data_list = root.findall('.//row')

            # 데이터를 저장할 리스트 초기화
            records = []

            for item in data_list:
                time = item.find('TIME').text  # 시간 정보
                data_value = item.find('DATA_VALUE').text  # 대출금리 값

                # 추가적인 항목 정보 추출
                item_name1 = item.find('ITEM_NAME1').text  # 항목명1
                item_name2 = item.find('ITEM_NAME2').text  # 항목명2 (필요 시)

                # 시간 형식 변환
                if freq == 'Q':
                    year = time[:4]
                    quarter = time[5]  # 'Q1'에서 '1' 추출
                    display_time = f"{year}-{quarter}분기"
                elif freq == 'M':
                    year = time[:4]
                    month = time[4:6]
                    display_time = f"{year}-{month}월"
                else:
                    display_time = f"{time}년"

                # 리스트에 추가
                records.append({
                    '시간': display_time,
                    '항목명': item_name1,
                    '대출금리': data_value
                })

            # DataFrame 생성
            df = pd.DataFrame(records)

            # DataFrame 출력
            print(df)
            df.to_csv('./각 연도별 여러 대출금리.csv', encoding='cp949')

    except Exception as e:
        print(f'데이터 처리 중 오류 발생: {str(e)}')
else:
    print(f'HTTP 오류 발생: 상태 코드 {response.status_code}')
