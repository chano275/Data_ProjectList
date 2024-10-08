from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests

# Selenium WebDriver 설정 (Chrome)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
channel_url = 'https://www.youtube.com/@syukaworld/videos'  # YouTube 채널의 비디오 페이지 URL
driver.get(channel_url)  # 해당 URL 열기
time.sleep(5)  # 페이지가 완전히 로드될 때까지 잠시 대기

# 스크롤을 통해 더 많은 비디오 로드 (YouTube 페이지가 동적으로 비디오 목록을 로드하는 방식 고려)
scroll_pause_time = 2
last_height = driver.execute_script("return document.documentElement.scrollHeight")

for _ in range(10):  # 10회 스크롤 (필요에 따라 조정 가능)
    # 스크롤을 맨 아래로
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    # 페이지 로드 대기
    time.sleep(scroll_pause_time)

    # 새로운 스크롤 높이 계산
    new_height = driver.execute_script("return document.documentElement.scrollHeight")

    # 더 이상 로드할 비디오가 없을 때 중지
    if new_height == last_height:
        break
    last_height = new_height

# 동적으로 로드된 비디오 목록의 썸네일과 링크 추출
videos = driver.find_elements(By.XPATH, '//a[@id="video-title-link"]')  # XPATH 수정

# 썸네일 이미지 저장 폴더 생성
if not os.path.exists('thumbnails'):
    os.makedirs('thumbnails')

# 썸네일 이미지 다운로드
for video in videos:
    video_url = video.get_attribute('href')

    if video_url:
        video_id = video_url.split('v=')[-1]  # 수정된 비디오 ID 추출 방법
        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'

        # 이미지 다운로드
        img_data = requests.get(thumbnail_url).content
        with open(f'thumbnails/{video_id}.jpg', 'wb') as handler:
            handler.write(img_data)
            print(f"Downloaded: {video_id}.jpg")

driver.quit()
print("All thumbnails downloaded.")
