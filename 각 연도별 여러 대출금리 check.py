import pandas as pd

df = pd.read_csv('각 연도별 여러 대출금리.csv', encoding='utf-8')
df = df[df['항목명'] == '한국은행 기준금리']
print(df)