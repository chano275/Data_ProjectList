import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트 설정

# 데이터 로드 (위도, 경도, 인구 증감율, 연도 등의 정보가 포함된 CSV 파일)
df = pd.read_csv('population_data_with_differences.csv')

# 각 지역의 중심 위도와 경도 정보 추가
region_coordinates = {
    '서울특별시': (37.5665, 126.9780),
    '강원특별자치도': (37.8228, 128.1555),
    '경기도': (37.4138, 127.5183),
    '경상남도': (35.4606, 128.2132),
    '경상북도': (36.2486, 128.6647),
    '광주광역시': (35.1595, 126.8526),
    '대구광역시': (35.8714, 128.6014),
    '대전광역시': (36.3504, 127.3845),
    '부산광역시': (35.1796, 129.0756),
    '세종특별자치시': (36.4800, 127.2890),
    '울산광역시': (35.5384, 129.3114),
    '인천광역시': (37.4563, 126.7052),
    '전라남도': (34.8161, 126.4630),
    '전라북도': (35.7175, 127.1530),
    '충청남도': (36.5184, 126.8000),
    '충청북도': (36.6357, 127.4913)
}

# 제주특별자치도를 제외한 지역 좌표만 추가
df = df[df['adm_nm'] != '제주특별자치도']

# 2015년 데이터 제외
df = df[df['year'] != 2015]

# 지역별로 위도와 경도를 데이터프레임에 추가
df['latitude'] = df['adm_nm'].map(lambda x: region_coordinates.get(x, (None, None))[0])
df['longitude'] = df['adm_nm'].map(lambda x: region_coordinates.get(x, (None, None))[1])

# 위도와 경도가 없는 데이터 제거
df = df.dropna(subset=['latitude', 'longitude'])

# 나이대 코드와 라벨 매핑
age_code_to_label = {
    31: '10대',
    32: '20대',
    33: '30대',
    34: '40대',
    35: '50대',
    36: '60대',
    40: '70대 이상'
}

# age_type이 숫자 코드인 경우 라벨로 변환
df['age_label'] = df['age_type'].map(age_code_to_label)

# 인구 증감율의 절대값을 계산한 새로운 컬럼 추가
df['population_diff_abs'] = df['population_diff'].abs() / 10  # 원형 마커 크기를 10분의 1로 축소

# Streamlit 페이지 설정
st.set_page_config(page_title="인구 증감 지도 시각화", layout="wide")

# 페이지 제목 설정
st.title('인구 증감 지도 시각화')

# 연도 선택 dropdown 메뉴 추가 (2015년 제외)
year_options = sorted(df['year'].unique())
selected_year = st.selectbox('연도를 선택하세요', year_options)

# 성별 선택 멀티드롭다운 메뉴 추가
gender_options = ['남성', '여성']
selected_genders = st.multiselect('성별을 선택하세요', gender_options, default=gender_options)

# **나이대 선택 멀티드롭다운 메뉴 추가**
age_options = sorted(df['age_label'].dropna().unique())
selected_ages = st.multiselect('나이대를 선택하세요', age_options, default=age_options)

# 선택된 연도, 성별, 나이대의 데이터 필터링
df_filtered = df[(df['year'] == selected_year) &
                 (df['gender'].isin(selected_genders)) &
                 (df['age_label'].isin(selected_ages))]

# 성별별 데이터 분리
df_male = df_filtered[df_filtered['gender'] == '남성']
df_female = df_filtered[df_filtered['gender'] == '여성']

# Pydeck Layer 설정: 성별에 따라 시각화 설정
layers = []

# 남성 인구 증감 Layer
if '남성' in selected_genders and not df_male.empty:
    layers.append(
        pdk.Layer(
            'ScatterplotLayer',
            data=df_male,
            get_position='[longitude, latitude]',
            get_radius='[population_diff_abs * 10]',  # 상대값에 따라 크기 설정, 기존보다 축소
            get_fill_color='[population_diff > 0 ? 255 : 0, 0, population_diff < 0 ? 255 : 0, 180]',  # 빨강: 증가, 파랑: 감소
            pickable=True,
            opacity=0.6
        )
    )

# 여성 인구 증감 Layer
if '여성' in selected_genders and not df_female.empty:
    layers.append(
        pdk.Layer(
            'ScatterplotLayer',
            data=df_female,
            get_position='[longitude, latitude]',
            get_radius='[population_diff_abs * 10]',  # 상대값에 따라 크기 설정, 기존보다 축소
            get_fill_color='[population_diff > 0 ? 255 : 0, 0, population_diff < 0 ? 255 : 0, 180]',  # 빨강: 증가, 파랑: 감소
            pickable=True,
            opacity=0.6
        )
    )

# 지도 초기 상태 설정 (대한민국 중앙 기준)
view_state = pdk.ViewState(
    latitude=36.5,  # 대한민국 중앙의 위도
    longitude=127.5,  # 대한민국 중앙의 경도
    zoom=7,  # 확대 수준
    pitch=0  # 지도의 각도 설정
)

# Pydeck 차트 생성
r = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip={"text": "{adm_nm}\n인구 증감: {population_diff}"}
)

# Streamlit을 통해 차트 출력
st.pydeck_chart(r)

# 추가 설명 또는 가이드 출력
st.markdown(
    """
    ### 지도 설명
    - 각 원형의 크기는 인구 증감수를 나타내며, 상대적인 크기를 기준으로 조정되었습니다.
    - 색상은 인구의 증가와 감소를 나타내며, 성별에 따라 다른 색상으로 구분됩니다.
      - 남성: 빨강(증가), 파랑(감소)
      - 여성: 빨강(증가), 파랑(감소)
    - 선택한 성별과 나이대에 따라 인구 변화를 개별적으로 시각화할 수 있습니다.
    """
)

# ------------------------
# 추가 그래프 생성: 분석 내용을 시각화
# ------------------------

col1, col2 = st.columns(2)

# 1. 연도별 인구 변화 분석
with col1:
    st.subheader("연도별 인구 변화 분석")
    df_yearly_change = df.groupby('year')['population_diff'].sum().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_yearly_change, x='year', y='population_diff', marker='o')
    plt.title('연도별 인구 변화 (2016-2022)')
    plt.xlabel('연도')
    plt.ylabel('인구 증감수')
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()

# 2. 성별 인구 이동 패턴 분석
with col2:
    st.subheader("성별 인구 이동 패턴")
    df_gender_change = df.groupby(['year', 'gender'])['population_diff'].sum().reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_gender_change, x='year', y='population_diff', hue='gender')
    plt.title('성별 연도별 인구 변화 (2016-2022)')
    plt.xlabel('연도')
    plt.ylabel('인구 증감수')
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()

# 3. 나이대별 인구 이동 분석
col3, col4 = st.columns(2)
with col3:
    st.subheader("주요 나이대별 인구 이동 분석")
    age_groups = ['10대', '20대', '30대']
    df_age_groups = df[df['age_label'].isin(age_groups)].groupby(['year', 'age_label'])['population_diff'].sum().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_age_groups, x='year', y='population_diff', hue='age_label', marker='o')
    plt.title('주요 나이대별 인구 이동 (10대, 20대, 30대)')
    plt.xlabel('연도')
    plt.ylabel('인구 증감수')
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()  # 추가

# 4. 지역별 인구 변화 분석
with col4:
    st.subheader("수도권 vs 비수도권 인구 변화 분석")
    capital_regions = ['서울특별시', '경기도', '인천광역시']
    df['region_type'] = df['adm_nm'].apply(lambda x: '수도권' if x in capital_regions else '비수도권')
    df_region = df.groupby(['year', 'region_type'])['population_diff'].sum().reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_region, x='year', y='population_diff', hue='region_type')
    plt.title('수도권 vs 비수도권 인구 변화')
    plt.xlabel('연도')
    plt.ylabel('인구 증감수')
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()  # 추가