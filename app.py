import streamlit as st

# -----------------------
# 기본 설정
# -----------------------
st.set_page_config(page_title="미션 쇼핑 앱", layout="centered")

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "start"
if "budget" not in st.session_state:
    st.session_state.budget = 0
if "cart" not in st.session_state:
    st.session_state.cart = []
if "reflection" not in st.session_state:
    st.session_state.reflection = ""

# 상품 목록
items = {
    "연필": 1000,
    "공책": 3000,
    "지우개": 1500,
    "필통": 5000,
    "가방": 20000
}

# -----------------------
# 1. 시작 화면
# -----------------------
def start_page():
    st.title("🎯 미션 선택 화면")

    st.write("미션을 선택하고 예산을 골라주세요.")

    budget = st.radio(
        "예산을 선택하세요:",
        options=[10000, 30000, 50000],
        format_func=lambda x: f"{x:,}원"
    )

    if st.button("미션 선택 완료"):
        st.session_state.budget = budget
        st.session_state.page = "shopping"
        st.session_state.cart = []
        st.session_state.reflection = ""
        st.rerun()

# -----------------------
# 2. 쇼핑 화면
# -----------------------
def shopping_page():
    st.title("🛒 쇼핑 화면")

    st.write(f"현재 예산: **{st.session_state.budget:,}원**")

    total_price = sum(items[item] for item in st.session_state.cart)
    remaining = st.session_state.budget - total_price

    st.write(f"현재 사용 금액: {total_price:,}원")
    st.write(f"남은 금액: {remaining:,}원")

    st.divider()
    st.subheader("상품 목록")

    for name, price in items.items():
        col1, col2, col3 = st.columns([3, 2, 2])
        col1.write(f"**{name}**")
        col2.write(f"{price:,}원")

        if col3.button(f"{name} 담기"):
            if remaining - price < 0:
                st.warning("❗ 예산을 초과할 수 없습니다.")
            else:
                st.session_state.cart.append(name)
            st.rerun()

    st.divider()

    st.subheader("🧺 장바구니")
    if st.session_state.cart:
        for item in st.session_state.cart:
            st.write(f"- {item} ({items[item]:,}원)")
    else:
        st.write("장바구니가 비어 있습니다.")

    if st.button("구매 완료 → 결과 화면"):
        st.session_state.page = "result"
        st.rerun()

# -----------------------
# 3. 결과 화면
# -----------------------
def result_page():
    st.title("✅ 결과 화면")

    total_price = sum(items[item] for item in st.session_state.cart)
    remaining = st.session_state.budget - total_price

    st.subheader("📦 구매한 상품")
    if st.session_state.cart:
        for item in st.session_state.cart:
            st.write(f"- {item} ({items[item]:,}원)")
    else:
        st.write("구매한 상품이 없습니다.")

    st.divider()
    st.write(f"총 사용 금액: **{total_price:,}원**")
    st.write(f"남은 금액: **{remaining:,}원**")

    if remaining >= 0:
        st.success("🎉 미션 성공! 예산 안에서 구매했습니다.")
    else:
        st.error("❌ 미션 실패! 예산을 초과했습니다.")

    st.divider()
    st.subheader("📝 느낀 점 작성")
    st.session_state.reflection = st.text_area(
        "자신의 구매 판단에 대해 느낀 점을 작성하세요.",
        value=st.session_state.reflection
    )

    if st.button("처음으로 돌아가기"):
        st.session_state.page = "start"
        st.session_state.budget = 0
        st.session_state.cart = []
        st.session_state.reflection = ""
        st.rerun()

# -----------------------
# 화면 라우팅
# -----------------------
if st.session_state.page == "start":
    start_page()
elif st.session_state.page == "shopping":
    shopping_page()
elif st.session_state.page == "result":
    result_page()
