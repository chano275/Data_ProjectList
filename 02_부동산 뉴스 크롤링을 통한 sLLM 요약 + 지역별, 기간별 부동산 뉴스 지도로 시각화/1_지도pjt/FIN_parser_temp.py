from bs4 import BeautifulSoup
import requests


def joongang(_url):  # 중앙일보
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return soup.find('div', class_='article_body').get_text(strip=True) if soup.find('div', class_='article_body') else "본문을 찾을 수 없습니다."

# def hani(_url):  # 한겨레  ###################################
#     soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
#     return soup.find('div', class_='article-text').get_text(strip=True) if soup.find('div', class_='article-text') else "본문을 찾을 수 없습니다."

# def khan(_url):  # 경향신문  # 언론사에서 거부해놓음
#     soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
#     return soup.find('div', id='articleBody').get_text(strip=True) if soup.find('div', id='articleBody') else "본문을 찾을 수 없습니다."

def magazine_hankyung(_url):  # 매거진 한경
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    article_body = soup.find('div', class_='article-body')
    return article_body.get_text(strip=True) if article_body else "본문을 찾을 수 없습니다."

def hankyung(_url):  # 한국경제
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return soup.find('div', id='articletxt').get_text(strip=True) if soup.find('div', id='articletxt') else "본문을 찾을 수 없습니다."

def mk(_url):  # 매일경제
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return ' '.join(p.get_text(strip=True) for p in soup.select('div.news_cnt_detail_wrap p')) if soup.select('div.news_cnt_detail_wrap p') else "본문을 찾을 수 없습니다."


def fnnews(_url):  # 파이낸셜뉴스
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return soup.find('div', id='article_content').get_text(strip=True) if soup.find('div', id='article_content') else "본문을 찾을 수 없습니다."

def mbc(_url):  # MBC 뉴스
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return soup.find('div', id='content').get_text(strip=True) if soup.find('div', id='content') else "본문을 찾을 수 없습니다."

def kbs(_url):  # KBS 뉴스
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return soup.find('div', class_='detail-body font-size').get_text(strip=True) if soup.find('div', class_='detail-body font-size') else "본문을 찾을 수 없습니다."

def weekly_donga(_url):  # 주간동아
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    article_view = soup.find('div', class_='article_view')
    return article_view.get_text(strip=True) if article_view else "본문을 찾을 수 없습니다."

def w_donga(_url):  # 우먼동아
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return ' '.join(p.get_text(strip=True) for p in soup.select('div.article_box p')) if soup.select('div.article_box p') else "본문을 찾을 수 없습니다."

def donga(_url):  # 동아일보
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return ' '.join(p.get_text(strip=True) for p in soup.select('section.news_view')) if soup.select('section.news_view') else "본문을 찾을 수 없습니다."


def kgnews(_url):  # 경기신문
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return soup.find('div', class_='content').get_text(strip=True) if soup.find('div', class_='content') else "본문을 찾을 수 없습니다."

def yna(_url):  # 연합뉴스
    soup = BeautifulSoup(requests.get(_url).text, 'html.parser')
    return ' '.join(p.get_text(strip=True) for p in soup.select('article p')) if soup.select('article p') else "본문을 찾을 수 없습니다."




def get_article_content(link):
    if 'joongang' in link:return joongang(link)
    # elif 'hani' in link:return hani(link)
    # elif 'khan' in link:return khan(link)
    elif 'magazine.hankyung' in link:return magazine_hankyung(link)
    elif 'hankyung' in link:return hankyung(link)
    elif 'mk.co.kr' in link:return mk(link)
    elif 'fnnews' in link:return fnnews(link)
    elif 'imnews.imbc.com' in link:return mbc(link)
    elif 'news.kbs.co.kr' in link:return kbs(link)
    elif 'weekly.donga' in link:return weekly_donga(link)
    elif 'woman.donga' in link:return w_donga(link)
    elif 'donga.com' in link:return donga(link)
    elif 'kgnews.co.kr' in link:return kgnews(link)
    elif 'yna.co.kr' in link:return yna(link)
    else:return "지원되지 않는 언론사입니다."
