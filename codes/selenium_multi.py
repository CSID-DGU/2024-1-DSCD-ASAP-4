# import time
# start = time.time()
#     end = time.time()
#     print("수행시간: %f 초" % (end - start))

import selenium #셀레니움
import pandas as pd #csv를 읽고 dataframe을 사용하기 위한 pandas
from selenium import webdriver #브라우저를 띄우고 컨트롤하기 위한 webdriver
from selenium.webdriver.common.keys import Keys #브라우저에 키입력 용
from selenium.webdriver.common.by import By #webdriver를 이용해 태그를 찾기 위함
from selenium.webdriver.support.ui import WebDriverWait #Explicitly wait을 위함
from webdriver_manager.chrome import ChromeDriverManager #크롬에서 크롤링 진행 크롬 웹 드라이버 설치시 필요
from selenium.webdriver.support import expected_conditions as EC #브라우저에 특정 요소 상태 확인을 위해
from bs4 import BeautifulSoup #브라우저 태그를 가져오고 파싱하기 위함
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException #예외처리를 위한 예외들
from time import sleep

from multiprocessing import Pool

def crawling(keyword):

    ##최종##
    store_name_lst = []
    category_lst = []
    phone_num_lst = []
    address_lst = []
    score_lst = []
    visitor_review_lst = []

    def switch_left():
        ############## iframe으로l 왼쪽 포커스 맞추기 ##############
        driver.switch_to.parent_frame()
        iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
        driver.switch_to.frame(iframe)
        
    def switch_right():
        ############## iframe으로 오른쪽 포커스 맞추기 ##############
        driver.switch_to.parent_frame()
        #가게명 클릭 후 우측 프레임 로딩 대기
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "entryIframe"))
        )
        sleep(0.2) #혹시 몰라 추가시간

        iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
        driver.switch_to.frame(iframe)


    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument('window-size=1380,900')
    #driver = webdriver.Chrome(ChromeDriverManager().install()) # 크롬 드라이버 설치하지 않은 경우
    driver = webdriver.Chrome(options=options) # 크롬 드라이버 설치한 경우
    
    # 대기 시간
    driver.implicitly_wait(time_to_wait=3)
    
    # 반복 종료 조건
    loop = True

    driver.get("https://map.naver.com/v5/") #네이버지도 열기
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "input_search"))
        ) #입력창이 뜰 때까지 대기
    finally:
        pass



    keyword = keyword
    #keyword = str(input('키워드를 입력하시오: '))




    search_box = driver.find_element(By.CLASS_NAME,"input_search") #검색창 찾기
    search_box.send_keys(keyword) #검색어 입력
    search_box.send_keys(Keys.ENTER) #검색

    
    driver.implicitly_wait(5)

    while(loop):
        switch_left()

        ############## 맨 밑까지 스크롤 ##############
        scrollable_element = driver.find_element(By.CLASS_NAME, "Ryr1F")
        last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)


        while True:
            # 요소 내에서 아래로 600px 스크롤
            driver.execute_script("arguments[0].scrollTop += 1500;", scrollable_element)
    
            # 페이지 로드를 기다림
            sleep(0.5)  # 동적 콘텐츠 로드 시간에 따라 조절
    
            # 새 높이 계산
            new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
    
            # 스크롤이 더 이상 늘어나지 않으면 루프 종료
            if new_height == last_height:
                break
    
            last_height = new_height


if __name__=='__main__':
    keyword = ['서울 중구 카페','대전 중구 태권도장', '대구 중구 헬스장']

    pool = Pool(processes=3)
    pool.map(crawling, keyword)