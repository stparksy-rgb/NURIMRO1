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
    
    col1, col2 = st.columns(2)
    
    with col1:
        거래일자 = st.date_input("거래 날짜", value=datetime.now())
        
        # 거래처 입력
        거래처_입력방식 = st.radio("거래처 입력 방식", ["기존 거래처 선택", "새 거래처 입력"], horizontal=True)
        
        if 거래처_입력방식 == "기존 거래처 선택":
            거래처 = st.selectbox("거래처 선택", [""] + 거래처_list)
            
            # 거래처 선택 시 미수금 표시
            if 거래처 and 거래처 != "":
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
            거래처 = st.text_input("거래처명")
        
        # 품목 입력 (자동완성 추가!)
        st.markdown("#### 품목 입력")
        품목입력방식 = st.radio("품목 입력 방식", ["품목 검색", "직접 입력"], horizontal=True)
        
        if 품목입력방식 == "품목 검색":
            if len(products_df) > 0:
                # 검색 필터 (개선된 자동완성!)
                검색어 = st.text_input("품목 검색", placeholder="품목명 또는 코드 입력 (예: 절단석, P-001)")
                
                # 검색어에 따라 필터링
                if 검색어 and len(검색어) >= 1:
                    검색결과 = products_df[
                        products_df['품목코드'].str.contains(검색어, case=False, na=False) |
                        products_df['품목명'].str.contains(검색어, case=False, na=False) |
                        products_df['카테고리'].str.contains(검색어, case=False, na=False)
                    ]
                else:
                    # 검색어 없으면 전체 표시
                    검색결과 = products_df
                
                if len(검색결과) > 0:
                    if 검색어:
                        st.success(f"🔍 {len(검색결과)}개 품목 발견!")
                    else:
                        st.info(f"📦 전체 {len(검색결과)}개 품목")
                    
                    # 검색 결과를 바로 리스트로 표시
                    품목_옵션 = []
                    for _, row in 검색결과.iterrows():
                        옵션 = f"[{row['품목코드']}] {row['품목명']}"
                        if pd.notna(row['카테고리']):
                            옵션 += f" - {row['카테고리']}"
                        if pd.notna(row['규격']):
                            옵션 += f" {row['규격']}"
                        품목_옵션.append(옵션)
                    
                    선택품목 = st.selectbox("✨ 품목 선택", ["선택하세요"] + 품목_옵션, key="search_result")
                    
                    if 선택품목 and 선택품목 != "선택하세요":
                        # 선택된 품목 정보 추출
                        품목코드 = 선택품목.split(']')[0].replace('[', '')
                        품목정보 = products_df[products_df['품목코드'] == 품목코드].iloc[0]
                        품목 = f"{품목정보['품목명']} @ {품목정보['규격']}"
                        st.success(f"✅ 선택: {품목}")
                    else:
                        품목 = ""
                else:
                    st.warning("❌ 검색 결과가 없습니다.")
                    품목 = ""
            else:
                st.warning("등록된 품목이 없습니다. '직접 입력'을 사용하세요.")
                품목 = st.text_area("품목 [적요]", height=80)
        else:
            품목 = st.text_area("품목 [적요]", height=80)
        
    with col2:
        거래유형 = st.selectbox("거래 유형", ["=입금", "=출금", "=외입", "=외출", "=견적"])
        
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
        
        st.info(f"**공급가액:** {공급가액:,.0f}원\n\n**부가세:** {부가세:,.0f}원\n\n**합계:** {공급가액+부가세:,.0f}원")
    
    st.markdown("---")
    
    if st.button("💾 저장하기", type="primary", use_container_width=True):
        if not 거래처:
            st.error("거래처를 입력해주세요.")
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
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📋 품목 목록", "➕ 품목 추가", "🔍 품목 검색"])
    
    # ===== 탭1: 품목 목록 =====
    with tab1:
        st.markdown("### 📋 전체 품목 목록")
        
        if len(products_df) > 0:
            # 카테고리 필터
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                카테고리_list = ["전체"] + sorted(products_df['카테고리'].unique().tolist())
                선택카테고리 = st.selectbox("카테고리 필터", 카테고리_list)
            
            # 필터링
            if 선택카테고리 != "전체":
                filtered_df = products_df[products_df['카테고리'] == 선택카테고리]
            else:
                filtered_df = products_df
            
            st.markdown(f"**총 {len(filtered_df)}개 품목**")
            
            # 데이터프레임 표시
            st.dataframe(filtered_df, use_container_width=True, height=600)
            
            # 통계
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 품목 수", f"{len(products_df)}개")
            with col2:
                st.metric("카테고리 수", f"{products_df['카테고리'].nunique()}개")
            with col3:
                st.metric("현재 표시", f"{len(filtered_df)}개")
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
    
    st.info("🚧 **거래처 관리 기능은 곧 추가될 예정입니다!**")
    
    st.markdown("""
    ### 📋 구현 예정 기능:
    
    - ✅ 거래처 정보 관리 (사업자번호, 주소, 연락처)
    - ✅ 거래처별 거래 내역
    - ✅ 거래처별 미수금 현황
    - ✅ 거래처 검색 (이름, 사업자번호, 주소)
    - ✅ 담당자 정보 관리
    - ✅ 배송지 정보 관리
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
