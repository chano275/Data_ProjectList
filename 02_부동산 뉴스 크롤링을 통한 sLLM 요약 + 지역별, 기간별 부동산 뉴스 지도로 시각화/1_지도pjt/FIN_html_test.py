import requests
from bs4 import BeautifulSoup



def check_article_content(link):
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup.prettify())  # HTML 구조를 출력하여 확인
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

# 테스트할 링크 입력
test_link = "https://sports.donga.com/article/all/20241022/130268017/1"
check_article_content(test_link)
