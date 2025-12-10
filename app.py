import streamlit as st

# 상품 목록 정의
PRODUCTS = {
    "연필": 500,
    "공책": 1500,
    "지우개": 300,
    "색연필 세트": 4000,
    "풀": 700,
    "가위": 1200,
    "자": 600,
    "클립": 200,
    "스티커": 1000,
    "형광펜": 900
}

# --- 1. 상태 초기화 (Session State) ---
def init_session_state():
    """웹 앱의 세션 상태를 초기화합니다."""
    if 'page' not in st.session_state:
        st.session_state['page'] = 'start'  # 'start', 'shopping', 'result'
    if 'budget' not in st.session_state:
        st.session_state['budget'] = 0
    if 'cart' not in st.session_state:
        st.session_state['cart'] = {}  # {상품명: 수량}
    if 'notes' not in st.session_state:
        st.session_state['notes'] = ""

def calculate_current_cost():
    """장바구니에 담긴 상품의 총 금액을 계산합니다."""
    total_cost = 0
    for item, quantity in st.session_state.cart.items():
        total_cost += PRODUCTS[item] * quantity
    return total_cost

# --- 2. 화면 구성 요소 ---

def start_page():
    """
    1. 시작 화면: 학생이 미션을 선택하는 창
    - 미션별 예산 선택 기능
    - 미션 선택 완료 시 '쇼핑화면'으로 이동
    """
    st.title("💰 미션 선택 및 예산 설정")
    st.markdown("---")
    st.info("💡 **미션:** 예산 범위 안에서 필요한 학용품을 구입하세요.")

    st.header("미션 예산을 선택해주세요.")

    # 미션별 예산 설정
    missions = {
        "초급 미션 (가벼운 쇼핑)": 5000,
        "중급 미션 (다양한 물품 구입)": 10000,
        "고급 미션 (꼼꼼한 계획 필요)": 15000
    }

    # 라디오 버튼으로 미션 선택
    selected_mission = st.radio(
        "미션 선택:",
        list(missions.keys()),
        index=0
    )
    
  selected_mission = st.radio(
        "미션 선택:",
        list(missions.keys()),
        index=0
    )
    
    selected_budget = missions[selected_mission]
    
    # 이 부분을 수정하세요!
    st.subheader(f"선택하신 미션의 예산은 **{selected_budget:,d}원**입니다.") 
    
    st.markdown("---")

def shopping_page():
    """
    2. 쇼핑 화면: 예산 범위 안에서 상품을 선택하는 화면
    - 상품 목록, 가격 확인
    - 실시간 사용 금액 및 남은 예산 확인
    - 장바구니 목록 확인 및 상품 추가 기능
    - 예산 초과 시 경고 메시지
    """
    st.title("🛒 쇼핑하기")
    
    current_cost = calculate_current_cost()
    remaining_budget = st.session_state.budget - current_cost
    
    # 🌟 실시간 예산 정보 표시 (컬럼 사용)
    col1, col2, col3 = st.columns(3)
    col1.metric("총 예산", f"{st.session_state.budget: 목표:5,d}원")
    col2.metric("현재 사용 금액", f"{current_cost: 목표:5,d}원", delta=f"{-current_cost: 목표:5,d}", delta_color="inverse")
    col3.metric("남은 예산", f"{remaining_budget: 목표:5,d}원", delta=f"{remaining_budget: 목표:5,d}")

    st.markdown("---")
    
    if remaining_budget < 0:
        st.error("🚨 **경고:** 예산을 초과했습니다! 장바구니를 확인하여 일부 상품을 줄이거나 제거해야 합니다.")

    # 🌟 상품 목록과 장바구니를 위한 컬럼 분할
    col_products, col_cart = st.columns([2, 1])

    # --- 2-1. 상품 목록 (왼쪽 컬럼) ---
    with col_products:
        st.header("📚 상품 목록")
        for item, price in PRODUCTS.items():
            col_item, col_price, col_add = st.columns([3, 1, 1])
            
            with col_item:
                st.write(f"**{item}**")
            with col_price:
                st.write(f"{price:,}원")
            with col_add:
                # '담기' 버튼을 클릭하면 장바구니에 1개 추가
                if st.button("담기", key=f"add_{item}"):
                    # 예산 초과 여부를 먼저 검사 (추가될 경우)
                    if remaining_budget - price < 0 and item not in st.session_state.cart:
                         st.warning(f"⚠️ **{item}**을 담으면 예산을 초과합니다! 신중하게 선택해주세요.")
                    elif remaining_budget - price < 0 and item in st.session_state.cart:
                         # 이미 카트에 있는 경우, 수량 추가 시 초과하는지 검사
                         current_total = calculate_current_cost()
                         if current_total + price > st.session_state.budget:
                              st.warning(f"⚠️ **{item}**을 더 담으면 예산을 초과합니다! 신중하게 선택해주세요.")
                         else:
                              # 수량 증가
                              st.session_state.cart[item] = st.session_state.cart.get(item, 0) + 1
                              st.rerun()

                    else:
                        # 정상적으로 추가
                        st.session_state.cart[item] = st.session_state.cart.get(item, 0) + 1
                        st.rerun()

    # --- 2-2. 장바구니 (오른쪽 컬럼) ---
    with col_cart:
        st.header("🛒 장바구니")
        
        if not st.session_state.cart or all(qty == 0 for qty in st.session_state.cart.values()):
            st.markdown("장바구니가 비어 있습니다.")
        else:
            cart_items = [(item, quantity, PRODUCTS[item]) 
                          for item, quantity in st.session_state.cart.items() if quantity > 0]

            # 장바구니 테이블 출력
            cart_data = [{"상품": item, "수량": qty, "개당 가격": f"{price:,}원", "총액": f"{qty * price:,}원"} 
                         for item, qty, price in cart_items]
            st.table(cart_data)
            
            # 장바구니 아이템별 수량 조절 버튼
            st.markdown("**수량 조절 / 삭제**")
            for item, quantity, price in cart_items:
                col_i, col_q, col_minus = st.columns([3, 1, 1])
                with col_i:
                    st.write(item)
                with col_q:
                    st.write(str(quantity))

                with col_minus:
                    # '빼기' 버튼 (수량 감소 또는 삭제)
                    if st.button("-1", key=f"remove_{item}", help=f"{item} 1개 제거"):
                        st.session_state.cart[item] -= 1
                        if st.session_state.cart[item] <= 0:
                            del st.session_state.cart[item]
                        st.rerun()

    st.markdown("---")
    
    # 🌟 구매 완료 버튼
    if st.button("구매 완료", type="primary"):
        st.session_state.page = 'result'
        st.rerun()

def result_page():
    """
    3. 결과 화면: 최종 구매 내역, 성공 여부, 느낀점 작성
    - 구매한 상품 목록 및 총액 표시
    - 예산 내 구매 성공 여부 표시
    - 느낀점/판단 작성 필드
    """
    st.title("🎉 미션 결과")

    # 최종 계산
    current_cost = calculate_current_cost()
    remaining_budget = st.session_state.budget - current_cost
    
    # 🌟 미션 성공 여부 판단 및 표시
    is_success = remaining_budget >= 0
    
    if is_success:
        st.balloons()
        st.success("✅ **미션 성공!** 예산 범위 안에서 현명하게 구매했습니다.")
    else:
        st.error("❌ **미션 실패!** 예산을 초과하여 구매했습니다. 다음에는 더 신중하게 계획해보세요.")
        
    st.markdown("---")

    st.header("💰 최종 구매 내역")
    
    # 최종 구매 내역 테이블
    cart_items = [(item, quantity, PRODUCTS[item]) 
                  for item, quantity in st.session_state.cart.items() if quantity > 0]

    if cart_items:
        cart_data = [{"상품": item, "수량": qty, "개당 가격": f"{price:,}원", "총액": f"{qty * price:,}원"} 
                     for item, qty, price in cart_items]
        st.table(cart_data)
    else:
        st.warning("구매한 상품이 없습니다.")


    # 🌟 최종 예산 요약 (metric)
    col1, col2, col3 = st.columns(3)
    col1.metric("총 예산", f"{st.session_state.budget: 목표:5,d}원")
    col2.metric("총 사용 금액", f"{current_cost: 목표:5,d}원")
    col3.metric("남은 예산", f"{remaining_budget: 목표:5,d}원")
    
    st.markdown("---")

    # 🌟 느낀점/판단 작성
    st.header("📝 나의 쇼핑 행동에 대한 느낀점 및 판단")
    
    # 텍스트 에어리어에 기존 저장된 내용을 불러옴
    st.session_state.notes = st.text_area(
        "구매 과정에서 느낀 점, 잘한 점, 아쉬운 점 등을 자유롭게 작성해보세요.",
        value=st.session_state.notes,
        height=150
    )
    
    # 저장 버튼 (텍스트 에어리어는 입력 시 자동으로 세션 상태 업데이트는 안되므로, 버튼으로 명시적 저장 유도)
    st.caption("작성하신 내용은 현재 세션에 저장됩니다.")
    
    st.markdown("---")

    # 🌟 다시 시작 버튼
    if st.button("🔄 다시 시작하기 / 새로운 미션", type="secondary"):
        st.session_state.page = 'start'
        st.session_state.budget = 0
        st.session_state.cart = {}
        st.session_state.notes = ""
        st.rerun()


# --- 메인 실행 로직 ---
if __name__ == "__main__":
    st.set_page_config(
        page_title="학생 쇼핑 미션 앱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 세션 상태 초기화
    init_session_state()

    # 페이지 라우팅
    if st.session_state.page == 'start':
        start_page()
    elif st.session_state.page == 'shopping':
        shopping_page()
    elif st.session_state.page == 'result':
        result_page()
