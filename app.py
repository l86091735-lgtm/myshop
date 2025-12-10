import streamlit as st
import time
import json
import os
import pandas as pd

# -----------------------
# 기본 설정
# -----------------------
st.set_page_config(page_title="미션 쇼핑 앱", layout="centered")

PRODUCT_FILE = "products.csv"
RANKING_FILE = "ranking.json"

# -----------------------
# 파일 로드 함수
# -----------------------
@st.cache_data
def load_products():
    return pd.read_csv(PRODUCT_FILE)

def load_ranking():
    if not os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ranking(data):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -----------------------
# 상품 불러오기
# -----------------------
products_df = load_products()

products = {
    row["name"]: {
        "price": int(row["price"]),
        "image": row["image_url"]
    }
    for _, row in products_df.iterrows()
}

# -----------------------
# 세션 상태
# -----------------------
if "page" not in st.session_state:
    st.session_state.page = "start"
if "budget" not in st.session_state:
    st.session_state.budget = 0
if "cart" not in st.session_state:
    st.session_state.cart = []
if "reflection" not in st.session_state:
    st.session_state.reflection = ""
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "보통"
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "time_limit" not in st.session_state:
    st.session_state.time_limit = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "player_name" not in st.session_state:
    st.session_state.player_name = ""

DIFFICULTY_SETTINGS = {
    "쉬움": {"time": 180, "bonus": 1, "budgets": [30000, 50000, 70000]},
    "보통": {"time": 120, "bonus": 2, "budgets": [20000, 40000, 60000]},
    "어려움": {"time": 60, "bonus": 3, "budgets": [10000, 20000, 30000]}
}

# -----------------------
# 1. 시작 화면
# -----------------------
def start_page():
    st.title("🎯 미션 시작")

    name = st.text_input("이름 입력")

    difficulty = st.radio("난이도 선택", ["쉬움", "보통", "어려움"])
    budgets = DIFFICULTY_SETTINGS[difficulty]["budgets"]

    budget = st.radio("예산 선택", budgets, format_func=lambda x: f"{x:,}원")

    if st.button("미션 시작"):
        st.session_state.player_name = name if name else "익명"
        st.session_state.difficulty = difficulty
        st.session_state.budget = budget
        st.session_state.cart = []
        st.session_state.reflection = ""
        st.session_state.score = 0
        st.session_state.start_time = time.time()
        st.session_state.time_limit = DIFFICULTY_SETTINGS[difficulty]["time"]
        st.session_state.page = "shopping"
        st.rerun()

# -----------------------
# 2. 쇼핑 화면
# -----------------------
def shopping_page():
    st.title("🛒 쇼핑 화면")

    elapsed = int(time.time() - st.session_state.start_time)
    remaining_time = st.session_state.time_limit - elapsed

    if remaining_time <= 0:
        st.warning("⏰ 시간이 초과되었습니다!")
        st.session_state.page = "result"
        st.rerun()

    st.write(f"이름: **{st.session_state.player_name}**")
    st.write(f"난이도: **{st.session_state.difficulty}**")
    st.write(f"남은 시간: **{remaining_time}초**")
    st.write(f"예산: **{st.session_state.budget:,}원**")

    total_price = sum(products[item]["price"] for item in st.session_state.cart)
    remaining_money = st.session_state.budget - total_price

    st.write(f"사용 금액: {total_price:,}원")
    st.write(f"남은 예산: {remaining_money:,}원")

    st.divider()

    # 상품 목록
    st.subheader("상품 목록")

    for name, info in products.items():
        col1, col2 = st.columns([2, 3])

        with col1:
            st.image(info["image"], use_container_width=True)

        with col2:
            st.write(f"**{name}**")
            st.write(f"{info['price']:,}원")

            if st.button(f"{name} 담기"):
                if remaining_money - info["price"] < 0:
                    st.warning("❗ 예산 초과!")
                else:
                    st.session_state.cart.append(name)
                st.rerun()

    st.divider()

    if st.button("구매 완료 → 결과"):
        st.session_state.page = "result"
        st.rerun()

# -----------------------
# 점수 계산
# -----------------------
def calculate_score():
    used = sum(products[item]["price"] for item in st.session_state.cart)
    remaining_money = st.session_state.budget - used

    time_used = int(time.time() - st.session_state.start_time)
    time_left = max(st.session_state.time_limit - time_used, 0)

    bonus = DIFFICULTY_SETTINGS[st.session_state.difficulty]["bonus"]

    score = 0
    if remaining_money >= 0:
        efficiency = int((used / st.session_state.budget) * 100)
        score += efficiency * 10

    score += time_left * 2
    score *= bonus

    return score

# -----------------------
# 3. 결과 화면
# -----------------------
def result_page():
    st.title("✅ 결과 화면")

    total_price = sum(products[item]["price"] for item in st.session_state.cart)
    remaining_money = st.session_state.budget - total_price

    st.subheader("📦 구매한 상품")
    if st.session_state.cart:
        for item in st.session_state.cart:
            st.write(f"- {item} ({products[item]['price']:,}원)")
    else:
        st.write("구매한 상품이 없습니다.")

    st.divider()

    st.write(f"총 사용 금액: **{total_price:,}원**")
    st.write(f"남은 금액: **{remaining_money:,}원**")

    st.session_state.score = calculate_score()
    st.subheader(f"🏆 점수: {st.session_state.score}점")

    if remaining_money >= 0:
        st.success("🎉 미션 성공!")
    else:
        st.error("❌ 미션 실패!")

    st.divider()

    # 느낀점
    st.session_state.reflection = st.text_area("느낀 점 작성")

    if st.button("랭킹 저장"):
        ranking = load_ranking()
        ranking.append({
            "name": st.session_state.player_name,
            "score": st.session_state.score,
            "difficulty": st.session_state.difficulty
        })
        ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)[:10]
        save_ranking(ranking)
        st.success("랭킹 저장 완료!")

    st.divider()

    st.subheader("🏅 TOP 10 랭킹")
    ranking = load_ranking()
    if ranking:
        for i, r in enumerate(ranking, 1):
            st.write(f"{i}. {r['name']} - {r['score']}점 ({r['difficulty']})")
    else:
        st.write("랭킹 데이터가 없습니다.")

    if st.button("다시 시작"):
        st.session_state.page = "start"
        st.session_state.budget = 0
        st.session_state.cart = []
        st.session_state.reflection = ""
        st.session_state.score = 0
        st.session_state.start_time = None
        st.rerun()

# -----------------------
# 페이지 분기
# -----------------------
if st.session_state.page == "start":
    start_page()
elif st.session_state.page == "shopping":
    shopping_page()
elif st.session_state.page == "result":
    result_page()
