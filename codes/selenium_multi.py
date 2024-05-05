import selenium #셀레니움
import pandas as pd #csv를 읽고 dataframe을 사용하기 위한 pandas
import numpy as np
from selenium import webdriver #브라우저를 띄우고 컨트롤하기 위한 webdriver
from selenium.webdriver.common.keys import Keys #브라우저에 키입력 용
from selenium.webdriver.common.by import By #webdriver를 이용해 태그를 찾기 위함
from selenium.webdriver.support.ui import WebDriverWait #Explicitly wait을 위함
from webdriver_manager.chrome import ChromeDriverManager #크롬에서 크롤링 진행 크롬 웹 드라이버 설치시 필요
from selenium.webdriver.support import expected_conditions as EC #브라우저에 특정 요소 상태 확인을 위해
from bs4 import BeautifulSoup #브라우저 태그를 가져오고 파싱하기 위함
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException #예외처리를 위한 예외들
from time import sleep
import sys
from multiprocessing import Pool

""" 주석고 같이 실행해서 법정동 csv 조금 수정했습니다. 파일은 함께 드렸으니 따로 실행하실 필요 없습니다.
df_all=pd.read_csv('법정동_20240201.csv') ##현재 법정동csv 
df_all.dropna(subset=['읍면동명'],inplace=True)
df_all=df_all.reset_index().drop('index',axis=1)
df_all.fillna('',inplace=True)
df_all=df_all.assign(
    지역 = lambda x:x['시도명']+' ' + x['시군구명']+' ' +x['읍면동명']+' '
)
df_all=df_all[['지역','시도명','시군구명','읍면동명']]
df_all = df_all.drop_duplicates()
df_all.to_csv("./법정동.csv",encoding='cp949') #정리 후 법정동csv 저장
"""

def scrape(args): #keyword, x_position //
    keyword = args[0] #키워드
    x_position = args[1] #창 x 위치

    ##키워드 한 번##
    store_name_lst = []
    category_lst = []
    phone_num_lst = []
    address_lst = []
    score_lst = []
    reviews_lst = []

    def switch_left():
        ############## iframe으로l 왼쪽 포커스 맞추기 ##############
        driver.switch_to.parent_frame()
        iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
        driver.switch_to.frame(iframe)
        
    def switch_right():
        ############## iframe으로 오른쪽 포커스 맞추기 ##############
        driver.switch_to.parent_frame()
        #가게명 클릭 후 우측 프레임 로딩 대기
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "entryIframe"))
        )
        sleep(0.5) #혹시 몰라 추가시간
        iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
        driver.switch_to.frame(iframe)

    def crawl_details(driver):
        store_name, category, phone_num, address, score, review_str = None, None, None, None, None, None #초기화
        try:
            title = driver.find_element(By.XPATH,'//div[@class = "zD5Nm undefined"]')
            store_name = title.find_element(By.XPATH,'.//div[1]/div[1]/span[1]').text
            if title.find_elements(By.XPATH,'.//div[1]/div[1]/span')[-1].text == '새로오픈':
                category = title.find_elements(By.XPATH,'.//div[1]/div[1]/span')[-2].text
            else:
                category = title.find_elements(By.XPATH,'.//div[1]/div[1]/span')[-1].text

            try:
                phone_num = driver.find_element(By.XPATH,'//span[@class = "xlx7Q"]').text
                driver.implicitly_wait(0.5)
            except:
                phone_num = '-'
            address = driver.find_element(By.XPATH,'//span[@class = "LDgIH"]').text

            try:
                review_str = ''
                reviews = title.find_elements(By.XPATH, './/div[@class = "dAsGb"]/span[@class = "PXMot"]')
                for review in reviews:
                    a_review = review.find_element(By.XPATH,'./a').text
                    review_str += a_review + ' '

            except:
                review_str = '-'

            try:
                score = title.find_element(By.XPATH, './/div[@class = "dAsGb"]/span[@class = "PXMot LXIwF"]').text
                score = score.replace('\n',' ') #줄바꿈 대체
            except:
                score = '-' 

            print(f'가게명: {store_name},   업종: {category},   전화번호: {phone_num},   주소: {address},   별점: {score}   리뷰: {review_str}')

            return store_name, category, phone_num, address, score, review_str

        except Exception as e:
            print("상세 정보를 가져오는 중 에러 발생:", e)
            #return None, None, None, None, None, None
            return store_name, category, phone_num, address, score, review_str #오류 이후만 None
        




    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument('window-size=600,1000')
    driver = webdriver.Chrome(ChromeDriverManager().install()) # 크롬 드라이버 설치하지 않은 경우
    # driver = webdriver.Chrome(options=options) # 크롬 드라이버 설치한 경우
    
    driver.set_window_position(x_position,0) ##창 띄우는 위치

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

    switch_left()
    # 조건에 맞는 업체 없는 경우
    try:
        no_result_message = driver.find_element(By.CLASS_NAME,'FYvSc').text
        if no_result_message == '조건에 맞는 업체가 없습니다.':
            return pd.DataFrame([['','','','','','']], columns=['가게명', '업종', '전화번호', '주소', '별점', '방문자/블로그 리뷰'])
        pass
    except:
        pass


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

        ############## 현재 page number 가져오기 ##############
        current_page_no = driver.find_element(By.XPATH,'//a[contains(@class, "mBN2s qxokY")]').text

        # 현재 페이지에 등록된 모든 가게 조회
        # 첫페이지 광고 2개 때문에 첫페이지는 앞 2개를 빼야함

        elements = driver.find_elements(By.XPATH,'//*[@id = "_pcmap_list_scroll_container"]/ul/li')

        # 페이지 및 가게 수 출력
        print(f'현재 {current_page_no} 페이지 / 총 {len(elements)}개(광고 포함)의 가게를 찾았습니다.\n')
        
        
        switch_left()
    
        
        for index, e in enumerate(elements, start=1): #기존: elemets
            store_name = '' # 가게 이름
            category = '' # 카테고리
            address = '' # 가게 주소
            business_hours = [] # 영업 시간
            phone_num = '' # 전화번호
    
            switch_left()
            '''가게명 클릭 '''
            
            try:
                #우측 그림 or 없음 - type1
                if e.get_attribute("data-laim-exp-id")=="undefined":
                    e.find_elements(By.XPATH, "./div[1]/div")[-1].find_element(By.XPATH,"./a[1]/div/div/span[1]").click() 

                #아래에 그림있는 경우 - type2
                elif e.get_attribute("data-laim-exp-id")=="undefinedundefined":
                    e.find_element(By.CLASS_NAME,'CHC5F').find_element(By.XPATH, "./a/div/div/span[1]").click() 
                    
                #광고 - type3
                else:  #"undefined*e"
                    continue #다음 for문 루프로
            except:
                pass
            ''''''
            # button = driver.find_element_by_xpath(".//a/div/div/span")
            # driver.execute_script("arguments[0].click();", button)

            try:
                switch_right()
            except: #오류날 시 0.5초 대기 후 재시도
                print('0.5초 대기 후 우측 전환')
                sleep(0.5)
                switch_right()
                break ###########################

            #title 불러와지면 넘어감
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH,'//div[@class = "zD5Nm undefined"]'))
            )

            #상세정보 크롤링
            store_name, category, phone_num, address, score, reviews = crawl_details(driver)
            
            store_name_lst.append(store_name)
            category_lst.append(category)
            phone_num_lst.append(phone_num)
            address_lst.append(address)
            score_lst.append(score)
            reviews_lst.append(reviews)

        switch_left()

        # 이건 페이지 넘어갈때마다 확인 -> true라면 마지막 페이지임
        next_page = driver.find_elements(By.XPATH,'//*[@id="app-root"]/div/div[2]/div[2]/a')[-1]

        # 페이지 다음 버튼이 활성화 상태일 경우 계속 진행
        if(next_page.get_attribute('aria-disabled') == 'false'):
            driver.find_elements(By.XPATH,'//*[@id="app-root"]/div/div[2]/div[2]/a')[-1].click()
        # 아닐 경우 루프 정지
        else:
            loop = False #모두 끝
           
    driver.switch_to.default_content()
    driver.find_element(By.CLASS_NAME, "btn_clear").click()
    driver.implicitly_wait(5)

    #한 키워드가 끝난 결과를 all_df에 추가
    keyword_df = pd.DataFrame(zip(store_name_lst, category_lst, phone_num_lst, address_lst, score_lst, reviews_lst), columns=['가게명', '업종', '전화번호', '주소', '별점', '방문자/블로그 리뷰']) #한 키워드의 모든 결과 저장
    
    driver.quit()
    return keyword_df # 키워드 한 개에 대한


'''멀티 프로세싱'''
if __name__=='__main__':

    all_df = pd.DataFrame()  #전체 df

    # df_all = pd.read_csv('data/법정동.csv', encoding='cp949') #수정한 법정동 csv 불러옴

    df_all_concat = pd.read_csv('data/법정동.csv', encoding='cp949')['지역']

    '''각 항목에서 "전체" 선택 원할 시 입력 없이 enter'''
    #지역, 키워드 입력받음#
    city = input('원하는 시도명을 입력하세요.') #'서울특별시'
    district = input('원하는 시군구명을 입력하세요.')#'종로구'
    town = input('원하는 읍면동명을 입력하세요.') #'효자동'
    keyword = input('검색어를 입력하세요.') #'태권도'

    if city+district+town == '': #전국 (<- 아무것도 입력 안 한 경우)
        regions = df_all_concat #전국 지역 리스트
    elif district+town == '':
        regions = list(filter(lambda x: city in x, df_all_concat)) #해당하는 지역 리스트
    else:
        regions = list(filter(lambda x: city + ' ' + district + ' ' + town in x, df_all_concat)) #해당하는 지역 리스트

    keywords_list = [region+keyword for region in regions]

    x_position = [i*300 % 1500 for i in range(len(keywords_list))]

    pool = Pool(processes=5)
    keywords_df = pool.map(scrape, zip(keywords_list, x_position))

    print('끝났다~~~~~~~~~~~~')
    # print(keywords_df)############

    for df in keywords_df: #브라우저 별로 크롤링된 결과 병합
        #print(df)
        all_df = pd.concat([all_df, df], ignore_index=True) #all_df에 키워드별 df 추가


    ##중복 제거
    all_df = all_df.drop_duplicates(subset=all_df.columns)
    ##가게명이 None인 경우 drop
    all_df = all_df[all_df['가게명'] != ''].reset_index(drop=True)


    ##프랜차이즈 여부 컬럼 생성##
    boolin =  all_df['가게명'].str.endswith('점')
    all_df1=all_df[boolin] #'-점'으로 끝나는 경우

    all_df1.loc[:,'가게명'] = all_df1.loc[:,'가게명'].str.rsplit(" ", n=1).str.get(0)

    #위 상호명이 5개 이상인 경우는 프랜차이즈
    store_counts = all_df1.groupby('가게명').size()
    excluded_stores = store_counts[store_counts >= 5].index
    all_df['프랜차이즈여부'] = np.where(all_df['가게명'].isin(excluded_stores), 'O', 'X')

    print(all_df)
    
    '''csv 저장'''
    all_df.to_csv('./multi_result_{}_{}_{}_{}.csv'.format(city, district, town, keyword), encoding='cp949')