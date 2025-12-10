import streamlit as st
import time
import json
import os

# -----------------------
# 기본 설정
# -----------------------
st.set_page_config(page_title="미션 쇼핑 앱 (랭킹 포함)", layout="centered")

RANKING_FILE = "ranking.json"

# 랭킹 파일 초기화
if not os.path.exists(RANKING_FILE):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def load_ranking():
    with open(RANKING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_ranking(data):
    with open(RANKING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

# 기본 상품
if "items" not in st.session_state:
    st.session_state.items = {
        "연필": 1000,
        "공책": 3000,
        "지우개": 1500,
        "필통": 5000,
        "가방": 20000
    }

# 난이도 설정
DIFFICULTY_SETTINGS = {
    "쉬움": {"time": 180, "bonus": 1},
    "보통": {"time": 120, "bonus": 2},
    "어려움": {"time": 60, "bonus": 3}
}

# -----------------------
# 1. 시작 화면
# -----------------------
def start_page():
    st.title("🎯 미션 시작")

    name = st.text_input("이름을 입력하세요")

    difficulty = st.radio("난이도 선택", ["쉬움", "보통", "어려움"])

    if difficulty == "쉬움":
        budgets = [30000, 50000, 70000]
    elif difficulty == "보통":
        budgets = [20000, 40000, 60000]
    else:
        budgets = [10000, 20000, 30000]

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
    st.title("🛒 쇼핑")

    elapsed = int(time.time() - st.session_state.start_time)
    remaining_time = st.session_state.time_limit - elapsed

    if remaining_time <= 0:
        st.warning("⏰ 시간 초과!")
        st.session_state.page = "result"
        st.rerun()

    st.write(f"이름: **{st.session_state.player_name}**")
    st.write(f"난이도: **{st.session_state.difficulty}**")
    st.write(f"남은 시간: **{remaining_time}초**")
    st.write(f"예산: **{st.session_state.budget:,}원**")

    total_price = sum(st.session_state.items[item] for item in st.session_state.cart)
    remaining_money = st.session_state.budget - total_price

    st.write(f"사용 금액: {total_price:,}원")
    st.write(f"남은 예산: {remaining_money:,}원")

    st.divider()

    # 상품 추가
    st.subheader("➕ 상품 추가")
    new_name = st.text_input("상품 이름")
    new_price = st.number_input("상품 가격", min_value=0, step=500)

    if st.button("상품 등록"):
        if new_name and new_price > 0:
            st.session_state.items[new_name] = new_price
            st.success("상품이 추가됐습니다.")
            st.rerun()

    st.divider()

    # 상품 목록
    st.subheader("상품 목록")
    for name, price in st.session_state.items.items():
        col1, col2, col3 = st.columns([3, 2, 2])
        col1.write(f"**{name}**")
        col2.write(f"{price:,}원")

        if col3.button(f"{name} 담기"):
            if remaining_money - price < 0:
                st.warning("❗ 예산 초과!")
            else:
                st.session_state.cart.append(name)
            st.rerun()

    st.divider()

    if st.button("구매 완료"):
        st.session_state.page = "result"
        st.rerun()

# -----------------------
# 점수 계산 함수
# -----------------------
def calculate_score():
    used = sum(st.session_state.items[item] for item in st.session_state.cart)
    remaining_money = st.session_state.budget - used

    difficulty_bonus = DIFFICULTY_SETTINGS[st.session_state.difficulty]["bonus"]
    time_used = int(time.time() - st.session_state.start_time)
    time_left = max(st.session_state.time_limit - time_used, 0)

    score = 0

    # 예산 활용 점수
    if remaining_money >= 0:
        efficiency = int(((used / st.session_state.budget) * 100))
        score += efficiency * 10

    # 남은 시간 보너스
    score += time_left * 2

    # 난이도 보너스
    score *= difficulty_bonus

    return score

# -----------------------
# 3. 결과 화면
# -----------------------
def result_page():
    st.title("✅ 결과")

    total_price = sum(st.session_state.items[item] for item in st.session_state.cart)
    remaining_money = st.session_state.budget - total_price

    st.subheader("📦 구매 내역")
    if st.session_state.cart:
        for item in st.session_state.cart:
            st.write(f"- {item} ({st.session_state.items[item]:,}원)")
    else:
        st.write("구매 내역 없음")

    st.write(f"사용 금액: **{total_price:,}원**")
    st.write(f"남은 금액: **{remaining_money:,}원**")

    # 점수 계산
    st.session_state.score = calculate_score()
    st.subheader(f"🏆 점수: {st.session_state.score}점")

    if remaining_money >= 0:
        st.success("미션 성공!")
    else:
        st.error("미션 실패!")

    # 느낀점
    st.session_state.reflection = st.text_area("느낀 점", value=st.session_state.reflection)

    # 랭킹 저장
    if st.button("랭킹에 저장"):
        ranking = load_ranking()

        ranking.append({
            "name": st.session_state.player_name,
            "score": st.session_state.score,
            "difficulty": st.session_state.difficulty
        })

        # 점수 기준 내림차순 정렬
        ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)[:10]

        save_ranking(ranking)
        st.success("랭킹이 저장되었습니다.")

    st.divider()

    # 랭킹 표시
    st.subheader("🏅 TOP 10 랭킹")
    ranking = load_ranking()

    if ranking:
        for i, r in enumerate(ranking, start=1):
            st.write(f"{i}. {r['name']} - {r['score']}점 ({r['difficulty']})")
    else:
        st.write("아직 랭킹이 없습니다.")

    if st.button("다시 시작"):
        st.session_state.page = "start"
        st.session_state.budget = 0
        st.session_state.cart = []
        st.session_state.reflection = ""
        st.session_state.start_time = None
        st.session_state.score = 0
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
