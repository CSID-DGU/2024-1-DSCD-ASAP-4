import pandas as pd
import numpy as np
import pandas as pd
import random
from bokeh.io import output_file, save, show, curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Select, Button, Div, CustomJS, HoverTool, TextInput
from bokeh.layouts import column, row
from bokeh.tile_providers import get_provider, Vendors
from pyproj import Proj, transform
import subprocess
from threading import Thread
import time
import requests
# from bokeh.models import ColumnDataSource, GMap, GMapOptions

# path = 'C:/Users/taejin/Desktop/2024-1-DSCD-ASAP-4/codes' #코드 폴더 경로

# HTML 제목
title = Div(text=f"""
    <div style="display: flex; align-items: center; justify-content: center;">
        <h1 style="margin: 0;">네이버 지도 크롤링  </h1>
        <alt="Naver Map" style="width: 50px; height: 50px; margin-right: 10px;">
    </div>
    """, style={'text-align': 'center'})

# 데이터 정의
df = pd.read_csv('../data/법정동.csv', encoding='cp949')

# 빈 딕셔너리 생성
regions = {}

regions[''] = {'': ['']}
# 데이터를 그룹화하여 딕셔너리 형태로 변환
for 시도명, 시도_df in df.groupby('시도명'):
    regions[시도명] = {'': ['']}  # 시도명 아래에 빈 문자열로 이루어진 리스트를 추가합니다.
    for 시군구명, 시군구_df in 시도_df.groupby('시군구명'):
        regions[시도명][시군구명] = list(시군구_df['읍면동명'])

        # 시군구명 아래에 빈 문자열로 이루어진 리스트를 추가합니다.
        regions[시도명][시군구명].append('')

    # 시군구명이 없는 경우에도 빈 문자열 리스트를 추가합니다.
    regions[시도명][''].append('')

# 초기 선택값 설정
states = list(regions.keys())
initial_state = states[0]
initial_city = list(regions[initial_state].keys())[0]
initial_towns = regions[initial_state][initial_city]

# Bokeh Select 위젯 생성
state_select = Select(title="시/도", value=initial_state, options=states)
city_select = Select(title="시/군/구", value=initial_city, options=list(regions[initial_state].keys()))
town_select = Select(title="읍/면/동", value=initial_towns[0], options=initial_towns)
keyword_input = TextInput(title="Keyword", value="")

print(state_select.value, city_select.value, town_select.value, keyword_input.value)

# 콜백 함수 정의 및 연결
def update_cities(attr, old, new):
    selected_state = state_select.value
    cities = list(regions[selected_state].keys())
    city_select.options = cities
    city_select.value = cities[0]
    update_towns(None, None, None)

def update_towns(attr, old, new):
    selected_state = state_select.value
    selected_city = city_select.value
    towns = regions[selected_state][selected_city]
    town_select.options = towns
    town_select.value = towns[0]

def update_data():
    # Get input values
    global city, district, town, keyword
    city = state_select.value
    district = city_select.value
    town = town_select.value
    keyword = keyword_input.value

    # Run selenium_multi.py with the input values
    subprocess.run(['python', 'selenium_multi.py', '--city', city, '--district', district, '--town', town, '--keyword', keyword])
    
    
    ##### 지도 시각화 ##################
    result_df = pd.read_csv('../result/multi_result_{}_{}_{}_{}.csv'.format(city, district, town, keyword), encoding='cp949')
    result_df.drop('Unnamed: 0',axis=1,inplace=True)

    # 광역시와 특별시 리스트
    RLG2 = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종']
    RLG3 = ['수원시', '성남시', '안양시', '안산시', '고양시', '용인시', '청주시', '천안시', '전주시', '포항시', '창원시', '부천시']

        
    result_df['시도명'] = result_df['도로명주소'].str.split(" ", n=3).str.get(0)#.map(sido_mapping)

    # 시 군 구 단위 결정
    def determine_gu_unit(row):
        parts = row['도로명주소'].split()
        si = parts[1] if len(parts) > 1 else ''
        
        if si in RLG3:
            gu = parts[2] if len(parts) > 2 else ''
            return si + ' ' + gu if gu.endswith('구') else si
        elif row['시도명'] in RLG2:
            for part in parts:
                if part.endswith('구'):
                    return part
            return ''
        else:
            return si

    result_df['시군구명'] = result_df.apply(lambda row: determine_gu_unit(row), axis=1)

    # 읍/면/동 단위 결정
    def determine_eup_myeon_dong_unit(row):
        addr_parts = row['주소'].split() if isinstance(row['주소'], str) else []
        road_parts = row['도로명주소'].split() if isinstance(row['도로명주소'], str) else []
        
        for part in addr_parts:
            if part.endswith('동') or part.endswith('가'):
                return part
        for part in road_parts:
            if part.endswith('읍') or part.endswith('면'):
                return part
        return ''

    result_df['읍면동명'] = result_df.apply(determine_eup_myeon_dong_unit, axis=1)

    # 리 단위 결정 -> 굳이 필요할까..? 너무 작은 단위라 굳이?
    def determine_ri_unit(address):
        if isinstance(address, str):
            parts = address.split()
            for part in parts:
                if part.endswith('리'):
                    return part
        return ''

    result_df['리 단위'] = result_df['주소'].apply(determine_ri_unit)
    
    
    ## 데이터 필터링 코드 -> 원하는 지역만 볼 수 있게
    selected_state = state_select.value
    selected_city = city_select.value
    selected_town = town_select.value

    # 시군구명이 공백이면
    print('========')#######################
    print(selected_state)
    print(selected_city)
    print(selected_town)
    print('========')


    # result_df.to_csv('../result_df확인.csv', encoding='cp949')#################

    if selected_city == '':
        result_df1 = result_df[result_df['시도명'] == selected_state]
    # 읍면동명이 공백이면
    elif selected_town == '':
        result_df1 = result_df[(result_df['시도명'] == selected_state) & 
                                (result_df['시군구명'] == selected_city)]
    # 시군구명과 읍면동명 모두 공백이 아니면
    else:
        result_df1 = result_df[(result_df['시도명'] == selected_state) & 
                                (result_df['시군구명'] == selected_city) & 
                                (result_df['읍면동명'] == selected_town)]

    # result_df1.to_csv('../result_df1확인.csv', encoding='cp949')#################
    
    #네이버 API로 위경도 열 생성.
    visual_df = result_df1.drop_duplicates(subset=result_df.columns)

    # 위경도 변환 함수
    def get_lat_lng(address):
        client_id = 's8pego1ogd'  # 네이버 API 클라이언트 ID
        client_secret = 'IDwfqb34hdFls7BxU0V8WknUzJ0HrQn46NUjfBn9'  # 네이버 API 시크릿
        
        url = f'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}'
        headers = {
            'X-NCP-APIGW-API-KEY-ID': client_id,
            'X-NCP-APIGW-API-KEY': client_secret
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'addresses' in data and len(data['addresses']) > 0:
                latitude = data['addresses'][0]['y']
                longitude = data['addresses'][0]['x']
                return latitude, longitude
        return None, None

    def convert_address_to_lat_lng(df, address_column):
        latitudes = []
        longitudes = []
        for index, row in df.iterrows():
            address = row[address_column]
            if address:
                latitude, longitude = get_lat_lng(address)
                latitudes.append(latitude)
                longitudes.append(longitude)
                time.sleep(0.1)  # API 호출 제한을 피하기 위해 딜레이 추가
            else:
                latitudes.append(None)
                longitudes.append(None)
        df['Latitude'] = latitudes
        df['Longitude'] = longitudes
        return df


    # 주소를 위도와 경도로 변환하여 데이터프레임에 추가
    convert_address_to_lat_lng(visual_df, '도로명주소')

    visual_df['Latitude'] = visual_df['Latitude'].astype('float')
    visual_df['Longitude'] = visual_df['Longitude'].astype('float')
    visual_df.dropna(subset=['읍면동명'], inplace=True)

    data=visual_df.copy()
    # 좌표를 웹 메르케이터로 변환 (이거 안하면 잘 안되길래 일단 넣었음 )
    wgs84 = Proj(init='epsg:4326')
    mercator = Proj(init='epsg:3857')
    data['x'], data['y'] = transform(wgs84, mercator, data['Longitude'].values, data['Latitude'].values)


    sido=data['시도명'].unique()
    gungu=data['시군구명'].unique()
    dong=data['읍면동명'].unique()

    # 각 도시의 데이터에 대한 ColumnDataSource 생성
    sido_sources = {sido: ColumnDataSource(data[data['시도명'] == sido]) for sido in sido}
    sido_sources['All'] = ColumnDataSource(data)

    gungu_sources = {gungu: ColumnDataSource(data[data['시군구명'] == gungu]) for gungu in gungu}
    gungu_sources['All'] = ColumnDataSource(data)

    dong_sources = {dong: ColumnDataSource(data[data['읍면동명'] == dong]) for dong in dong}
    dong_sources['All'] = ColumnDataSource(data)

    sources = {'All': ColumnDataSource(data)}
    sources.update(sido_sources)
    sources.update(gungu_sources)
    sources.update(dong_sources)


    # 지도 설정 => 일반 지도로 하고 싶으면 Vendors.OSM 쓰면 됨.
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)
    p = figure(x_axis_type="mercator", y_axis_type="mercator", width=800, height=600, tools='pan, wheel_zoom, reset, hover')
    p.add_tile(tile_provider)

    # 지도에 점 추가
    points = p.circle('x', 'y', size=10, fill_color='blue', fill_alpha=0.8, line_color=None, source=sources['All'])

    # 마우스로 정보 표시
    hover = HoverTool()
    hover.point_policy = "follow_mouse"
    hover.tooltips = [("🏠", "@{가게명}"), ("✔", "@{업종}"), ("📍", "@{주소}"), ("⭐", "@{별점}"), ("👀", "@{리뷰 합계}")]
    p.add_tools(hover)


    # HTML 제목
    # {city} {district} {town}
    image_path = '../data/navermap.jpg'
    title = Div(text=f"""
    <div style="display: flex; align-items: center; justify-content: center;">
        <h1 style="margin: 0;">네이버 지도 시각화- {keyword} </h1>
        <img src={image_path} alt="Naver Map" style="width: 50px; height: 50px; margin-right: 10px;">
    </div>
    """, style={'text-align': 'center'})

    # 지역 선택 -> select 생성.
    sido_options = ['All'] + sido.tolist()
    sido_select = Select(title="시도명에 따라 필터링:", value='All', options=sido_options)

    gungu_options = ['All'] + gungu.tolist()
    gungu_select = Select(title="시군구명에 따라 필터링:", value='All', options=gungu_options)

    dong_options = ['All'] + dong.tolist()
    dong_select = Select(title="읍면동명에 따라 필터링:", value='All', options=dong_options)


    # 필터링 버튼
    filter_button = Button(label="필터링", button_type="success")

    # CustomJS 코드 -> 필터링 버튼을 눌렀을 때의 동작. 각각의 경우의 수에 다라 한것인디 이건 크롤링이랑 합칠때 하거나 수정할거 있음 수정하면 될듯..?
    button_callback_code = """
        var selected_sido = sido_select.value;
        var selected_gungu = gungu_select.value;
        var selected_dong = dong_select.value;
        var new_data;
        if (selected_sido == 'All' && selected_gungu == 'All' && selected_dong == 'All') {
            new_data = sido_sources['All'].data;
        } else if (selected_sido == 'All' && selected_gungu == 'All') {
            new_data = dong_sources[selected_dong].data;
        } else if (selected_sido == 'All' && selected_dong == 'All') {
            new_data = gungu_sources[selected_gungu].data;
        } else if (selected_gungu == 'All' && selected_dong == 'All') {
            new_data = sido_sources[selected_sido].data;
        } else if (selected_sido == 'All') {
            new_data = dong_sources[selected_dong].data;
        } else if (selected_gungu == 'All') {
            new_data = sido_sources[selected_sido].data.filter(function (item) {return item['시군구명'] === selected_gungu});
        } else if (selected_dong == 'All') {
            new_data = sido_sources[selected_sido].data.filter(function (item) {return item['읍면동명'] === selected_dong});
        } else {
            new_data = dong_sources[selected_dong].data;
        }
        source.data = new_data;
    """
        #p.title.text = (selected_sido == 'All' ? 'All sidos' : selected_sido) + ' - ' + (selected_gungu == 'All' ? 'All gungus' : selected_gungu) + ' - ' + (selected_dong == 'All' ? 'All dongs' : selected_dong);


    # CustomJS 콜백
    button_callback = CustomJS(args=dict(source=sources['All'], sido_sources=sido_sources, gungu_sources=gungu_sources, dong_sources=dong_sources, p=p, sido_select=sido_select, gungu_select=gungu_select, dong_select=dong_select), code=button_callback_code)
    filter_button.js_on_click(button_callback)


    # 각 지역의 가게 수 표시 dataframe 삽입.
    # 시도명별 가게 수 Barplot 생성
    sido_store_counts = data.groupby('시도명').size().reset_index(name='가게 수')
    sido_bar_source = ColumnDataSource(sido_store_counts)
    sido_bar_plot = figure(x_range=sido_store_counts['시도명'], plot_height=350, title="✅시도명 별 가게 수", toolbar_location=None, tools="")
    sido_bar_plot.vbar(x='시도명', top='가게 수', width=0.9, source=sido_bar_source, color='blue')
    sido_bar_plot.xaxis.major_label_orientation = 1.2
    sido_bar_plot.xgrid.grid_line_color = None
    sido_bar_plot.y_range.start = 0

    # 시군구명별 가게 수 Barplot 생성
    gungu_store_counts = data.groupby('시군구명').size().reset_index(name='가게 수')
    gungu_bar_source = ColumnDataSource(gungu_store_counts)
    gungu_bar_plot = figure(x_range=gungu_store_counts['시군구명'], plot_height=350, title="✅시군구명 별 가게 수", toolbar_location=None, tools="")
    gungu_bar_plot.vbar(x='시군구명', top='가게 수', width=0.9, source=gungu_bar_source, color='green')
    gungu_bar_plot.xaxis.major_label_orientation = 1.2
    gungu_bar_plot.xgrid.grid_line_color = None
    gungu_bar_plot.y_range.start = 0

    # 읍면동별 가게 수 Barplot 생성
    dong_store_counts = data.groupby('읍면동명').size().reset_index(name='가게 수')
    dong_bar_source = ColumnDataSource(dong_store_counts)
    dong_bar_plot = figure(x_range=dong_store_counts['읍면동명'], plot_height=350, title="✅읍면동명 별 가게 수", toolbar_location=None, tools="")
    dong_bar_plot.vbar(x='읍면동명', top='가게 수', width=0.9, source=dong_bar_source, color='orange')
    dong_bar_plot.xaxis.major_label_orientation = 1.2
    dong_bar_plot.xgrid.grid_line_color = None
    dong_bar_plot.y_range.start = 0

    #store_text = Div(text=f"<b>📊각 지역별 가게 수📊</b><br>{count_text}", style={'font-size': '120%', 'text-align': 'center'})

    # 레이아웃에 바 그래프 추가
    bar_layout = column(sido_bar_plot, gungu_bar_plot, dong_bar_plot)

    # 레이아웃 구성
    controls = column(row(sido_select, gungu_select, dong_select), filter_button)
    left_layout = column(title,p, controls)
    layout_1 = row(left_layout, bar_layout)
    curdoc().add_root(layout_1)
    

state_select.on_change('value', update_cities)
city_select.on_change('value', update_towns)

# Create a button that will trigger the update
update_button = Button(label="확인")
update_button.on_click(update_data)


# 레이아웃 구성
layout = column(title, state_select, city_select, town_select, keyword_input, update_button, Div())

# Bokeh 문서에 레이아웃 추가
curdoc().add_root(layout)