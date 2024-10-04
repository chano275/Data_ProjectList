from bs4 import BeautifulSoup
from parser_temp import get_article_content
import requests
import pandas as pd


query = '부동산'  # 검색어 입력 (예: '프롭테크')  # 나중에 응용 프로그램화? / streamlit에 df형식 띄우기
encoded_query = requests.utils.quote(query)  # 검색어를 URL에 맞게 인코딩
base_url = f"https://search.naver.com/search.naver?where=news&query={encoded_query}&start="  # 네이버 뉴스 검색 URL (최대 10페이지까지 가능)
page_number = 10  # 첫 페이지

news_data = []  # 크롤링할 데이터를 담을 리스트

for page in range(1, page_number):  # 뉴스 기사를 5페이지까지 크롤링 (원하는 페이지 수로 수정 가능)
    url = f"{base_url}{(page - 1) * 10 + 1}"      # 각 페이지의 URL 구성
    response = requests.get(url)      # HTTP 요청
    soup = BeautifulSoup(response.text, 'html.parser')      # BeautifulSoup 객체 생성
    articles = soup.select('div.news_wrap.api_ani_send')      # 뉴스 기사 리스트 추출
    for article in articles:
        title_tag = article.select_one('a.news_tit')
        title = title_tag.text if title_tag else 'N/A'
        link = title_tag['href'] if title_tag else 'N/A'
        date_tag = article.select_one('span.info')
        date = date_tag.text if date_tag else 'N/A'
        content = get_article_content(link)

        if content == "지원되지 않는 언론사입니다.":pass
        else:
            news_data.append({
                'Title': title,
                'Link': link,
                'Date': date,
                'Content': content
            })

# pandas 데이터프레임으로 변환
df_news = pd.DataFrame(news_data)

# 데이터프레임 출력
print(df_news)
df_news.to_csv('./save.csv', encoding='utf-8-sig', index=False)