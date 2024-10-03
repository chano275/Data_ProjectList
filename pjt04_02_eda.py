import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트 설정
plt.rcParams['axes.unicode_minus'] = False

WHERE = ['서울특별시', '경기도', '강원특별자치도', '경상남도', '경상북도', '광주광역시', '대구광역시', '대전광역시', '부산광역시', '세종특별자치시', '울산광역시', '인천광역시', '전라남도', '전라북도', '충청남도', '충청북도']  # 지역 목록
YEAR = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']  # 연
age_labels = ['10대', '20대', '30대', '40대', '50대', '60대', '70대 이상']

df = pd.read_csv('./population_data_with_differences.csv')
df = df[df['year'] != '2015']  # 2015년 데이터 제외

# 연도별로 데이터 필터링 및 지역별로 population_diff 막대 그래프 그리기
for year in YEAR:
    df_year = df[df['year'] == int(year)]  # 연도별로 필터링

    #############################################################################
    # subplot 생성
    available_regions, total_plots = WHERE, 17
    n_cols, n_rows = 4, 5
    fig, axes = plt.subplots(5, 4, figsize=(16, 4 * 5))
    axes = axes.flatten()  # 2차원 배열을 1차원 배열로 변환

    # 서울특별시와 경기도를 제외한 나머지 지역의 합산 값을 저장할 데이터프레임
    total_population_diff = df_year[(df_year['adm_nm'] != '서울특별시') & (df_year['adm_nm'] != '경기도')].groupby(['age_type', 'gender'])['population_diff'].sum().reset_index()
    # 1. 합산 그래프를 첫 번째 subplot에 그리기
    ax_total = axes[0]  # 첫 번째 subplot
    x_total = range(len(total_population_diff['age_type'].unique()))  # 나이대의 위치 설정
    width = 0.35  # 막대의 너비 설정

    # 남성과 여성 합산 데이터를 나란히 표시
    for gender, offset in zip(['남성', '여성'], [-width/2, width/2]):
        df_total_gender = total_population_diff[total_population_diff['gender'] == gender]
        colors = ['red' if diff > 0 else 'blue' for diff in df_total_gender['population_diff']]
        ax_total.bar([pos + offset for pos in x_total], df_total_gender['population_diff'], width=width, color=colors)

    # 합산 subplot에 제목 및 레이블 설정
    ax_total.text(0.01, 0.95, '왼쪽: 남성, 오른쪽: 여성', transform=ax_total.transAxes, ha='left', va='top', fontsize=8)
    ax_total.set_title('서울, 경기도 제외 합산', fontsize=10, pad=15)
    ax_total.set_xlabel('나이대', fontsize=9)
    ax_total.set_ylabel('인구수 변화량', fontsize=9)
    ax_total.set_xticks(x_total)
    ax_total.set_xticklabels(age_labels, fontsize=8)  # 나이대를 한글로 표시
    ax_total.tick_params(axis='y', labelsize=8)
    ax_total.grid(True)
    gap = 40000
    ax_total.set_ylim(-gap, gap)  # Y축 범위 고정
    ax_total.set_yticks(range(-gap, gap + 1, 10000))  # Y축 눈금 간격 고정

    #############################################################################
    # 2. 지역별 그래프를 두 번째 subplot 부터 그리기
    for idx, region in enumerate(available_regions, start=1):
        df_region = df_year[df_year['adm_nm'] == region]  # 지역별로 필터링
        ax = axes[idx]
        age_groups = df_region['age_type'].unique()  # 나이대별 그룹 추출
        x = range(len(age_groups))  # 나이대의 위치 설정

        for gender, offset in zip(['남성', '여성'], [-width/2, width/2]):  # 남성과 여성 막대 그래프 나란히 표시
            df_gender = df_region[df_region['gender'] == gender]
            colors = ['red' if diff > 0 else 'blue' for diff in df_gender['population_diff']]
            ax.bar([pos + offset for pos in x], df_gender['population_diff'], width=width, color=colors)  # 막대 그래프 그리기

        # 각 subplot에 제목 및 레이블 설정
        ax.text(0.01, 0.95, '왼쪽: 남성, 오른쪽: 여성', transform=ax.transAxes, ha='left', va='top', fontsize=8)
        ax.set_title(f'{region}', fontsize=10, pad=15)
        ax.set_xlabel('나이대', fontsize=9)
        ax.set_ylabel('인구수 변화량', fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(age_labels, fontsize=8)
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(True)
        ax.set_ylim(-gap, gap)
        ax.set_yticks(range(-gap, gap + 1, 10000))

    for idx in range(total_plots, len(axes)):fig.delaxes(axes[idx])    # 나머지 빈 subplot 숨기기
    fig.suptitle(f'{year}년 - 모든 지역의 인구 변화 (성별/나이대별)', fontsize=14)    # 메인 제목 설정
    plt.tight_layout(rect=[0, 0, 1, 0.95])    # 레이아웃 조정
    plt.subplots_adjust(hspace=0.5, wspace=0.3)
    plt.show()    # 그래프 출력

