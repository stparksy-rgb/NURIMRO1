import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import hashlib

# 페이지 설정
st.set_page_config(
    page_title="누리엠알오 장부관리",
    page_icon="📊",
    layout="wide"
)

# 비밀번호 해싱 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 로그인 체크
def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in

# 로그인 화면
def login_page():
    st.markdown("<h1 style='text-align: center; color: #4a90e2;'>🔐 누리엠알오 장부관리</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #cccccc;'>로그인이 필요합니다</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🔓 로그인", use_container_width=True, type="primary"):
                # 비밀번호: 1248
                correct_hash = hash_password("1248")
                input_hash = hash_password(password)
                
                if input_hash == correct_hash:
                    st.session_state.logged_in = True
                    st.success("✅ 로그인 성공!")
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 틀렸습니다.")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.info("💡 **비밀번호를 잊으셨나요?**\n\n관리자에게 문의하세요.")

# 로그아웃 함수
def logout():
    st.session_state.logged_in = False
    st.rerun()

# 커스텀 CSS - 세련된 다크 테마 (글자 2/3 크기)
st.markdown("""
<style>
    /* ==================== 전체 배경 ==================== */
    .stApp {
        background-color: #0f0f0f !important;
        color: #e0e0e0 !important;
    }
    
    /* 메인 컨텐츠 영역 */
    .main .block-container {
        background-color: #0f0f0f !important;
        padding: 1.5rem !important;
        max-width: 1400px !important;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    /* ==================== 텍스트 스타일 (2/3 크기) ==================== */
    /* 일반 텍스트 */
    .stApp p, .stApp span, .stApp div, .stApp label {
        color: #e0e0e0 !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
    }
    
    /* 제목 */
    h1 {
        color: #4fc3f7 !important;
        font-size: 2.0rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        border-bottom: 2px solid #1e88e5 !important;
        padding-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #81c784 !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        color: #ffb74d !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.8rem !important;
    }
    
    h4 {
        color: #e0e0e0 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    /* ==================== 입력 필드 ==================== */
    /* 텍스트 입력 */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 3px solid #666666 !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        padding: 14px !important;
        border-radius: 8px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4a90e2 !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #888888 !important;
        font-weight: 500 !important;
    }
    
    /* 텍스트 영역 */
    .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 3px solid #666666 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        padding: 14px !important;
        border-radius: 8px !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #4a90e2 !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #888888 !important;
        font-weight: 500 !important;
    }
    
    /* 숫자 입력 */
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 3px solid #666666 !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        padding: 14px !important;
        border-radius: 8px !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #4a90e2 !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
    }
    
    /* 날짜 입력 */
    .stDateInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 3px solid #666666 !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        padding: 14px !important;
        border-radius: 8px !important;
    }
    
    .stDateInput > div > div > input:focus {
        border-color: #4a90e2 !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
    }
    
    /* ==================== 드롭다운 (셀렉트박스) - 선택값 보이게! ==================== */
    /* 드롭다운 컨테이너 */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 3px solid #666666 !important;
        border-radius: 8px !important;
    }
    
    /* 드롭다운 기본 스타일 */
    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    /* 드롭다운 선택된 값을 담는 컨테이너 */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        padding: 10px !important;
    }
    
    /* 선택된 값 텍스트 - 최우선 적용! */
    .stSelectbox [data-baseweb="select"] > div > div {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div > div > div {
        color: #000000 !important;
    }
    
    /* 모든 span 태그 */
    .stSelectbox [data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* input 태그 (검색용) */
    .stSelectbox [data-baseweb="select"] input {
        color: #000000 !important;
        caret-color: #000000 !important;
    }
    
    /* placeholder */
    .stSelectbox [data-baseweb="select"] input::placeholder {
        color: #666666 !important;
    }
    
    /* 선택된 값을 보여주는 모든 요소에 강제 적용 */
    .stSelectbox div[role="button"] {
        color: #000000 !important;
    }
    
    .stSelectbox div[role="button"] * {
        color: #000000 !important;
    }
    
    /* 드롭다운 화살표 */
    .stSelectbox svg {
        fill: #000000 !important;
    }
    
    /* 드롭다운 열렸을 때 메뉴 */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 2px solid #666666 !important;
    }
    
    /* 드롭다운 옵션 리스트 */
    [role="listbox"] {
        background-color: #ffffff !important;
    }
    
    /* 드롭다운 각 옵션 */
    [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
    }
    
    /* 드롭다운 옵션 호버 */
    [role="option"]:hover {
        background-color: #e8e8e8 !important;
        color: #000000 !important;
    }
    
    /* 드롭다운 선택된 옵션 */
    [role="option"][aria-selected="true"] {
        background-color: #d0d0d0 !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* ==================== 멀티셀렉트 ==================== */
    .stMultiSelect [data-baseweb="select"] {
        background-color: #1e1e1e !important;
        border: 2px solid #424242 !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #1e88e5 !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
    }
    
    /* ==================== 버튼 ==================== */
    .stButton > button {
        background-color: #4a90e2 !important;
        color: #ffffff !important;
        border: none !important;
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        padding: 16px 32px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #357abd !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4) !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #28a745 !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #218838 !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #6c757d !important;
    }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background-color: #17a2b8 !important;
        color: #ffffff !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
    }
    
    /* ==================== 라디오 버튼 ==================== */
    .stRadio > div {
        gap: 1rem !important;
    }
    
    .stRadio [role="radiogroup"] label {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        padding: 12px 20px !important;
        border-radius: 8px !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        border: 2px solid #4a4a4a !important;
        cursor: pointer !important;
    }
    
    .stRadio [role="radiogroup"] label:hover {
        background-color: #3a3a3a !important;
        border-color: #6a6a6a !important;
    }
    
    .stRadio [role="radiogroup"] [data-checked="true"] label {
        background-color: #4a90e2 !important;
        border-color: #4a90e2 !important;
        color: #ffffff !important;
    }
    
    /* 라디오 버튼 원형 아이콘 */
    .stRadio input[type="radio"] {
        width: 20px !important;
        height: 20px !important;
    }
    
    /* ==================== 체크박스 ==================== */
    .stCheckbox label {
        font-size: 1.0rem !important;
        font-weight: 500 !important;
        color: #e0e0e0 !important;
    }
    
    /* ==================== 메트릭 (지표) ==================== */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #4fc3f7 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        color: #b0b0b0 !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
    }
    
    /* ==================== 데이터프레임 ==================== */
    .stDataFrame {
        font-size: 0.95rem !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background-color: #1a1a1a !important;
        border: 1px solid #424242 !important;
        border-radius: 6px !important;
    }
    
    /* ==================== 정보 박스 ==================== */
    .stInfo {
        background-color: #1e3a5f !important;
        border-left: 4px solid #1e88e5 !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
        font-size: 1.0rem !important;
    }
    
    .stSuccess {
        background-color: #1b5e20 !important;
        border-left: 4px solid #43a047 !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
        font-size: 1.0rem !important;
    }
    
    .stWarning {
        background-color: #5d4037 !important;
        border-left: 4px solid #ff9800 !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
        font-size: 1.0rem !important;
    }
    
    .stError {
        background-color: #5d1f1f !important;
        border-left: 4px solid #f44336 !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
        font-size: 1.0rem !important;
    }
    
    /* ==================== 탭 ==================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: transparent !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e1e !important;
        color: #b0b0b0 !important;
        border-radius: 6px 6px 0 0 !important;
        padding: 10px 20px !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1e88e5 !important;
        color: #ffffff !important;
    }
    
    /* ==================== 마크다운 ==================== */
    .stMarkdown {
        color: #e0e0e0 !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
    }
    
    .stMarkdown a {
        color: #4fc3f7 !important;
        text-decoration: none !important;
        font-weight: 600 !important;
    }
    
    .stMarkdown a:hover {
        color: #81d4fa !important;
        text-decoration: underline !important;
    }
    
    /* ==================== 로딩 스피너 ==================== */
    .stSpinner > div {
        border-top-color: #1e88e5 !important;
    }
    
    /* ==================== 사이드바 메뉴 ==================== */
    [data-testid="stSidebar"] .stRadio > label {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    
    /* ==================== 추가 미세 조정 ==================== */
    input::placeholder, textarea::placeholder {
        color: #757575 !important;
        opacity: 1 !important;
    }
    
    /* 포커스 상태 */
    input:focus, textarea:focus, select:focus {
        outline: none !important;
        border-color: #1e88e5 !important;
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.2) !important;
    }
    
    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #424242 !important;
        border-radius: 4px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #616161 !important;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 파일 경로
DATA_FILE = "data/ledger.csv"
BASE_RECEIVABLE_FILE = "data/base_receivables.csv"
PRODUCTS_FILE = "data/products.csv"

# 세션 상태 초기화
if 'ledger_df' not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.ledger_df = pd.read_csv(DATA_FILE, parse_dates=['날짜'])
    else:
        st.session_state.ledger_df = pd.DataFrame(columns=['날짜', '거래처', '품목', '수량', '단가', '공급가액', '부가세', '참조'])

# 기초 미수금 초기화
if 'base_receivables_df' not in st.session_state:
    if os.path.exists(BASE_RECEIVABLE_FILE):
        st.session_state.base_receivables_df = pd.read_csv(BASE_RECEIVABLE_FILE)
    else:
        st.session_state.base_receivables_df = pd.DataFrame(columns=['거래처', '기초미수금', '기준일자'])

# 품목 데이터 초기화
if 'products_df' not in st.session_state:
    if os.path.exists(PRODUCTS_FILE):
        st.session_state.products_df = pd.read_csv(PRODUCTS_FILE)
    else:
        st.session_state.products_df = pd.DataFrame(columns=['품목코드', '품목명', '카테고리', '규격'])

# 데이터 저장 함수
def save_data():
    st.session_state.ledger_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def save_base_receivables():
    st.session_state.base_receivables_df.to_csv(BASE_RECEIVABLE_FILE, index=False, encoding='utf-8-sig')

def save_products():
    st.session_state.products_df.to_csv(PRODUCTS_FILE, index=False, encoding='utf-8-sig')

# ==================== 로그인 체크 ====================
if not check_login():
    login_page()
    st.stop()

# ==================== 메인 애플리케이션 ====================
# 사이드바 - 메뉴
st.sidebar.title("📋 장부 관리 시스템")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "메뉴 선택",
    ["🏠 대시보드", "➕ 거래 입력", "📄 거래 내역", "📊 통계 분석", "💰 외상 관리", "📦 품목 관리", "👥 거래처 관리", "⚙️ 설정"]
)

# ==================== 대시보드 ====================
if menu == "🏠 대시보드":
    st.title("📊 대시보드")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("아직 거래 내역이 없습니다. '거래 입력' 메뉴에서 데이터를 추가해주세요.")
    else:
        # 날짜 필터
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", value=df['날짜'].min().date())
        with col2:
            end_date = st.date_input("종료일", value=df['날짜'].max().date())
        
        # 날짜 필터링
        mask = (df['날짜'].dt.date >= start_date) & (df['날짜'].dt.date <= end_date)
        df_filtered = df[mask].copy()
        
        # 주요 지표
        st.markdown("### 📈 주요 지표")
        
        # 수입/지출 계산
        입금_df = df_filtered[df_filtered['참조'].str.contains('입금', na=False)]
        출금_df = df_filtered[df_filtered['참조'].str.contains('출금', na=False)]
        외입_df = df_filtered[df_filtered['참조'].str.contains('외입', na=False)]
        
        총수입 = 입금_df['공급가액'].sum()
        총지출 = abs(출금_df['공급가액'].sum())
        총매입 = 외입_df[외입_df['공급가액'] > 0]['공급가액'].sum()
        총매입부가세 = 외입_df[외입_df['공급가액'] > 0]['부가세'].sum()
        순이익 = 총수입 - 총지출
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("💰 총 수입", f"{총수입:,.0f}원")
        with col2:
            st.metric("💸 총 지출", f"{총지출:,.0f}원")
        with col3:
            st.metric("📦 총 매입", f"{총매입:,.0f}원")
        with col4:
            st.metric("💵 순이익", f"{순이익:,.0f}원", delta=f"{(순이익/총수입*100):.1f}%" if 총수입 > 0 else "0%")
        with col5:
            st.metric("🧾 부가세(매입)", f"{총매입부가세:,.0f}원")
        
        st.markdown("---")
        
        # 차트
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📅 일별 수입/지출 추이")
            
            # 일별 집계
            입금_daily = 입금_df.groupby(입금_df['날짜'].dt.date)['공급가액'].sum().reset_index()
            입금_daily.columns = ['날짜', '수입']
            
            출금_daily = 출금_df.groupby(출금_df['날짜'].dt.date)['공급가액'].sum().abs().reset_index()
            출금_daily.columns = ['날짜', '지출']
            
            # 병합
            daily_df = pd.merge(입금_daily, 출금_daily, on='날짜', how='outer').fillna(0)
            
            if len(daily_df) > 0:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=daily_df['날짜'], y=daily_df['수입'], name='수입', marker_color='#2E7D32'))
                fig.add_trace(go.Bar(x=daily_df['날짜'], y=daily_df['지출'], name='지출', marker_color='#C62828'))
                fig.update_layout(barmode='group', height=400, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("해당 기간 데이터가 없습니다.")
        
        with col2:
            st.markdown("### 🏢 주요 거래처 TOP 10")
            
            # 거래처별 집계
            거래처_sum = df_filtered[df_filtered['참조'].str.contains('입금', na=False)].groupby('거래처')['공급가액'].sum().sort_values(ascending=False).head(10)
            
            if len(거래처_sum) > 0:
                fig = px.bar(
                    x=거래처_sum.values,
                    y=거래처_sum.index,
                    orientation='h',
                    labels={'x': '금액 (원)', 'y': '거래처'},
                    color=거래처_sum.values,
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("해당 기간 데이터가 없습니다.")
        
        # 월별 통계
        st.markdown("### 📆 월별 통계")
        
        df_filtered['년월'] = df_filtered['날짜'].dt.to_period('M').astype(str)
        
        월별_입금 = df_filtered[df_filtered['참조'].str.contains('입금', na=False)].groupby('년월')['공급가액'].sum()
        월별_출금 = df_filtered[df_filtered['참조'].str.contains('출금', na=False)].groupby('년월')['공급가액'].sum().abs()
        월별_매입 = df_filtered[df_filtered['참조'].str.contains('외입', na=False) & (df_filtered['공급가액'] > 0)].groupby('년월')['공급가액'].sum()
        
        월별_df = pd.DataFrame({
            '수입': 월별_입금,
            '지출': 월별_출금,
            '매입': 월별_매입,
            '순이익': 월별_입금 - 월별_출금
        }).fillna(0)
        
        월별_df = 월별_df.applymap(lambda x: f"{x:,.0f}")
        st.dataframe(월별_df, use_container_width=True)

# ==================== 거래 입력 ====================
elif menu == "➕ 거래 입력":
    st.title("➕ 거래 입력")
    
    df = st.session_state.ledger_df
    products_df = st.session_state.products_df
    
    # 기존 거래처 목록
    거래처_list = sorted(df['거래처'].dropna().unique().tolist()) if len(df) > 0 else []
    
    # ========== 가로 레이아웃: 좌우 2분할 ==========
    left_col, right_col = st.columns([1, 1])
    
    # ========== 좌측: 선택 영역 ==========
    with left_col:
        st.markdown("### 📋 거래 정보")
        
        거래일자 = st.date_input("거래 날짜", value=datetime.now())
        
        st.markdown("---")
        
        # 거래처 입력
        st.markdown("#### 거래처")
        거래처_입력방식 = st.radio("", ["기존 거래처 선택", "새 거래처 입력"], horizontal=True, label_visibility="collapsed")
        
        if 거래처_입력방식 == "기존 거래처 선택":
            거래처 = st.selectbox("거래처 선택", [""] + 거래처_list, label_visibility="collapsed")
            
            # ✅ 선택된 거래처 명확히 표시!
            if 거래처 and 거래처 != "":
                st.markdown(f"""
                <div style='background-color: #e3f2fd; border: 2px solid #1e88e5; border-radius: 8px; padding: 12px; margin: 10px 0;'>
                    <h4 style='color: #1565c0; margin: 0;'>✅ 선택된 거래처</h4>
                    <h3 style='color: #0d47a1; margin: 5px 0;'>{거래처}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # 미수금 표시
                기초미수금_dict = st.session_state.base_receivables_df.set_index('거래처')['기초미수금'].to_dict()
                기초미수금 = 기초미수금_dict.get(거래처, 0)
                
                거래처_df = df[df['거래처'] == 거래처]
                외입_df = 거래처_df[거래처_df['참조'].str.contains('외입|외출', na=False)]
                입금_df = 거래처_df[거래처_df['참조'].str.contains('입금', na=False)]
                
                총외상 = 외입_df['공급가액'].sum() + 외입_df['부가세'].sum()
                총입금 = 입금_df['공급가액'].sum()
                미수금 = 기초미수금 + 총외상 + 총입금
                
                if 미수금 > 0:
                    st.warning(f"⚠️ **미수금:** {미수금:,.0f}원")
                else:
                    st.success("✅ 미수금 없음")
        else:
            거래처 = st.text_input("거래처명", label_visibility="collapsed")
            if 거래처:
                st.markdown(f"""
                <div style='background-color: #e8f5e9; border: 2px solid #43a047; border-radius: 8px; padding: 12px; margin: 10px 0;'>
                    <h4 style='color: #2e7d32; margin: 0;'>✅ 입력된 거래처</h4>
                    <h3 style='color: #1b5e20; margin: 5px 0;'>{거래처}</h3>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 품목 입력
        st.markdown("#### 품목")
        품목입력방식 = st.radio("", ["품목 검색", "직접 입력"], horizontal=True, label_visibility="collapsed")
        
        if 품목입력방식 == "품목 검색":
            if len(products_df) > 0:
                # 검색 필터
                검색어 = st.text_input("품목 검색", placeholder="품목명 또는 숫자코드 입력 (예: 절단석, 001)", label_visibility="collapsed")
                
                # 검색어에 따라 필터링
                if 검색어 and len(검색어) >= 1:
                    # 숫자만 입력하면 P- 붙여서 검색
                    if 검색어.isdigit():
                        검색코드 = f"P-{검색어.zfill(3)}"  # 001, 01, 1 모두 P-001로 변환
                        검색결과 = products_df[
                            products_df['품목코드'].str.contains(검색코드, case=False, na=False)
                        ]
                    else:
                        검색결과 = products_df[
                            products_df['품목코드'].str.contains(검색어, case=False, na=False) |
                            products_df['품목명'].str.contains(검색어, case=False, na=False) |
                            products_df['카테고리'].str.contains(검색어, case=False, na=False)
                        ]
                else:
                    # 검색어 없으면 상위 20개만
                    검색결과 = products_df.head(20)
                
                if len(검색결과) > 0:
                    if 검색어:
                        st.success(f"🔍 {len(검색결과)}개 품목 발견!")
                    else:
                        st.info(f"📦 최근 {len(검색결과)}개 품목")
                    
                    # 검색 결과를 바로 리스트로 표시
                    품목_옵션 = []
                    for _, row in 검색결과.iterrows():
                        # 품목코드에서 숫자만 추출해서 간단히 표시
                        코드숫자 = row['품목코드'].replace('P-', '')
                        옵션 = f"[{코드숫자}] {row['품목명']}"
                        if pd.notna(row['카테고리']):
                            옵션 += f" - {row['카테고리']}"
                        if pd.notna(row['규격']):
                            옵션 += f" {row['규격']}"
                        품목_옵션.append((옵션, row['품목코드']))
                    
                    선택품목_idx = st.selectbox("품목 선택", range(len(품목_옵션) + 1), 
                                              format_func=lambda x: "선택하세요" if x == 0 else 품목_옵션[x-1][0],
                                              key="search_result", label_visibility="collapsed")
                    
                    if 선택품목_idx and 선택품목_idx > 0:
                        # 선택된 품목 정보 추출
                        품목코드 = 품목_옵션[선택품목_idx-1][1]
                        품목정보 = products_df[products_df['품목코드'] == 품목코드].iloc[0]
                        품목 = f"{품목정보['품목명']} @ {품목정보['규격']}"
                        
                        # ✅ 선택된 품목 명확히 표시!
                        st.markdown(f"""
                        <div style='background-color: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; padding: 12px; margin: 10px 0;'>
                            <h4 style='color: #e65100; margin: 0;'>✅ 선택된 품목</h4>
                            <h3 style='color: #bf360c; margin: 5px 0;'>{품목}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        품목 = ""
                else:
                    st.warning("❌ 검색 결과가 없습니다.")
                    품목 = ""
            else:
                st.warning("등록된 품목이 없습니다. '직접 입력'을 사용하세요.")
                품목 = st.text_area("품목 [적요]", height=80, label_visibility="collapsed")
        else:
            품목 = st.text_area("품목 [적요]", height=80, label_visibility="collapsed")
            if 품목:
                st.markdown(f"""
                <div style='background-color: #f3e5f5; border: 2px solid #9c27b0; border-radius: 8px; padding: 12px; margin: 10px 0;'>
                    <h4 style='color: #6a1b9a; margin: 0;'>✅ 입력된 품목</h4>
                    <h3 style='color: #4a148c; margin: 5px 0;'>{품목[:50]}...</h3>
                </div>
                """, unsafe_allow_html=True)
    
    # ========== 우측: 입력 + 계산 영역 ==========
    with right_col:
        st.markdown("### 💰 금액 정보")
        
        거래유형 = st.selectbox("거래 유형", ["=입금", "=출금", "=외입", "=외출", "=견적"])
        
        # ✅ 선택된 거래 유형 명확히 표시!
        if 거래유형:
            유형_색상 = {
                "=입금": ("#e8f5e9", "#43a047", "#2e7d32", "#1b5e20"),
                "=출금": ("#ffebee", "#e53935", "#c62828", "#b71c1c"),
                "=외입": ("#e3f2fd", "#1e88e5", "#1565c0", "#0d47a1"),
                "=외출": ("#fff3e0", "#fb8c00", "#f57c00", "#e65100"),
                "=견적": ("#f3e5f5", "#8e24aa", "#6a1b9a", "#4a148c"),
            }
            배경, 테두리, 제목, 내용 = 유형_색상.get(거래유형, ("#fff", "#000", "#000", "#000"))
            
            st.markdown(f"""
            <div style='background-color: {배경}; border: 2px solid {테두리}; border-radius: 8px; padding: 12px; margin: 10px 0;'>
                <h4 style='color: {제목}; margin: 0;'>✅ 선택된 거래 유형</h4>
                <h3 style='color: {내용}; margin: 5px 0;'>{거래유형}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        수량 = st.number_input("수량", min_value=0, value=0, step=1, format="%d")
        단가 = st.number_input("단가", min_value=0.0, value=0.0, step=100.0)
        
        # 공급가액 자동 계산
        if 거래유형 == "=출금":
            공급가액 = -(수량 * 단가 if 수량 > 0 and 단가 > 0 else st.number_input("공급가액", value=0.0, step=1000.0))
        else:
            공급가액 = 수량 * 단가 if 수량 > 0 and 단가 > 0 else st.number_input("공급가액", value=0.0, step=1000.0)
        
        # 부가세 자동 계산 (외입/외출인 경우)
        if 거래유형 in ["=외입", "=외출"]:
            부가세_적용 = st.checkbox("부가세 10% 적용", value=True)
            부가세 = round(공급가액 * 0.1) if 부가세_적용 else 0.0
        else:
            부가세 = 0.0
        
        # 💰 금액 요약 (크고 명확하게!)
        st.markdown("---")
        st.markdown("### 📊 금액 요약")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("공급가액", f"{공급가액:,.0f}원")
        with col_b:
            st.metric("부가세", f"{부가세:,.0f}원")
        with col_c:
            st.metric("합계", f"{공급가액+부가세:,.0f}원", delta=f"{부가세:,.0f}원")
    
    # ========== 하단: 저장 버튼 ==========
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 저장하기", type="primary", use_container_width=True):
            if not 거래처:
                st.error("❌ 거래처를 입력해주세요.")
            else:
                new_row = pd.DataFrame([{
                    '날짜': pd.to_datetime(거래일자),
                    '거래처': 거래처,
                    '품목': 품목,
                    '수량': 수량,
                    '단가': 단가,
                    '공급가액': 공급가액,
                    '부가세': 부가세,
                    '참조': 거래유형
                }])
                
                st.session_state.ledger_df = pd.concat([st.session_state.ledger_df, new_row], ignore_index=True)
                save_data()
                st.success("✅ 거래 내역이 저장되었습니다!")
                st.balloons()
                st.rerun()

# ==================== 거래 내역 ====================
elif menu == "📄 거래 내역":
    st.title("📄 거래 내역")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("아직 거래 내역이 없습니다.")
    else:
        # 필터
        col1, col2, col3 = st.columns(3)
        
        with col1:
            거래유형_필터 = st.multiselect("거래 유형", df['참조'].unique(), default=df['참조'].unique())
        with col2:
            거래처_필터 = st.multiselect("거래처", ["전체"] + sorted(df['거래처'].dropna().unique().tolist()), default=["전체"])
        with col3:
            검색어 = st.text_input("품목 검색", "")
        
        # 미수금 실시간 표시
        if "전체" not in 거래처_필터 and len(거래처_필터) == 1:
            선택거래처 = 거래처_필터[0]
            
            # 미수금 계산
            기초미수금_dict = st.session_state.base_receivables_df.set_index('거래처')['기초미수금'].to_dict()
            기초미수금 = 기초미수금_dict.get(선택거래처, 0)
            
            거래처_df = df[df['거래처'] == 선택거래처]
            외입_df = 거래처_df[거래처_df['참조'].str.contains('외입|외출', na=False)]
            입금_df = 거래처_df[거래처_df['참조'].str.contains('입금', na=False)]
            
            총외상 = 외입_df['공급가액'].sum() + 외입_df['부가세'].sum()
            총입금 = 입금_df['공급가액'].sum()
            미수금 = 기초미수금 + 총외상 + 총입금
            
            # 미수금 표시
            if 미수금 > 0:
                st.markdown(f"""
                <div style='background-color: #fee; border: 2px solid #f88; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #c00; margin: 0;'>⚠️ 미수금 현황</h3>
                    <h2 style='color: #c00; margin: 5px 0;'>{미수금:,.0f}원</h2>
                    <p style='color: #666; margin: 5px 0; font-size: 0.9em;'>
                        기초미수금: {기초미수금:,.0f}원 | 
                        외상: {총외상:,.0f}원 | 
                        입금: {총입금:,.0f}원
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #efe; border: 2px solid #8c8; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #080; margin: 0;'>✅ 미수금 없음</h3>
                    <p style='color: #666; margin: 5px 0;'>현재 미수금이 없습니다.</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 필터링
        df_filtered = df[df['참조'].isin(거래유형_필터)]
        
        if "전체" not in 거래처_필터:
            df_filtered = df_filtered[df_filtered['거래처'].isin(거래처_필터)]
        
        if 검색어:
            df_filtered = df_filtered[df_filtered['품목'].str.contains(검색어, na=False)]
        
        # 정렬
        df_filtered = df_filtered.sort_values('날짜', ascending=False)
        
        st.markdown(f"### 총 {len(df_filtered)}건")
        
        # 데이터 표시
        display_df = df_filtered.copy()
        display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
        display_df['공급가액'] = display_df['공급가액'].apply(lambda x: f"{x:,.0f}")
        display_df['부가세'] = display_df['부가세'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, height=600)
        
        # 엑셀 다운로드
        st.markdown("---")
        
        @st.cache_data
        def convert_to_excel(dataframe):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                dataframe.to_excel(writer, index=False, sheet_name='거래내역')
            return output.getvalue()
        
        excel_data = convert_to_excel(df_filtered)
        
        st.download_button(
            label="📥 엑셀 다운로드",
            data=excel_data,
            file_name=f"거래내역_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==================== 통계 분석 ====================
elif menu == "📊 통계 분석":
    st.title("📊 통계 분석")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("아직 거래 내역이 없습니다.")
    else:
        분석유형 = st.selectbox("분석 유형", ["월별 분석", "거래처별 분석", "품목별 분석", "부가세 분석"])
        
        if 분석유형 == "월별 분석":
            st.markdown("### 📆 월별 수입/지출 분석")
            
            df['년월'] = df['날짜'].dt.to_period('M').astype(str)
            
            입금_df = df[df['참조'].str.contains('입금', na=False)].groupby('년월')['공급가액'].sum()
            출금_df = df[df['참조'].str.contains('출금', na=False)].groupby('년월')['공급가액'].sum().abs()
            매입_df = df[df['참조'].str.contains('외입', na=False) & (df['공급가액'] > 0)].groupby('년월')['공급가액'].sum()
            부가세_df = df[df['참조'].str.contains('외입', na=False) & (df['공급가액'] > 0)].groupby('년월')['부가세'].sum()
            
            월별_df = pd.DataFrame({
                '수입': 입금_df,
                '지출': 출금_df,
                '매입': 매입_df,
                '부가세': 부가세_df,
                '순이익': 입금_df - 출금_df
            }).fillna(0)
            
            # 그래프
            fig = go.Figure()
            fig.add_trace(go.Bar(name='수입', x=월별_df.index, y=월별_df['수입'], marker_color='#2E7D32'))
            fig.add_trace(go.Bar(name='지출', x=월별_df.index, y=월별_df['지출'], marker_color='#C62828'))
            fig.add_trace(go.Scatter(name='순이익', x=월별_df.index, y=월별_df['순이익'], mode='lines+markers', line=dict(color='#1976D2', width=3)))
            
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # 테이블
            st.dataframe(월별_df.applymap(lambda x: f"{x:,.0f}"), use_container_width=True)
        
        elif 분석유형 == "거래처별 분석":
            st.markdown("### 🏢 거래처별 분석")
            
            거래처별 = df[df['참조'].str.contains('입금', na=False)].groupby('거래처').agg({
                '공급가액': 'sum',
                '날짜': 'count'
            }).rename(columns={'날짜': '거래횟수'}).sort_values('공급가액', ascending=False)
            
            거래처별['평균거래액'] = 거래처별['공급가액'] / 거래처별['거래횟수']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### TOP 20 거래처")
                top20 = 거래처별.head(20).copy()
                top20['공급가액'] = top20['공급가액'].apply(lambda x: f"{x:,.0f}")
                top20['평균거래액'] = top20['평균거래액'].apply(lambda x: f"{x:,.0f}")
                st.dataframe(top20, use_container_width=True)
            
            with col2:
                st.markdown("#### 거래처별 매출 비중")
                fig = px.pie(거래처별.head(10), values='공급가액', names=거래처별.head(10).index, hole=0.4)
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        elif 분석유형 == "품목별 분석":
            st.markdown("### 📦 품목별 매출 분석")
            
            # 품목에서 키워드 추출 (간단히)
            df_입금 = df[df['참조'].str.contains('입금', na=False)].copy()
            
            if len(df_입금) > 0:
                품목별 = df_입금.groupby('품목')['공급가액'].sum().sort_values(ascending=False).head(20)
                
                st.bar_chart(품목별)
                
                st.dataframe(품목별.apply(lambda x: f"{x:,.0f}"), use_container_width=True)
            else:
                st.info("입금 데이터가 없습니다.")
        
        elif 분석유형 == "부가세 분석":
            st.markdown("### 🧾 부가세 분석")
            
            df['년월'] = df['날짜'].dt.to_period('M').astype(str)
            
            매입부가세 = df[(df['참조'].str.contains('외입', na=False)) & (df['공급가액'] > 0)].groupby('년월')['부가세'].sum()
            
            부가세_df = pd.DataFrame({
                '매입부가세': 매입부가세
            }).fillna(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 월별 매입 부가세")
                st.bar_chart(부가세_df['매입부가세'])
            
            with col2:
                st.markdown("#### 통계")
                st.metric("총 매입부가세", f"{부가세_df['매입부가세'].sum():,.0f}원")
                st.metric("월평균 매입부가세", f"{부가세_df['매입부가세'].mean():,.0f}원")

# ==================== 외상 관리 ====================
elif menu == "💰 외상 관리":
    st.title("💰 외상 관리")
    
    df = st.session_state.ledger_df.copy()
    base_rec = st.session_state.base_receivables_df.copy()
    
    if len(df) == 0:
        st.info("아직 거래 내역이 없습니다.")
    else:
        # 외상 매출 (입금 전)
        st.markdown("### 📤 외상 매출 (미수금)")
        
        외상매출 = df[df['참조'].str.contains('외입|견적', na=False) & (df['공급가액'] > 0)].copy()
        입금내역 = df[df['참조'].str.contains('입금', na=False)].copy()
        
        # 거래처별 외상 집계
        거래처별_외상 = 외상매출.groupby('거래처').agg({
            '공급가액': 'sum',
            '부가세': 'sum',
            '날짜': 'max'
        }).rename(columns={'날짜': '최근거래일'})
        
        거래처별_입금 = 입금내역.groupby('거래처')['공급가액'].sum()
        
        거래처별_외상['입금액'] = 거래처별_입금
        거래처별_외상 = 거래처별_외상.fillna(0)
        
        # 기초 미수금 추가 (241231 기준)
        기초미수금_dict = {}
        if len(base_rec) > 0:
            for _, row in base_rec.iterrows():
                기초미수금_dict[row['거래처']] = row['기초미수금']
        
        거래처별_외상['기초미수금'] = 거래처별_외상.index.map(lambda x: 기초미수금_dict.get(x, 0))
        
        # 미수금 계산: 기초미수금 + 외상 + 부가세 - 입금
        거래처별_외상['미수금'] = (거래처별_외상['기초미수금'] + 
                                    거래처별_외상['공급가액'] + 
                                    거래처별_외상['부가세'] - 
                                    거래처별_외상['입금액'])
        
        # 미수금이 있는 거래처만
        미수금_df = 거래처별_외상[거래처별_외상['미수금'] > 0].sort_values('미수금', ascending=False)
        
        if len(미수금_df) > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 미수금", f"{미수금_df['미수금'].sum():,.0f}원")
            with col2:
                st.metric("미수 거래처 수", f"{len(미수금_df)}개")
            with col3:
                st.metric("최대 미수금", f"{미수금_df['미수금'].max():,.0f}원")
            
            st.markdown("---")
            
            # 상세 내역
            display_df = 미수금_df.copy()
            display_df['최근거래일'] = display_df['최근거래일'].dt.strftime('%Y-%m-%d')
            display_df = display_df.applymap(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)
            
            st.dataframe(display_df, use_container_width=True)
            
            st.markdown("---")
            st.info("💡 **팁:** 미수금이 정확하지 않다면 '설정 → 기초 미수금 설정'에서 2024.12.31 기준 미수금을 입력하세요!")
        else:
            st.success("✅ 미수금이 없습니다!")

# ==================== 품목 관리 ====================
elif menu == "📦 품목 관리":
    st.title("📦 품목 관리")
    
    products_df = st.session_state.products_df
    ledger_df = st.session_state.ledger_df
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📋 품목 목록", "➕ 품목 추가", "🔍 품목 검색"])
    
    # ===== 탭1: 품목 목록 (3단 레이아웃) =====
    with tab1:
        if len(products_df) > 0:
            # ========== 3단 레이아웃: 카테고리 | 품목 | 상세정보 ==========
            col_category, col_product, col_detail = st.columns([1, 1.5, 2.5])
            
            # ========== 1단: 카테고리 선택 ==========
            with col_category:
                st.markdown("### 📂 카테고리")
                
                # NaN 값 제거 후 정렬
                카테고리_unique = products_df['카테고리'].dropna().unique().tolist()
                카테고리_list = ["전체"] + sorted([x for x in 카테고리_unique if x])
                
                선택카테고리 = st.radio("", 카테고리_list, label_visibility="collapsed")
                
                st.markdown("---")
                
                # 카테고리별 개수 표시
                if 선택카테고리 == "전체":
                    st.info(f"📦 전체 {len(products_df)}개 품목")
                else:
                    개수 = len(products_df[products_df['카테고리'] == 선택카테고리])
                    st.info(f"📦 {개수}개 품목")
            
            # ========== 2단: 품목 선택 ==========
            with col_product:
                st.markdown("### 📦 품목 선택")
                
                # 카테고리 필터링
                if 선택카테고리 != "전체":
                    filtered_df = products_df[products_df['카테고리'] == 선택카테고리]
                else:
                    filtered_df = products_df
                
                if len(filtered_df) > 0:
                    # 품목 리스트를 라디오 버튼으로
                    품목_옵션 = []
                    for _, row in filtered_df.iterrows():
                        옵션 = f"{row['품목명']}"
                        if pd.notna(row['규격']):
                            옵션 += f" ({row['규격']})"
                        품목_옵션.append((옵션, row['품목코드']))
                    
                    # 선택 상태 저장
                    if 'selected_product' not in st.session_state:
                        st.session_state.selected_product = None
                    
                    선택된_인덱스 = 0
                    if st.session_state.selected_product:
                        try:
                            선택된_인덱스 = [x[1] for x in 품목_옵션].index(st.session_state.selected_product)
                        except:
                            선택된_인덱스 = 0
                    
                    선택품목 = st.radio(
                        "",
                        range(len(품목_옵션)),
                        format_func=lambda x: 품목_옵션[x][0],
                        index=선택된_인덱스,
                        label_visibility="collapsed"
                    )
                    
                    if 선택품목 is not None:
                        st.session_state.selected_product = 품목_옵션[선택품목][1]
                else:
                    st.warning("해당 카테고리에 품목이 없습니다.")
                    st.session_state.selected_product = None
            
            # ========== 3단: 품목 상세 정보 ==========
            with col_detail:
                if st.session_state.selected_product:
                    품목코드 = st.session_state.selected_product
                    품목정보 = products_df[products_df['품목코드'] == 품목코드].iloc[0]
                    
                    st.markdown("### 📊 품목 상세 정보")
                    
                    # 기본 정보
                    st.markdown("#### 📦 기본 정보")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**품목코드:** `{품목정보['품목코드']}`")
                        st.markdown(f"**품목명:** **{품목정보['품목명']}**")
                    with col2:
                        st.markdown(f"**카테고리:** {품목정보['카테고리']}")
                        st.markdown(f"**규격:** {품목정보['규격']}")
                    
                    st.markdown("---")
                    
                    # 이 품목의 거래 내역 필터링
                    품목명 = 품목정보['품목명']
                    품목_거래 = ledger_df[ledger_df['품목'].str.contains(품목명, na=False)]
                    
                    if len(품목_거래) > 0:
                        # 구매 거래 (외입)
                        구매_거래 = 품목_거래[품목_거래['참조'].str.contains('외입', na=False)]
                        
                        # 판매 거래 (외출)
                        판매_거래 = 품목_거래[품목_거래['참조'].str.contains('외출', na=False)]
                        
                        # 💰 구매 정보
                        st.markdown("#### 💰 구매 정보 (내가 사는 가격)")
                        
                        if len(구매_거래) > 0:
                            평균_구매가 = 구매_거래['단가'].mean()
                            최저_구매가 = 구매_거래['단가'].min()
                            최고_구매가 = 구매_거래['단가'].max()
                            총_구매수량 = 구매_거래['수량'].sum()
                            
                            # 최저가/최고가 거래처
                            최저가_row = 구매_거래[구매_거래['단가'] == 최저_구매가].iloc[0]
                            최고가_row = 구매_거래[구매_거래['단가'] == 최고_구매가].iloc[0]
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("평균 구매가", f"{평균_구매가:,.0f}원")
                            with col2:
                                st.metric("최저가", f"{최저_구매가:,.0f}원")
                            with col3:
                                st.metric("최고가", f"{최고_구매가:,.0f}원")
                            
                            st.markdown(f"""
                            - **최저가 거래처:** {최저가_row['거래처']} ({최저가_row['날짜'].strftime('%m/%d')})
                            - **최고가 거래처:** {최고가_row['거래처']} ({최고가_row['날짜'].strftime('%m/%d')})
                            - **총 구매 횟수:** {len(구매_거래)}건
                            - **총 구매 수량:** {총_구매수량:,.0f}개
                            """)
                        else:
                            st.info("구매 내역이 없습니다.")
                        
                        st.markdown("---")
                        
                        # 🏢 판매 현황
                        st.markdown("#### 🏢 판매 현황 (내가 판 거래처)")
                        
                        if len(판매_거래) > 0:
                            # 당월 판매수량
                            현재월 = datetime.now().month
                            당월_판매 = 판매_거래[판매_거래['날짜'].dt.month == 현재월]
                            당월_판매수량 = 당월_판매['수량'].sum()
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("당월 판매수량", f"{당월_판매수량:,.0f}개", f"{datetime.now().month}월")
                            with col2:
                                st.metric("총 판매수량", f"{판매_거래['수량'].sum():,.0f}개")
                            
                            # 최근 판매 거래처 (최근 5건)
                            st.markdown("**최근 판매 거래처:**")
                            최근_판매 = 판매_거래.sort_values('날짜', ascending=False).head(5)
                            
                            for idx, row in 최근_판매.iterrows():
                                st.markdown(f"- **{row['거래처']}** - {row['수량']:,.0f}개 ({row['날짜'].strftime('%m/%d')})")
                        else:
                            st.info("판매 내역이 없습니다.")
                        
                        st.markdown("---")
                        
                        # 📅 최근 거래 내역
                        st.markdown("#### 📅 최근 거래 내역 (최근 10건)")
                        
                        최근_거래 = 품목_거래.sort_values('날짜', ascending=False).head(10)
                        
                        # 거래 내역을 표로 표시
                        display_df = 최근_거래[['날짜', '거래처', '참조', '수량', '단가']].copy()
                        display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
                        display_df['구분'] = display_df['참조'].apply(lambda x: '구매' if '외입' in x else '판매' if '외출' in x else x)
                        display_df['수량'] = display_df['수량'].apply(lambda x: f"{x:,.0f}개")
                        display_df['단가'] = display_df['단가'].apply(lambda x: f"{x:,.0f}원")
                        display_df = display_df[['날짜', '거래처', '구분', '수량', '단가']]
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        
                    else:
                        st.info("이 품목의 거래 내역이 없습니다.")
                else:
                    st.info("👈 좌측에서 품목을 선택하세요.")
        else:
            st.info("등록된 품목이 없습니다. '품목 추가' 탭에서 품목을 추가하세요.")
    
    # ===== 탭2: 품목 추가 =====
    with tab2:
        st.markdown("### ➕ 새 품목 추가")
        
        col1, col2 = st.columns(2)
        
        with col1:
            새품목코드 = st.text_input("품목코드", placeholder="예: P-001")
            새품목명 = st.text_input("품목명", placeholder="예: TURBO Premium 절단석")
        
        with col2:
            새카테고리 = st.text_input("카테고리", placeholder="예: 절단석")
            새규격 = st.text_input("규격", placeholder="예: 4인치")
        
        if st.button("💾 품목 추가", type="primary", use_container_width=True):
            if not 새품목코드 or not 새품목명:
                st.error("품목코드와 품목명은 필수입니다!")
            elif 새품목코드 in products_df['품목코드'].values:
                st.error(f"품목코드 '{새품목코드}'는 이미 존재합니다!")
            else:
                new_row = pd.DataFrame([{
                    '품목코드': 새품목코드,
                    '품목명': 새품목명,
                    '카테고리': 새카테고리,
                    '규격': 새규격
                }])
                st.session_state.products_df = pd.concat([products_df, new_row], ignore_index=True)
                save_products()
                st.success(f"✅ 품목 '{새품목명}' (코드: {새품목코드})이 추가되었습니다!")
                st.rerun()
    
    # ===== 탭3: 품목 검색 =====
    with tab3:
        st.markdown("### 🔍 품목 검색")
        
        검색어 = st.text_input("검색어 입력", placeholder="품목명, 품목코드, 카테고리로 검색...")
        
        if 검색어:
            검색결과 = products_df[
                products_df['품목코드'].str.contains(검색어, case=False, na=False) |
                products_df['품목명'].str.contains(검색어, case=False, na=False) |
                products_df['카테고리'].str.contains(검색어, case=False, na=False) |
                products_df['규격'].str.contains(검색어, case=False, na=False)
            ]
            
            if len(검색결과) > 0:
                st.success(f"🔍 {len(검색결과)}개 품목을 찾았습니다!")
                st.dataframe(검색결과, use_container_width=True)
            else:
                st.warning("검색 결과가 없습니다.")

# ==================== 거래처 관리 ====================
elif menu == "👥 거래처 관리":
    st.title("👥 거래처 관리")
    
    ledger_df = st.session_state.ledger_df
    base_recv_df = st.session_state.base_receivables_df
    
    # 거래처 목록 추출
    거래처_list = sorted(ledger_df['거래처'].dropna().unique().tolist()) if len(ledger_df) > 0 else []
    
    # ========== 구매 주기 분석 함수 ==========
    def 구매주기_분석(거래처명, ledger_df):
        """거래처의 품목별 구매 주기 분석 (고객이 구매하는 주기)"""
        거래처_df = ledger_df[ledger_df['거래처'] == 거래처명]
        # 내가 판매한 것 = 공급가액 > 0
        판매_df = 거래처_df[거래처_df['공급가액'] > 0]
        # 입금/출금 제외
        판매_df = 판매_df[~판매_df['참조'].str.contains('입금|출금', na=False)]
        
        if len(판매_df) < 2:
            return []
        
        결과 = []
        품목_list = 판매_df['품목'].unique()
        
        for 품목 in 품목_list:
            if pd.isna(품목):
                continue
            품목_df = 판매_df[판매_df['품목'] == 품목].sort_values('날짜')
            
            if len(품목_df) >= 2:
                # 구매일 간격 계산
                날짜들 = 품목_df['날짜'].tolist()
                간격들 = []
                for i in range(1, len(날짜들)):
                    간격 = (날짜들[i] - 날짜들[i-1]).days
                    if 간격 > 0:
                        간격들.append(간격)
                
                if 간격들:
                    평균_주기 = sum(간격들) / len(간격들)
                    마지막_구매일 = 날짜들[-1]
                    다음_예상일 = 마지막_구매일 + timedelta(days=평균_주기)
                    남은_일수 = (다음_예상일 - datetime.now()).days
                    
                    결과.append({
                        '품목': 품목[:30] + '...' if len(품목) > 30 else 품목,
                        '평균주기': int(평균_주기),
                        '마지막구매': 마지막_구매일,
                        '다음예상': 다음_예상일,
                        '남은일수': 남은_일수,
                        '구매횟수': len(품목_df)
                    })
        
        # 남은 일수 기준 정렬 (임박한 것 먼저)
        결과.sort(key=lambda x: x['남은일수'])
        return 결과
    
    def 판매기대치_계산(거래처명, ledger_df):
        """거래처의 판매 기대치 점수 계산"""
        거래처_df = ledger_df[ledger_df['거래처'] == 거래처명]
        # 내가 판매한 것 = 공급가액 > 0
        판매_df = 거래처_df[거래처_df['공급가액'] > 0]
        # 입금/출금 제외
        판매_df = 판매_df[~판매_df['참조'].str.contains('입금|출금', na=False)]
        
        if len(판매_df) == 0:
            return 0, {}
        
        # 최근 3개월 데이터만
        최근3개월 = datetime.now() - timedelta(days=90)
        최근_판매 = 판매_df[판매_df['날짜'] >= 최근3개월]
        
        # 월평균 구매금액
        월평균_금액 = (최근_판매['공급가액'].sum() + 최근_판매['부가세'].sum()) / 3 if len(최근_판매) > 0 else 0
        
        # 구매 빈도 (월평균)
        월평균_횟수 = len(최근_판매) / 3
        
        # 구매 주기 임박 품목 수
        주기_분석 = 구매주기_분석(거래처명, ledger_df)
        임박_품목 = len([x for x in 주기_분석 if x['남은일수'] <= 7])
        
        # 기대치 점수 계산 (0~100)
        점수 = 0
        점수 += min(임박_품목 * 20, 40)  # 임박 품목 (최대 40점)
        점수 += min(월평균_금액 / 100000, 30)  # 금액 (최대 30점)
        점수 += min(월평균_횟수 * 5, 30)  # 빈도 (최대 30점)
        
        상세 = {
            '월평균금액': 월평균_금액,
            '월평균횟수': 월평균_횟수,
            '임박품목수': 임박_품목,
            '주기분석': 주기_분석[:3] if 주기_분석 else []  # 상위 3개만
        }
        
        return min(점수, 100), 상세
    
    # ========== 거래처 분류 함수 ==========
    def 거래처_분류(ledger_df):
        """거래처를 매입/고객으로 분류하고 최근 거래일 기준 정렬
        
        분류 기준 (공급가액 부호):
        - 공급가액 < 0 (마이너스): 매입업체 (내가 구입)
        - 공급가액 > 0 (플러스): 고객업체 (내가 판매)
        """
        매입업체 = {}  # 내가 사는 곳 (공급가액 마이너스)
        고객업체 = {}  # 내가 파는 곳 (공급가액 플러스)
        
        for _, row in ledger_df.iterrows():
            거래처 = row['거래처']
            날짜 = row['날짜']
            참조 = row['참조'] if pd.notna(row['참조']) else ''
            공급가액 = row['공급가액'] if pd.notna(row['공급가액']) else 0
            
            # 입금/출금은 제외 (거래처 분류에서)
            if '입금' in 참조 or '출금' in 참조:
                continue
            
            # 공급가액 부호로 분류
            if 공급가액 < 0:  # 마이너스 = 매입 (내가 구입)
                if 거래처 not in 매입업체 or 날짜 > 매입업체[거래처]:
                    매입업체[거래처] = 날짜
            elif 공급가액 > 0:  # 플러스 = 판매 (내가 판매)
                if 거래처 not in 고객업체 or 날짜 > 고객업체[거래처]:
                    고객업체[거래처] = 날짜
        
        # 3개월 기준으로 활성/휴면 분류
        기준일 = datetime.now() - timedelta(days=90)
        
        매입_활성 = [(k, v) for k, v in 매입업체.items() if v >= 기준일]
        매입_휴면 = [(k, v) for k, v in 매입업체.items() if v < 기준일]
        고객_활성 = [(k, v) for k, v in 고객업체.items() if v >= 기준일]
        고객_휴면 = [(k, v) for k, v in 고객업체.items() if v < 기준일]
        
        # 최근 거래일 기준 정렬 (최신순)
        매입_활성.sort(key=lambda x: x[1], reverse=True)
        매입_휴면.sort(key=lambda x: x[1], reverse=True)
        고객_활성.sort(key=lambda x: x[1], reverse=True)
        고객_휴면.sort(key=lambda x: x[1], reverse=True)
        
        return {
            '매입_활성': 매입_활성,
            '매입_휴면': 매입_휴면,
            '고객_활성': 고객_활성,
            '고객_휴면': 고객_휴면
        }
    
    # 거래처 분류 실행
    분류된_거래처 = 거래처_분류(ledger_df) if len(ledger_df) > 0 else {'매입_활성': [], '매입_휴면': [], '고객_활성': [], '고객_휴면': []}
    
    # ========== 탭 구성 (4개 탭) ==========
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 오늘의 영업", "📤 고객업체", "📥 매입업체", "➕ 거래처 추가"])
    
    # ===== 탭1: 오늘의 영업 대시보드 =====
    with tab1:
        st.markdown("### 🎯 오늘의 영업 대시보드")
        st.markdown(f"**{datetime.now().strftime('%Y년 %m월 %d일 %A')}** 기준")
        
        # 고객업체만 대상으로 (내 고객!)
        고객_list = [x[0] for x in 분류된_거래처['고객_활성']]
        
        if len(고객_list) > 0:
            # 모든 거래처의 판매 기대치 계산
            거래처_기대치 = []
            for 거래처 in 고객_list:
                점수, 상세 = 판매기대치_계산(거래처, ledger_df)
                if 점수 > 0:
                    거래처_기대치.append({
                        '거래처': 거래처,
                        '점수': 점수,
                        '상세': 상세
                    })
            
            # 점수순 정렬
            거래처_기대치.sort(key=lambda x: x['점수'], reverse=True)
            
            st.markdown("---")
            st.markdown("### 📞 오늘 연락 추천 거래처 TOP 5")
            
            if 거래처_기대치:
                for i, item in enumerate(거래처_기대치[:5]):
                    거래처명 = item['거래처']
                    점수 = item['점수']
                    상세 = item['상세']
                    
                    # 색상 결정
                    if 점수 >= 70:
                        색상 = "#ffebee"  # 빨강 (긴급)
                        테두리 = "#f44336"
                        아이콘 = "🔴"
                    elif 점수 >= 50:
                        색상 = "#fff3e0"  # 주황 (임박)
                        테두리 = "#ff9800"
                        아이콘 = "🟠"
                    elif 점수 >= 30:
                        색상 = "#fffde7"  # 노랑 (예정)
                        테두리 = "#ffeb3b"
                        아이콘 = "🟡"
                    else:
                        색상 = "#e8f5e9"  # 초록 (여유)
                        테두리 = "#4caf50"
                        아이콘 = "🟢"
                    
                    # 미수금 계산
                    기초미수금_dict = base_recv_df.set_index('거래처')['기초미수금'].to_dict() if len(base_recv_df) > 0 else {}
                    기초미수금 = 기초미수금_dict.get(거래처명, 0)
                    거래처_df = ledger_df[ledger_df['거래처'] == 거래처명]
                    외상_df = 거래처_df[거래처_df['참조'].str.contains('외입|외출', na=False)]
                    입금_df = 거래처_df[거래처_df['참조'].str.contains('입금', na=False)]
                    총외상 = 외상_df['공급가액'].sum() + 외상_df['부가세'].sum()
                    총입금 = 입금_df['공급가액'].sum()
                    미수금 = 기초미수금 + 총외상 + 총입금
                    
                    # 임박 품목 정보
                    임박_품목_텍스트 = ""
                    if 상세['주기분석']:
                        임박 = 상세['주기분석'][0]
                        if 임박['남은일수'] <= 0:
                            임박_품목_텍스트 = f"📦 **{임박['품목']}** 구매 예상일 지남!"
                        elif 임박['남은일수'] <= 3:
                            임박_품목_텍스트 = f"📦 **{임박['품목']}** {임박['남은일수']}일 후 구매 예상"
                        elif 임박['남은일수'] <= 7:
                            임박_품목_텍스트 = f"📦 **{임박['품목']}** 이번 주 구매 예상"
                    
                    st.markdown(f"""
                    <div style='background-color: {색상}; border: 2px solid {테두리}; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                        <h3 style='color: #333; margin: 0;'>{아이콘} {i+1}. {거래처명}</h3>
                        <p style='color: #666; margin: 5px 0;'>
                            💰 미수금: <b>{미수금:,.0f}원</b> | 
                            📊 월평균: <b>{상세['월평균금액']:,.0f}원</b> | 
                            🎯 기대점수: <b>{점수:.0f}점</b>
                        </p>
                        <p style='color: #333; margin: 5px 0;'>{임박_품목_텍스트}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("분석할 거래 데이터가 충분하지 않습니다.")
            
            # 구매 주기 임박 품목 전체
            st.markdown("---")
            st.markdown("### ⏰ 구매 주기 임박 품목 (전체)")
            
            모든_임박 = []
            for 거래처 in 거래처_list:
                주기_분석 = 구매주기_분석(거래처, ledger_df)
                for 품목 in 주기_분석:
                    if 품목['남은일수'] <= 14:  # 2주 이내
                        모든_임박.append({
                            '거래처': 거래처,
                            **품목
                        })
            
            모든_임박.sort(key=lambda x: x['남은일수'])
            
            if 모든_임박:
                임박_df = pd.DataFrame(모든_임박[:20])  # 상위 20개
                임박_df['다음예상'] = pd.to_datetime(임박_df['다음예상']).dt.strftime('%m/%d')
                임박_df['마지막구매'] = pd.to_datetime(임박_df['마지막구매']).dt.strftime('%m/%d')
                임박_df['상태'] = 임박_df['남은일수'].apply(
                    lambda x: '🔴 지남' if x <= 0 else '🟠 임박' if x <= 3 else '🟡 이번주' if x <= 7 else '🟢 여유'
                )
                
                display_df = 임박_df[['상태', '거래처', '품목', '평균주기', '마지막구매', '다음예상', '남은일수']]
                display_df.columns = ['상태', '거래처', '품목', '주기(일)', '마지막', '예상일', 'D-day']
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("2주 이내 구매 예상 품목이 없습니다.")
        else:
            st.info("거래처 데이터가 없습니다. 거래를 입력하면 자동으로 분석됩니다.")
    
    # ===== 탭2: 고객업체 (내가 판매하는 곳) =====
    with tab2:
        st.markdown("### 📤 고객업체")
        st.markdown("*내가 물건을 판매하는 업체*")
        
        # 고객업체 = 공급가액이 플러스인 거래
        고객_활성 = 분류된_거래처['고객_활성']
        고객_휴면 = 분류된_거래처['고객_휴면']
        
        # 전체 고객 목록 (활성 + 휴면)
        전체_고객 = []
        for x in 고객_활성:
            전체_고객.append((x[0], x[1], "🟢"))
        for x in 고객_휴면:
            전체_고객.append((x[0], x[1], "⚪"))
        
        if len(전체_고객) > 0:
            # 고객 선택 드롭다운
            고객_옵션 = [f"{x[2]} {x[0]} ({x[1].strftime('%m/%d')})" for x in 전체_고객]
            선택_idx = st.selectbox(
                f"고객 선택 (🟢활성 {len(고객_활성)}개 / ⚪휴면 {len(고객_휴면)}개)",
                range(len(고객_옵션)),
                format_func=lambda i: 고객_옵션[i],
                key="고객업체_선택"
            )
            
            선택_고객 = 전체_고객[선택_idx][0]
            
            st.markdown("---")
            st.markdown(f"## 🏢 {선택_고객}")
            
            # 이 고객에게 판매한 거래 데이터 (공급가액 > 0)
            고객_df = ledger_df[(ledger_df['거래처'] == 선택_고객) & (ledger_df['공급가액'] > 0) & (~ledger_df['참조'].str.contains('입금|출금', na=False))]
            
            # ===== 미수금 현황 =====
            st.markdown("### 💰 미수금 현황")
            
            기초미수금_dict = base_recv_df.set_index('거래처')['기초미수금'].to_dict() if len(base_recv_df) > 0 else {}
            기초미수금 = 기초미수금_dict.get(선택_고객, 0)
            
            # 전체 거래 (미수금 계산용)
            전체_거래처_df = ledger_df[ledger_df['거래처'] == 선택_고객]
            외상_df = 전체_거래처_df[전체_거래처_df['참조'].str.contains('외입|외출', na=False)]
            입금_df = 전체_거래처_df[전체_거래처_df['참조'].str.contains('입금', na=False)]
            
            총외상 = 외상_df['공급가액'].sum() + 외상_df['부가세'].sum()
            총입금 = 입금_df['공급가액'].sum()
            미수금 = 기초미수금 + 총외상 + 총입금
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("총 판매 횟수", f"{len(고객_df)}건")
            with col_b:
                총_판매금액 = 고객_df['공급가액'].sum() + 고객_df['부가세'].sum()
                st.metric("총 판매금액", f"{총_판매금액:,.0f}원")
            with col_c:
                delta_color = "inverse" if 미수금 > 0 else "normal"
                st.metric("현재 미수금", f"{미수금:,.0f}원", delta="미수" if 미수금 > 0 else "완납", delta_color=delta_color)
            
            st.markdown("---")
            
            # ===== 최근 60일 판매 내역 =====
            st.markdown("### 📦 최근 60일 판매 내역")
            
            if len(고객_df) > 0:
                # 60일 이내 거래만
                기준일_60 = datetime.now() - timedelta(days=60)
                최근60일_df = 고객_df[고객_df['날짜'] >= 기준일_60].sort_values('날짜', ascending=False)
                
                if len(최근60일_df) > 0:
                    st.success(f"🔍 최근 60일 내 {len(최근60일_df)}건 판매")
                    
                    # 테이블로 표시
                    for _, row in 최근60일_df.iterrows():
                        품목명 = row['품목'] if pd.notna(row['품목']) else ''
                        수량 = abs(row['수량']) if pd.notna(row['수량']) else 0
                        단가 = row['단가'] if pd.notna(row['단가']) else 0
                        공급가액 = row['공급가액'] if pd.notna(row['공급가액']) else 0
                        날짜 = row['날짜'].strftime('%m/%d')
                        
                        st.markdown(f"**{날짜}** | {품목명} | {수량:,.0f}개 × {단가:,.0f}원 = **{공급가액:,.0f}원**")
                else:
                    st.info("최근 60일 내 판매 내역이 없습니다.")
            else:
                st.info("판매 내역이 없습니다.")
            
            st.markdown("---")
            
            # ===== 구매 패턴 분석 =====
            st.markdown("### 📊 구매 패턴 분석")
            
            주기_분석 = 구매주기_분석(선택_고객, ledger_df)
            
            if 주기_분석:
                for item in 주기_분석[:5]:
                    남은일 = item['남은일수']
                    if 남은일 <= 0:
                        상태 = "🔴 구매일 지남!"
                    elif 남은일 <= 7:
                        상태 = f"🟠 {남은일}일 후"
                    elif 남은일 <= 14:
                        상태 = f"🟡 {남은일}일 후"
                    else:
                        상태 = f"🟢 {남은일}일 후"
                    
                    st.markdown(f"**{item['품목']}** - 주기: {item['평균주기']}일 | 마지막: {item['마지막구매'].strftime('%m/%d')} | {상태}")
            else:
                st.info("구매 패턴을 분석하려면 동일 품목 2회 이상 거래가 필요합니다.")
        else:
            st.info("고객업체 데이터가 없습니다.")
    
    # ===== 탭3: 매입업체 (내가 물건 사오는 곳) =====
    with tab3:
        st.markdown("### 📥 매입업체")
        st.markdown("*내가 물건을 구입하는 업체*")
        
        매입_활성 = 분류된_거래처['매입_활성']
        매입_휴면 = 분류된_거래처['매입_휴면']
        
        # 전체 매입업체 목록 (활성 + 휴면)
        전체_매입 = []
        for x in 매입_활성:
            전체_매입.append((x[0], x[1], "🟢"))
        for x in 매입_휴면:
            전체_매입.append((x[0], x[1], "⚪"))
        
        if len(전체_매입) > 0:
            # 매입업체 선택 드롭다운
            매입_옵션 = [f"{x[2]} {x[0]} ({x[1].strftime('%m/%d')})" for x in 전체_매입]
            선택_idx = st.selectbox(
                f"매입업체 선택 (🟢활성 {len(매입_활성)}개 / ⚪휴면 {len(매입_휴면)}개)",
                range(len(매입_옵션)),
                format_func=lambda i: 매입_옵션[i],
                key="매입업체_선택"
            )
            
            선택_매입업체 = 전체_매입[선택_idx][0]
            
            st.markdown("---")
            st.markdown(f"## 🏭 {선택_매입업체}")
            
            # 이 업체에서 매입한 거래 데이터 (공급가액 < 0)
            매입_df = ledger_df[(ledger_df['거래처'] == 선택_매입업체) & (ledger_df['공급가액'] < 0)]
            
            # ===== 매입 현황 =====
            st.markdown("### 💰 매입 현황")
            
            if len(매입_df) > 0:
                # 당월 매입
                현재월 = datetime.now().month
                당월_df = 매입_df[매입_df['날짜'].dt.month == 현재월]
                당월_금액 = abs(당월_df['공급가액'].sum() + 당월_df['부가세'].sum())
                
                # 총 매입 (절대값)
                총_금액 = abs(매입_df['공급가액'].sum() + 매입_df['부가세'].sum())
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("총 매입 횟수", f"{len(매입_df)}건")
                with col_b:
                    st.metric("당월 매입", f"{len(당월_df)}건 / {당월_금액:,.0f}원")
                with col_c:
                    st.metric("총 매입금액", f"{총_금액:,.0f}원")
                
                st.markdown("---")
                
                # ===== 최근 60일 매입 내역 =====
                st.markdown("### 📦 최근 60일 매입 내역")
                
                기준일_60 = datetime.now() - timedelta(days=60)
                최근60일_df = 매입_df[매입_df['날짜'] >= 기준일_60].sort_values('날짜', ascending=False)
                
                if len(최근60일_df) > 0:
                    st.success(f"🔍 최근 60일 내 {len(최근60일_df)}건 매입")
                    
                    for _, row in 최근60일_df.iterrows():
                        품목명 = row['품목'] if pd.notna(row['품목']) else ''
                        수량 = abs(row['수량']) if pd.notna(row['수량']) else 0
                        단가 = row['단가'] if pd.notna(row['단가']) else 0
                        공급가액 = abs(row['공급가액']) if pd.notna(row['공급가액']) else 0
                        날짜 = row['날짜'].strftime('%m/%d')
                        
                        st.markdown(f"**{날짜}** | {품목명} | {수량:,.0f}개 × {단가:,.0f}원 = **{공급가액:,.0f}원**")
                else:
                    st.info("최근 60일 내 매입 내역이 없습니다.")
                
                st.markdown("---")
                
                # ===== 주요 매입 품목 =====
                st.markdown("### 📊 주요 매입 품목")
                
                품목별_매입 = 매입_df.groupby('품목').agg({
                    '수량': 'sum',
                    '공급가액': 'sum',
                    '단가': 'mean'
                }).reset_index()
                품목별_매입['공급가액'] = 품목별_매입['공급가액'].abs()
                품목별_매입 = 품목별_매입.sort_values('공급가액', ascending=False).head(10)
                
                for _, row in 품목별_매입.iterrows():
                    품목명 = str(row['품목'])[:40] + '...' if len(str(row['품목'])) > 40 else row['품목']
                    st.markdown(f"**{품목명}** - {abs(row['수량']):,.0f}개 / 평균 {row['단가']:,.0f}원")
            else:
                st.info("매입 내역이 없습니다.")
        else:
            st.info("매입업체 데이터가 없습니다.")
    
    # ===== 탭4: 거래처 추가 (미래 기능) =====
    with tab4:
        st.markdown("### ➕ 거래처 정보 관리")
        st.info("🚧 거래처 상세 정보 입력 기능은 다음 버전에서 추가됩니다!")
        
        st.markdown("""
        **추가 예정 기능:**
        - 사업자등록번호
        - 대표자명, 업태, 종목
        - 주소, 연락처
        - 담당자 정보
        - 배송지 정보
        """)

# ==================== 설정 ====================
elif menu == "⚙️ 설정":
    st.title("⚙️ 설정")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["🗄️ 데이터 관리", "💰 기초 미수금 설정", "📊 통계"])
    
    # ===== 탭1: 데이터 관리 =====
    with tab1:
        st.markdown("### 🗄️ 데이터 관리")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 백업")
            if st.button("💾 백업 파일 다운로드"):
                df = st.session_state.ledger_df
                excel_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=excel_data,
                    file_name=f"장부백업_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.markdown("#### 데이터 초기화")
            if st.button("🗑️ 모든 데이터 삭제", type="secondary"):
                if st.checkbox("정말 삭제하시겠습니까?"):
                    st.session_state.ledger_df = pd.DataFrame(columns=['날짜', '거래처', '품목', '수량', '단가', '공급가액', '부가세', '참조'])
                    save_data()
                    st.success("데이터가 초기화되었습니다.")
                    st.rerun()
    
    # ===== 탭2: 기초 미수금 설정 =====
    with tab2:
        st.markdown("### 💰 기초 미수금 설정 (2024.12.31 기준)")
        
        st.info("""
        **💡 사용 방법:**
        1. 거래처를 선택하거나 직접 입력
        2. 2024년 12월 31일 기준 미수금 입력
        3. 저장 버튼 클릭
        
        ⚠️ **주의:** 컴장부에서 교차 검증 후 정확한 금액을 입력하세요!
        """)
        
        st.markdown("---")
        
        # 기존 거래처 목록
        df = st.session_state.ledger_df
        거래처_list = sorted(df['거래처'].dropna().unique().tolist()) if len(df) > 0 else []
        
        # 입력 폼
        col1, col2 = st.columns([2, 1])
        
        with col1:
            거래처_입력방식 = st.radio("거래처 선택 방식", ["기존 거래처", "직접 입력"], horizontal=True)
            
            if 거래처_입력방식 == "기존 거래처":
                if len(거래처_list) > 0:
                    선택거래처 = st.selectbox("거래처 선택", [""] + 거래처_list)
                else:
                    st.warning("거래처 내역이 없습니다. 직접 입력을 사용하세요.")
                    선택거래처 = ""
            else:
                선택거래처 = st.text_input("거래처명 입력")
        
        with col2:
            기초미수금 = st.number_input("기초 미수금 (원)", min_value=0, value=0, step=10000)
        
        if st.button("💾 저장하기", type="primary", use_container_width=True):
            if not 선택거래처:
                st.error("거래처를 선택하거나 입력해주세요.")
            else:
                # 기존 데이터에서 해당 거래처 제거
                base_rec = st.session_state.base_receivables_df
                base_rec = base_rec[base_rec['거래처'] != 선택거래처]
                
                # 새 데이터 추가
                new_row = pd.DataFrame([{
                    '거래처': 선택거래처,
                    '기초미수금': 기초미수금,
                    '기준일자': '2024-12-31'
                }])
                
                st.session_state.base_receivables_df = pd.concat([base_rec, new_row], ignore_index=True)
                save_base_receivables()
                
                st.success(f"✅ {선택거래처}의 기초 미수금 {기초미수금:,}원이 저장되었습니다!")
                st.rerun()
        
        st.markdown("---")
        
        # 현재 설정된 기초 미수금 목록
        st.markdown("### 📋 현재 설정된 기초 미수금")
        
        base_rec = st.session_state.base_receivables_df
        
        if len(base_rec) > 0:
            display_base = base_rec.copy()
            display_base['기초미수금'] = display_base['기초미수금'].apply(lambda x: f"{x:,.0f}원")
            
            st.dataframe(display_base, use_container_width=True)
            
            # 삭제 기능
            st.markdown("#### 🗑️ 기초 미수금 삭제")
            삭제할거래처 = st.selectbox("삭제할 거래처", [""] + base_rec['거래처'].tolist(), key="delete_select")
            
            if 삭제할거래처 and st.button("🗑️ 삭제하기", type="secondary"):
                st.session_state.base_receivables_df = base_rec[base_rec['거래처'] != 삭제할거래처]
                save_base_receivables()
                st.success(f"✅ {삭제할거래처}의 기초 미수금이 삭제되었습니다.")
                st.rerun()
        else:
            st.info("아직 설정된 기초 미수금이 없습니다.")
    
    # ===== 탭3: 통계 =====
    with tab3:
        st.markdown("### 📊 통계")
        
        df = st.session_state.ledger_df
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 거래 건수", f"{len(df)}건")
        with col2:
            st.metric("거래처 수", f"{df['거래처'].nunique()}개")
        with col3:
            st.metric("데이터 기간", f"{(df['날짜'].max() - df['날짜'].min()).days}일" if len(df) > 0 else "0일")
        
        st.markdown("---")
        
        base_rec = st.session_state.base_receivables_df
        col1, col2 = st.columns(2)
        with col1:
            st.metric("기초 미수금 설정 거래처", f"{len(base_rec)}개")
        with col2:
            총기초미수금 = base_rec['기초미수금'].sum() if len(base_rec) > 0 else 0
            st.metric("총 기초 미수금", f"{총기초미수금:,.0f}원")

# 푸터
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 정보")
st.sidebar.info(f"""
**프로그램:** 누리엠알오 장부관리  
**버전:** 1.0.0  
**데이터:** {len(st.session_state.ledger_df)}건  
**최종 수정:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
""")

st.sidebar.markdown("---")
if st.sidebar.button("🔒 로그아웃", use_container_width=True):
    logout()