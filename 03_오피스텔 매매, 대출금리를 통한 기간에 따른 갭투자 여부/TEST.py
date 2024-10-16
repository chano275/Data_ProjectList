import requests

# 디코딩된 인증키 사용 (필요에 따라 수정)
API_KEY = 'ophtl1lbQO6jla4+Jbkgnbcfo8LtBR69dkK7zrkGXu9c4IwDVGA4FwzzhsVRsIC9esBsOubhaQxWwye5gtsMbQ=='
ENDPOINT = 'https://apis.data.go.kr/1613000/RTMSDataSvcOffiTrade'

# 직접 URL 쿼리 구성
url = f"{ENDPOINT}?LAWD_CD=11110&DEAL_YMD=202308&serviceKey={API_KEY}"

# API 요청 보내기
response = requests.get(url)

# 응답 코드 및 내용 출력
print(f"응답 코드: {response.status_code}")
print(f"응답 내용:\n{response.text}")
