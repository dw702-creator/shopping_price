import streamlit as st
import pandas as pd

# -----------------------------
# 1. 상품 DB 로드
# -----------------------------
# GitHub raw URL 예시
DB_URL = "https://raw.githubusercontent.com/username/repo/main/product_db.csv"

@st.cache_data
def load_db():
    df = pd.read_csv(DB_URL)
    return df

# -----------------------------
# 2. Streamlit UI
# -----------------------------
st.title("👕 옷 검색 & 가격순 추천")

df = load_db()

st.sidebar.header("검색 조건 선택")
color = st.sidebar.text_input("색상 (예: 회색, 검정, 흰색)")
type_ = st.sidebar.text_input("종류 (예: 후드집업, 티셔츠)")
design = st.sidebar.text_input("디자인 (예: 검정 글씨, 로고, 심플)")

# -----------------------------
# 3. 조건 필터링
# -----------------------------
filtered = df.copy()

if color:
    filtered = filtered[filtered['color'].str.contains(color, case=False)]
if type_:
    filtered = filtered[filtered['type'].str.contains(type_, case=False)]
if design:
    filtered = filtered[filtered['design'].str.contains(design, case=False)]

# 가격순 정렬
filtered = filtered.sort_values(by="price").head(20)

# -----------------------------
# 4. 결과 출력
# -----------------------------
st.subheader(f"🔎 검색 결과 ({len(filtered)}개)")

if filtered.empty:
    st.write("조건에 맞는 상품이 없습니다.")
else:
    for idx, row in filtered.iterrows():
        st.markdown(f"### {row['name']}")
        st.write(f"색상: {row['color']}, 종류: {row['type']}, 디자인: {row['design']}")
        st.write(f"가격: {row['price']} 원")
        st.write(f"[구매 링크]({row['url']})")
        st.markdown("---")

