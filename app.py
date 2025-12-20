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
INVENTORY_FILE = "data/inventory.csv"

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

# 재고 데이터 초기화
if 'inventory_df' not in st.session_state:
    if os.path.exists(INVENTORY_FILE):
        st.session_state.inventory_df = pd.read_csv(INVENTORY_FILE)
    else:
        st.session_state.inventory_df = pd.DataFrame(columns=['품목명', '기초재고', '현재재고', '기준일자', '안전재고', '단위'])

# 데이터 저장 함수
def save_data():
    st.session_state.ledger_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

def save_base_receivables():
    st.session_state.base_receivables_df.to_csv(BASE_RECEIVABLE_FILE, index=False, encoding='utf-8-sig')

def save_products():
    st.session_state.products_df.to_csv(PRODUCTS_FILE, index=False, encoding='utf-8-sig')

def save_inventory():
    st.session_state.inventory_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')

def create_invoice_pdf(거래처, 날짜, 거래_목록, 회사정보=None):
    """거래명세서 PDF 생성"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import mm
    import io
    
    # 한글 폰트 등록
    try:
        pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
        font_name = 'NanumGothic'
    except:
        font_name = 'Helvetica'
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # 제목
    c.setFont(font_name, 20)
    c.drawCentredString(width/2, height - 40*mm, "거 래 명 세 서")
    
    # 거래처 정보
    c.setFont(font_name, 12)
    c.drawString(30*mm, height - 60*mm, f"거래처: {거래처}")
    c.drawString(30*mm, height - 68*mm, f"거래일: {날짜}")
    
    # 공급자 정보 (우측)
    c.drawString(120*mm, height - 60*mm, "공급자: 누리엠알오")
    c.drawString(120*mm, height - 68*mm, "사업자번호: 301-03-55081")
    
    # 테이블 헤더
    y = height - 85*mm
    c.setFont(font_name, 10)
    
    # 헤더 배경
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.rect(20*mm, y - 2*mm, 170*mm, 8*mm, fill=True, stroke=True)
    
    c.setFillColorRGB(0, 0, 0)
    c.drawString(22*mm, y, "No")
    c.drawString(35*mm, y, "품 목")
    c.drawString(100*mm, y, "수량")
    c.drawString(120*mm, y, "단가")
    c.drawString(150*mm, y, "금액")
    
    # 테이블 내용
    y -= 10*mm
    총공급가액 = 0
    총부가세 = 0
    
    for i, 거래 in enumerate(거래_목록, 1):
        c.drawString(22*mm, y, str(i))
        
        # 품목명이 길면 자르기
        품목명 = str(거래.get('품목', ''))[:25]
        c.drawString(35*mm, y, 품목명)
        
        수량 = 거래.get('수량', 0)
        단가 = 거래.get('단가', 0)
        금액 = 거래.get('공급가액', 0)
        부가세 = 거래.get('부가세', 0)
        
        c.drawRightString(115*mm, y, f"{수량:,.0f}")
        c.drawRightString(140*mm, y, f"{단가:,.0f}")
        c.drawRightString(185*mm, y, f"{금액:,.0f}")
        
        총공급가액 += 금액
        총부가세 += 부가세
        
        y -= 7*mm
        
        # 페이지 넘김 체크
        if y < 50*mm:
            c.showPage()
            c.setFont(font_name, 10)
            y = height - 30*mm
    
    # 합계선
    y -= 5*mm
    c.line(20*mm, y + 3*mm, 190*mm, y + 3*mm)
    
    # 합계
    c.setFont(font_name, 11)
    c.drawString(100*mm, y - 5*mm, f"공급가액: {총공급가액:,.0f}원")
    c.drawString(100*mm, y - 13*mm, f"부가세: {총부가세:,.0f}원")
    
    c.setFont(font_name, 14)
    c.drawString(100*mm, y - 25*mm, f"합 계: {총공급가액 + 총부가세:,.0f}원")
    
    # 하단 서명란
    c.setFont(font_name, 10)
    c.drawString(30*mm, 30*mm, "위와 같이 거래합니다.")
    c.drawString(140*mm, 30*mm, "공급자 (인)")
    
    c.save()
    buffer.seek(0)
    return buffer

# ==================== 로그인 체크 ====================
if not check_login():
    login_page()
    st.stop()

# ==================== 메인 애플리케이션 ====================
# 사이드바 - 메뉴
st.sidebar.title("📋 장부 관리 시스템")
st.sidebar.markdown("---")

# 첫 화면을 거래처 관리로 설정
if 'first_load' not in st.session_state:
    st.session_state.first_load = True
    st.session_state.default_menu = "👥 거래처 관리"

menu_list = ["🏠 대시보드", "➕ 거래 입력", "📄 거래 내역", "📊 통계 분석", "💰 외상 관리", "🧾 회계 관리", "📦 품목 관리", "📋 재고 관리", "👥 거래처 관리", "⚙️ 설정"]
default_index = menu_list.index("👥 거래처 관리") if st.session_state.get('first_load', False) else 0

menu = st.sidebar.radio(
    "메뉴 선택",
    menu_list,
    index=default_index
)

# 첫 로드 후 플래그 해제
if st.session_state.get('first_load', False):
    st.session_state.first_load = False

# ==================== 대시보드 ====================
if menu == "🏠 대시보드":
    st.title("📊 대시보드")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("아직 거래 내역이 없습니다. '거래 입력' 메뉴에서 데이터를 추가해주세요.")
    else:
        # 최근 4개년도만 표시
        당해연도 = datetime.now().year
        연도_목록 = [당해연도, 당해연도-1, 당해연도-2, 당해연도-3]
        연도_라벨 = [f"{당해연도}년 (당해)", f"{당해연도-1}년", f"{당해연도-2}년", f"{당해연도-3}년"]
        
        # 연도 선택 + 월 선택
        col1, col2 = st.columns(2)
        with col1:
            선택_연도_idx = st.selectbox("연도 선택", range(len(연도_라벨)), format_func=lambda i: 연도_라벨[i])
            선택_연도 = 연도_목록[선택_연도_idx]
        with col2:
            월_옵션 = ["전체"] + [f"{m}월" for m in range(1, 13)]
            선택_월 = st.selectbox("월 선택", 월_옵션, index=datetime.now().month if 선택_연도 == 당해연도 else 0)
        
        # 날짜 필터링
        df['연도'] = df['날짜'].dt.year
        df_filtered = df[df['연도'] == 선택_연도].copy()
        
        if 선택_월 != "전체":
            월_숫자 = int(선택_월.replace("월", ""))
            df_filtered = df_filtered[df_filtered['날짜'].dt.month == 월_숫자]
        
        # 주요 지표
        st.markdown(f"### 📈 {선택_연도}년 {선택_월} 주요 지표")
        
        # 수입/지출 계산
        입금_df = df_filtered[df_filtered['참조'].str.contains('입금', na=False)]
        출금_df = df_filtered[df_filtered['참조'].str.contains('출금', na=False)]
        외입_df = df_filtered[df_filtered['참조'].str.contains('외입', na=False)]
        외출_df = df_filtered[df_filtered['참조'].str.contains('외출', na=False)]
        
        총수입 = 입금_df['공급가액'].sum()
        총지출 = abs(출금_df['공급가액'].sum())
        # 외입은 음수이므로 절대값으로 매입금액 계산
        총매입 = abs(외입_df['공급가액'].sum())
        총매입부가세 = abs(외입_df['부가세'].sum())
        # 외출(판매) 금액
        총매출 = 외출_df['공급가액'].sum() + 외출_df['부가세'].sum()
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
            st.metric("🧾 총 매출", f"{총매출:,.0f}원")
        
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
        월별_매입 = df_filtered[df_filtered['참조'].str.contains('외입', na=False)].groupby('년월')['공급가액'].sum().abs()
        
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
                
                # 미수금 표시 (base_receivables 기준)
                기초미수금_dict = st.session_state.base_receivables_df.set_index('거래처')['기초미수금'].to_dict()
                미수금 = 기초미수금_dict.get(거래처, 0)
                
                if 미수금 > 0:
                    st.markdown(f"""
                    <div style='background-color: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; padding: 10px; margin: 5px 0;'>
                        <h4 style='color: #e65100; margin: 0;'>⚠️ 미수금: {미수금:,.0f}원</h4>
                    </div>
                    """, unsafe_allow_html=True)
                elif 미수금 < 0:
                    st.markdown(f"""
                    <div style='background-color: #e3f2fd; border: 2px solid #1e88e5; border-radius: 8px; padding: 10px; margin: 5px 0;'>
                        <h4 style='color: #1565c0; margin: 0;'>💰 선수금: {abs(미수금):,.0f}원</h4>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success("✅ 미수금 없음")
                
                # ✅ 해당 거래처 최근 거래 품목 7개 표시
                거래처_품목_df = df[(df['거래처'] == 거래처) & (~df['참조'].str.contains('입금|출금', na=False))]
                if len(거래처_품목_df) > 0:
                    최근품목 = 거래처_품목_df.sort_values('날짜', ascending=False)['품목'].dropna().unique()[:7]
                    if len(최근품목) > 0:
                        st.markdown("#### 📦 최근 거래 품목")
                        st.session_state['거래처_최근품목'] = list(최근품목)
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
                            <h4 style='color: #333; margin: 0;'>✅ 선택된 품목</h4>
                            <h3 style='color: #000; margin: 5px 0;'>{품목}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 📊 이전 납품가 표시 (거래처가 선택된 경우)
                        if 거래처:
                            # 해당 거래처 + 해당 품목 이전 거래 검색
                            이전거래 = df[
                                (df['거래처'] == 거래처) & 
                                (df['품목'].str.contains(품목정보['품목명'], na=False)) &
                                (df['참조'] == '=외출')  # 판매만
                            ].sort_values('날짜', ascending=False)
                            
                            if len(이전거래) > 0:
                                st.markdown(f"""
                                <div style='background-color: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; padding: 12px; margin: 10px 0;'>
                                    <h4 style='color: #000; margin: 0;'>📊 {거래처} 이전 납품 이력</h4>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # 최근 5건 표시
                                for _, row in 이전거래.head(5).iterrows():
                                    날짜_str = row['날짜'].strftime('%Y-%m-%d') if pd.notna(row['날짜']) else ''
                                    st.markdown(f"""
                                    <div style='background-color: #f5f5f5; border-radius: 5px; padding: 8px; margin: 5px 0;'>
                                        <span style='color: #000;'>{날짜_str}</span> | 
                                        <b style='color: #000;'>수량: {row['수량']:,.0f}</b> | 
                                        <b style='color: #1976d2;'>단가: {row['단가']:,.0f}원</b> | 
                                        <span style='color: #000;'>합계: {row['공급가액']:,.0f}원</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(f"💡 {거래처}에 이 품목 첫 납품입니다!")
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
        
        거래유형 = st.selectbox("거래 유형", ["=외출 (판매)", "=입금 (수금)", "=외입 (매입)", "=출금 (결제)", "=견적"])
        거래유형_값 = 거래유형.split(" ")[0]  # 실제 저장할 값
        
        # ✅ 선택된 거래 유형 명확히 표시!
        if 거래유형:
            유형_색상 = {
                "=외출 (판매)": ("#e3f2fd", "#1e88e5", "#1565c0", "#0d47a1"),
                "=입금 (수금)": ("#e8f5e9", "#43a047", "#2e7d32", "#1b5e20"),
                "=외입 (매입)": ("#fff3e0", "#fb8c00", "#f57c00", "#e65100"),
                "=출금 (결제)": ("#ffebee", "#e53935", "#c62828", "#b71c1c"),
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
        단가 = st.number_input("단가", min_value=0, value=0, step=100, format="%d")
        
        # 공급가액 자동 계산
        if 거래유형_값 == "=출금":
            공급가액 = -(수량 * 단가 if 수량 > 0 and 단가 > 0 else st.number_input("공급가액", value=0, step=1000, format="%d"))
        else:
            공급가액 = 수량 * 단가 if 수량 > 0 and 단가 > 0 else st.number_input("공급가액", value=0, step=1000, format="%d")
        
        # 부가세 자동 계산 (외출/외입인 경우)
        if 거래유형_값 in ["=외출", "=외입"]:
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
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        저장_버튼 = st.button("💾 저장하기", type="primary", use_container_width=True)
    with col2:
        저장_출력_버튼 = st.button("💾 저장 + 📄 명세서", use_container_width=True)
    
    if 저장_버튼 or 저장_출력_버튼:
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
                '참조': 거래유형_값
            }])
            
            st.session_state.ledger_df = pd.concat([st.session_state.ledger_df, new_row], ignore_index=True)
            save_data()
            st.success("✅ 거래 내역이 저장되었습니다!")
            
            # 저장 + 출력 버튼 클릭 시 PDF 생성
            if 저장_출력_버튼:
                거래_목록 = [{
                    '품목': 품목,
                    '수량': 수량,
                    '단가': 단가,
                    '공급가액': 공급가액,
                    '부가세': 부가세
                }]
                
                pdf_buffer = create_invoice_pdf(거래처, 거래일자.strftime('%Y-%m-%d'), 거래_목록)
                
                st.download_button(
                    label="📄 거래명세서 다운로드 (PDF)",
                    data=pdf_buffer,
                    file_name=f"거래명세서_{거래처}_{거래일자.strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.balloons()
                st.rerun()

# ==================== 거래 내역 ====================
elif menu == "📄 거래 내역":
    st.title("📄 거래 내역")
    
    df = st.session_state.ledger_df.copy()
    products_df = st.session_state.products_df
    
    # ===== 빠른 입력 (컴장부 스타일) =====
    with st.expander("➕ 빠른 거래 입력", expanded=False):
        st.markdown("##### 컴장부처럼 빠르게 입력하세요!")
        
        # 기존 거래처 목록
        거래처_list = sorted(df['거래처'].dropna().unique().tolist()) if len(df) > 0 else []
        
        # 기존 품목 목록 (ledger에서 추출)
        품목_list = sorted(df['품목'].dropna().unique().tolist()) if len(df) > 0 else []
        
        # 1줄: 날짜, 거래처, 거래유형
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            입력_날짜 = st.date_input("날짜", value=datetime.now(), key="quick_date")
        with col2:
            입력_거래처 = st.selectbox("거래처", [""] + 거래처_list, key="quick_customer")
        with col3:
            # 거래 유형 (외출이 기본 - 판매가 더 많음)
            입력_거래유형 = st.selectbox(
                "유형", 
                ["=외출 (판매)", "=입금 (수금)", "=외입 (매입)", "=출금 (결제)"], 
                key="quick_type"
            )
            # 실제 저장할 값 추출
            입력_거래유형_값 = 입력_거래유형.split(" ")[0]
        
        # 2줄: 품목(자동완성), 수량, 단가, 공급가액(자동계산)
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            # 품목 자동완성 - selectbox + 검색 기능
            품목_검색어 = st.text_input("품목 검색 (2글자 이상)", key="quick_product_search", placeholder="품목명 입력...")
            
            # 2글자 이상 입력시 필터링된 품목 표시
            if len(품목_검색어) >= 2:
                필터_품목 = [p for p in 품목_list if 품목_검색어.lower() in p.lower()]
                if 필터_품목:
                    입력_품목 = st.selectbox(
                        f"🔍 검색결과 ({len(필터_품목)}건)", 
                        ["직접입력: " + 품목_검색어] + 필터_품목[:20],  # 최대 20개
                        key="quick_product_select"
                    )
                    # "직접입력:" 선택시 검색어 그대로 사용
                    if 입력_품목.startswith("직접입력:"):
                        입력_품목 = 품목_검색어
                else:
                    입력_품목 = 품목_검색어
                    st.caption("검색 결과 없음 - 직접 입력됩니다")
            else:
                입력_품목 = 품목_검색어
                if 품목_검색어:
                    st.caption("2글자 이상 입력하면 품목 검색")
        
        with col2:
            입력_수량 = st.number_input("수량", min_value=0, value=0, step=1, format="%d", key="quick_qty")
        with col3:
            입력_단가 = st.number_input("단가", min_value=0, value=0, step=100, format="%d", key="quick_price")
        with col4:
            # 공급가액 자동 계산 (수정 불가)
            자동_공급가액 = 입력_수량 * 입력_단가
            st.text_input("공급가액", value=f"{자동_공급가액:,}", disabled=True, key="quick_amount_display")
            입력_공급가액 = 자동_공급가액
        
        # 부가세 및 저장
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            부가세_적용 = st.checkbox("부가세 10%", value=True if 입력_거래유형_값 in ["=외출", "=외입"] else False, key="quick_tax")
            입력_부가세 = round(입력_공급가액 * 0.1) if 부가세_적용 else 0
        with col2:
            st.metric("합계", f"{입력_공급가액 + 입력_부가세:,.0f}원")
        with col3:
            if st.button("💾 저장", type="primary", use_container_width=True, key="quick_save"):
                if not 입력_거래처:
                    st.error("❌ 거래처를 선택해주세요.")
                else:
                    new_row = pd.DataFrame([{
                        '날짜': pd.to_datetime(입력_날짜),
                        '거래처': 입력_거래처,
                        '품목': 입력_품목 if 입력_품목 else 입력_거래유형_값.replace("=", ""),
                        '수량': 입력_수량,
                        '단가': 입력_단가,
                        '공급가액': 입력_공급가액,
                        '부가세': 입력_부가세,
                        '참조': 입력_거래유형_값
                    }])
                    
                    st.session_state.ledger_df = pd.concat([st.session_state.ledger_df, new_row], ignore_index=True)
                    save_data()
                    st.success(f"✅ 저장 완료! {입력_거래처} - {입력_공급가액 + 입력_부가세:,.0f}원")
                    st.rerun()
    
    st.markdown("---")
    
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
        
        # 미수금 실시간 표시 - base_receivables에서 직접 가져옴
        if "전체" not in 거래처_필터 and len(거래처_필터) == 1:
            선택거래처 = 거래처_필터[0]
            
            # 미수금은 base_receivables에서 직접 가져옴 (컴장부 GULREST)
            기초미수금_dict = st.session_state.base_receivables_df.set_index('거래처')['기초미수금'].to_dict()
            미수금 = 기초미수금_dict.get(선택거래처, 0)
            
            # 미수금 표시
            if 미수금 > 0:
                st.markdown(f"""
                <div style='background-color: #fee; border: 2px solid #f88; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #c00; margin: 0;'>⚠️ 미수금: {미수금:,.0f}원</h3>
                </div>
                """, unsafe_allow_html=True)
            elif 미수금 < 0:
                st.markdown(f"""
                <div style='background-color: #e3f2fd; border: 2px solid #1e88e5; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #1565c0; margin: 0;'>💰 선수금: {abs(미수금):,.0f}원</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #efe; border: 2px solid #8c8; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #080; margin: 0;'>✅ 미수금 없음</h3>
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
        
        # 거래명세서 출력 (거래처 1개 선택 시)
        st.markdown("---")
        
        if "전체" not in 거래처_필터 and len(거래처_필터) == 1:
            선택거래처_명세 = 거래처_필터[0]
            
            st.markdown("#### 📄 거래명세서 출력")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                명세서_시작일 = st.date_input("시작일", value=datetime.now().replace(day=1), key="invoice_start")
            with col2:
                명세서_종료일 = st.date_input("종료일", value=datetime.now(), key="invoice_end")
            with col3:
                명세서_출력 = st.button("📄 거래명세서 생성", type="primary", use_container_width=True)
            
            if 명세서_출력:
                # 해당 기간 + 거래처 + 판매(외출)만 필터
                명세_df = df_filtered[
                    (df_filtered['참조'] == '=외출')
                ].copy()
                
                # 날짜 필터 (원본 df_filtered 사용)
                원본_df = st.session_state.ledger_df.copy()
                원본_df = 원본_df[
                    (원본_df['거래처'] == 선택거래처_명세) &
                    (원본_df['참조'] == '=외출') &
                    (원본_df['날짜'] >= pd.to_datetime(명세서_시작일)) &
                    (원본_df['날짜'] <= pd.to_datetime(명세서_종료일))
                ]
                
                if len(원본_df) > 0:
                    거래_목록 = []
                    for _, row in 원본_df.iterrows():
                        거래_목록.append({
                            '품목': row['품목'],
                            '수량': row['수량'],
                            '단가': row['단가'],
                            '공급가액': row['공급가액'],
                            '부가세': row['부가세']
                        })
                    
                    날짜_문자열 = f"{명세서_시작일.strftime('%Y-%m-%d')} ~ {명세서_종료일.strftime('%Y-%m-%d')}"
                    pdf_buffer = create_invoice_pdf(선택거래처_명세, 날짜_문자열, 거래_목록)
                    
                    st.download_button(
                        label="📥 거래명세서 다운로드 (PDF)",
                        data=pdf_buffer,
                        file_name=f"거래명세서_{선택거래처_명세}_{명세서_시작일.strftime('%Y%m%d')}_{명세서_종료일.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success(f"✅ {선택거래처_명세} 거래명세서 생성 완료! ({len(원본_df)}건)")
                else:
                    st.warning("해당 기간에 판매 거래가 없습니다.")
        
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
        # 최근 4개년도 필터
        당해연도 = datetime.now().year
        연도_목록 = [당해연도, 당해연도-1, 당해연도-2, 당해연도-3]
        
        col1, col2 = st.columns(2)
        with col1:
            분석유형 = st.selectbox("분석 유형", ["월별 분석", "거래처별 분석", "품목별 분석", "부가세 분석"])
        with col2:
            선택_연도 = st.selectbox("연도 선택", ["전체 (최근4년)"] + [f"{y}년" for y in 연도_목록])
        
        # 연도 필터링
        df['연도'] = df['날짜'].dt.year
        if 선택_연도 == "전체 (최근4년)":
            df = df[df['연도'].isin(연도_목록)]
        else:
            선택_연도_숫자 = int(선택_연도.replace("년", ""))
            df = df[df['연도'] == 선택_연도_숫자]
        
        if 분석유형 == "월별 분석":
            st.markdown("### 📆 월별 수입/지출 분석")
            
            df['년월'] = df['날짜'].dt.to_period('M').astype(str)
            
            입금_df = df[df['참조'].str.contains('입금', na=False)].groupby('년월')['공급가액'].sum()
            출금_df = df[df['참조'].str.contains('출금', na=False)].groupby('년월')['공급가액'].sum().abs()
            # 외입은 음수이므로 절대값
            매입_df = df[df['참조'].str.contains('외입', na=False)].groupby('년월')['공급가액'].sum().abs()
            부가세_df = df[df['참조'].str.contains('외입', na=False)].groupby('년월')['부가세'].sum().abs()
            # 외출(판매)
            매출_df = df[df['참조'].str.contains('외출', na=False)].groupby('년월').apply(
                lambda x: x['공급가액'].sum() + x['부가세'].sum()
            )
            
            월별_df = pd.DataFrame({
                '수입': 입금_df,
                '지출': 출금_df,
                '매입': 매입_df,
                '매출': 매출_df,
                '순이익': 입금_df - 출금_df
            }).fillna(0)
            
            # 최신순 정렬 (역순)
            월별_df = 월별_df.sort_index(ascending=False)
            
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
            
            # 외입(매입)은 음수이므로 절대값
            매입부가세 = df[df['참조'].str.contains('외입', na=False)].groupby('년월')['부가세'].sum().abs()
            # 외출(매출) 부가세
            매출부가세 = df[df['참조'].str.contains('외출', na=False)].groupby('년월')['부가세'].sum()
            
            부가세_df = pd.DataFrame({
                '매입부가세': 매입부가세,
                '매출부가세': 매출부가세,
                '납부세액': 매출부가세 - 매입부가세
            }).fillna(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 월별 부가세")
                fig = go.Figure()
                fig.add_trace(go.Bar(name='매출부가세', x=부가세_df.index, y=부가세_df['매출부가세'], marker_color='#2E7D32'))
                fig.add_trace(go.Bar(name='매입부가세', x=부가세_df.index, y=부가세_df['매입부가세'], marker_color='#C62828'))
                fig.update_layout(barmode='group', height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 통계")
                st.metric("총 매출부가세", f"{부가세_df['매출부가세'].sum():,.0f}원")
                st.metric("총 매입부가세", f"{부가세_df['매입부가세'].sum():,.0f}원")
                st.metric("납부세액 (매출-매입)", f"{부가세_df['납부세액'].sum():,.0f}원")

# ==================== 외상 관리 ====================
elif menu == "💰 외상 관리":
    st.title("💰 외상 관리")
    
    df = st.session_state.ledger_df.copy()
    base_rec = st.session_state.base_receivables_df.copy()
    
    if len(df) == 0:
        st.info("아직 거래 내역이 없습니다.")
    else:
        # 외상 매출 (미수금)
        st.markdown("### 📤 외상 매출 (미수금)")
        st.caption("💡 최근 1년 거래 기준 | 미수금 = 컴장부 GULREST 값")
        
        # 최근 1년 기준
        기준일_1년 = datetime.now() - timedelta(days=365)
        최근1년_df = df[df['날짜'] >= 기준일_1년]
        
        # 미수금은 base_receivables에서 가져옴 (컴장부 GULREST)
        기초미수금_dict = {}
        if len(base_rec) > 0:
            for _, row in base_rec.iterrows():
                기초미수금_dict[row['거래처']] = row['기초미수금']
        
        # 최근 1년 거래가 있는 거래처만
        최근_거래처 = 최근1년_df['거래처'].dropna().unique()
        
        # 거래처별 집계 (최근 1년)
        미수금_목록 = []
        
        for 거래처 in 최근_거래처:
            거래처_df = 최근1년_df[최근1년_df['거래처'] == 거래처]
            
            # 판매 거래 (입금/출금 제외, 공급가액 > 0)
            판매_df = 거래처_df[(거래처_df['공급가액'] > 0) & (~거래처_df['참조'].str.contains('입금|출금', na=False))]
            
            # 입금 거래
            입금_df = 거래처_df[거래처_df['참조'].str.contains('입금', na=False)]
            
            공급가액 = 판매_df['공급가액'].sum()
            부가세 = 판매_df['부가세'].sum()
            합계 = 공급가액 + 부가세
            입금액 = abs(입금_df['공급가액'].sum())
            
            # 미수금은 base_receivables에서 가져옴
            미수금 = 기초미수금_dict.get(거래처, 0)
            
            # 미수금이 양수인 경우만 (받을 돈)
            if 미수금 > 0:
                최근거래일 = 거래처_df['날짜'].max()
                
                미수금_목록.append({
                    '거래처': 거래처,
                    '공급가액': 공급가액,
                    '부가세': 부가세,
                    '합계': 합계,
                    '입금액': 입금액,
                    '미수금': 미수금,
                    '최근거래일': 최근거래일
                })
        
        if 미수금_목록:
            미수금_df = pd.DataFrame(미수금_목록)
            미수금_df = 미수금_df.sort_values('미수금', ascending=False)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 미수금", f"{미수금_df['미수금'].sum():,.0f}원")
            with col2:
                st.metric("미수 거래처 수", f"{len(미수금_df)}개")
            with col3:
                st.metric("최대 미수금", f"{미수금_df['미수금'].max():,.0f}원")
            
            st.markdown("---")
            
            # 상세 내역 표시
            display_df = 미수금_df.copy()
            display_df['최근거래일'] = display_df['최근거래일'].dt.strftime('%Y-%m-%d')
            
            # 컬럼 순서 정리: 거래처, 공급가액, 부가세, 합계, 입금액, 미수금
            display_df = display_df[['거래처', '공급가액', '부가세', '합계', '입금액', '미수금', '최근거래일']]
            
            # 금액 포맷팅
            for col in ['공급가액', '부가세', '합계', '입금액', '미수금']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # 다운로드 버튼
            csv = 미수금_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 미수금 목록 다운로드 (CSV)",
                data=csv,
                file_name="receivables_list.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ 미수금이 없습니다!")

# ==================== 회계 관리 ====================
elif menu == "🧾 회계 관리":
    st.title("🧾 회계 관리")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("아직 거래 내역이 없습니다.")
    else:
        # 최근 4개년도 필터
        당해연도 = datetime.now().year
        연도_목록 = [당해연도, 당해연도-1, 당해연도-2, 당해연도-3]
        
        # 탭 생성 (유영찬 매출 탭 추가)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 손익 현황", "🧾 부가세 현황", "💹 마진 분석", "🏢 거래처별 마진", "👤 유영찬 매출"])
        
        # ===== 탭1: 손익 현황 =====
        with tab1:
            st.markdown("### 📊 연도별 손익 현황")
            
            df['연도'] = df['날짜'].dt.year
            df_4년 = df[df['연도'].isin(연도_목록)]
            
            손익_데이터 = []
            for 연도 in sorted(연도_목록, reverse=True):
                연도_df = df_4년[df_4년['연도'] == 연도]
                
                # 수입 (입금)
                수입 = 연도_df[연도_df['참조'] == '=입금']['공급가액'].sum()
                
                # 지출 (출금) - 음수이므로 절대값
                지출 = abs(연도_df[연도_df['참조'] == '=출금']['공급가액'].sum())
                
                # 매출 (외출)
                외출_df = 연도_df[연도_df['참조'] == '=외출']
                매출 = 외출_df['공급가액'].sum()
                매출부가세 = 외출_df['부가세'].sum()
                
                # 매입 (외입) - 음수이므로 절대값
                외입_df = 연도_df[연도_df['참조'] == '=외입']
                매입 = abs(외입_df['공급가액'].sum())
                매입부가세 = abs(외입_df['부가세'].sum())
                
                # 마진 (매입단가가 있는 경우)
                마진 = 외출_df['마진'].sum() if '마진' in 외출_df.columns else 0
                
                손익_데이터.append({
                    '연도': f"{연도}년",
                    '매출': 매출,
                    '매입': 매입,
                    '마진': 마진,
                    '마진율': (마진 / 매출 * 100) if 매출 > 0 else 0,
                    '수입(입금)': 수입,
                    '지출(출금)': 지출,
                    '순이익': 수입 - 지출
                })
            
            손익_df = pd.DataFrame(손익_데이터)
            
            # 요약 지표
            col1, col2, col3, col4 = st.columns(4)
            당해_데이터 = 손익_df[손익_df['연도'] == f"{당해연도}년"].iloc[0] if len(손익_df[손익_df['연도'] == f"{당해연도}년"]) > 0 else None
            
            if 당해_데이터 is not None:
                with col1:
                    st.metric(f"{당해연도}년 매출", f"{당해_데이터['매출']:,.0f}원")
                with col2:
                    st.metric(f"{당해연도}년 마진", f"{당해_데이터['마진']:,.0f}원", delta=f"{당해_데이터['마진율']:.1f}%")
                with col3:
                    st.metric(f"{당해연도}년 수입", f"{당해_데이터['수입(입금)']:,.0f}원")
                with col4:
                    st.metric(f"{당해연도}년 순이익", f"{당해_데이터['순이익']:,.0f}원")
            
            st.markdown("---")
            
            # 연도별 비교 차트
            fig = go.Figure()
            fig.add_trace(go.Bar(name='매출', x=손익_df['연도'], y=손익_df['매출'], marker_color='#1976D2'))
            fig.add_trace(go.Bar(name='마진', x=손익_df['연도'], y=손익_df['마진'], marker_color='#43A047'))
            fig.add_trace(go.Bar(name='순이익', x=손익_df['연도'], y=손익_df['순이익'], marker_color='#FF9800'))
            fig.update_layout(barmode='group', height=400, title='연도별 손익 비교')
            st.plotly_chart(fig, use_container_width=True)
            
            # 상세 테이블
            display_손익 = 손익_df.copy()
            for col in ['매출', '매입', '마진', '수입(입금)', '지출(출금)', '순이익']:
                display_손익[col] = display_손익[col].apply(lambda x: f"{x:,.0f}")
            display_손익['마진율'] = display_손익['마진율'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_손익, use_container_width=True, hide_index=True)
        
        # ===== 탭2: 부가세 현황 =====
        with tab2:
            st.markdown("### 🧾 월별 부가세 장부")
            
            선택_연도_부가세 = st.selectbox("연도 선택", 연도_목록, format_func=lambda x: f"{x}년", key="vat_year")
            
            df['연도'] = df['날짜'].dt.year
            df['월'] = df['날짜'].dt.month
            연도_df = df[df['연도'] == 선택_연도_부가세]
            
            # 월별 부가세 계산
            월별_데이터 = []
            
            # 분기/반기 누적용
            q1_data = {'총매출액': 0, '계산서매출': 0, '매출부가세': 0, '현금매출': 0, '매입액': 0, '매입부가세': 0, '납부세액': 0}
            q2_data = {'총매출액': 0, '계산서매출': 0, '매출부가세': 0, '현금매출': 0, '매입액': 0, '매입부가세': 0, '납부세액': 0}
            q3_data = {'총매출액': 0, '계산서매출': 0, '매출부가세': 0, '현금매출': 0, '매입액': 0, '매입부가세': 0, '납부세액': 0}
            q4_data = {'총매출액': 0, '계산서매출': 0, '매출부가세': 0, '현금매출': 0, '매입액': 0, '매입부가세': 0, '납부세액': 0}
            
            for 월 in range(1, 13):
                월_df = 연도_df[연도_df['월'] == 월]
                
                # 매출
                외출_df = 월_df[월_df['참조'] == '=외출']
                총매출액 = 외출_df['공급가액'].sum() + 외출_df['부가세'].sum()
                계산서매출 = 외출_df[외출_df['부가세'] > 0]['공급가액'].sum()
                매출부가세 = 외출_df['부가세'].sum()
                현금매출 = 외출_df[외출_df['부가세'] == 0]['공급가액'].sum()
                
                # 매입
                외입_df = 월_df[월_df['참조'] == '=외입']
                매입액 = abs(외입_df['공급가액'].sum())
                매입부가세 = abs(외입_df['부가세'].sum())
                
                # 납부세액
                납부세액 = 매출부가세 - 매입부가세
                
                row_data = {
                    '구분': f"{월}월",
                    '총매출액': 총매출액,
                    '계산서매출': 계산서매출,
                    '매출부가세': 매출부가세,
                    '현금매출': 현금매출,
                    '매입액': 매입액,
                    '매입부가세': 매입부가세,
                    '납부세액': 납부세액
                }
                월별_데이터.append(row_data)
                
                # 분기별 누적
                if 월 <= 3:
                    for k in q1_data: q1_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                elif 월 <= 6:
                    for k in q2_data: q2_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                elif 월 <= 9:
                    for k in q3_data: q3_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                else:
                    for k in q4_data: q4_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                
                # 3월 후 1분기 합산
                if 월 == 3:
                    월별_데이터.append({'구분': '▶ 1분기 합계', **q1_data})
                
                # 6월 후 2분기 + 상반기 합산
                if 월 == 6:
                    월별_데이터.append({'구분': '▶ 2분기 합계', **q2_data})
                    상반기 = {k: q1_data[k] + q2_data[k] for k in q1_data}
                    월별_데이터.append({'구분': '★ 상반기 합계', **상반기})
                
                # 9월 후 3분기 합산
                if 월 == 9:
                    월별_데이터.append({'구분': '▶ 3분기 합계', **q3_data})
                
                # 12월 후 4분기 + 하반기 + 연간 합산
                if 월 == 12:
                    월별_데이터.append({'구분': '▶ 4분기 합계', **q4_data})
                    하반기 = {k: q3_data[k] + q4_data[k] for k in q3_data}
                    월별_데이터.append({'구분': '★ 하반기 합계', **하반기})
                    연간 = {k: q1_data[k] + q2_data[k] + q3_data[k] + q4_data[k] for k in q1_data}
                    월별_데이터.append({'구분': '◆ 연간 합계', **연간})
            
            월별_df = pd.DataFrame(월별_데이터)
            
            # 연간 요약 (상단)
            연간_매출부가세 = q1_data['매출부가세'] + q2_data['매출부가세'] + q3_data['매출부가세'] + q4_data['매출부가세']
            연간_매입부가세 = q1_data['매입부가세'] + q2_data['매입부가세'] + q3_data['매입부가세'] + q4_data['매입부가세']
            연간_납부세액 = 연간_매출부가세 - 연간_매입부가세
            
            st.markdown(f"#### {선택_연도_부가세}년 연간 요약")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📤 매출부가세", f"{연간_매출부가세:,.0f}원")
            with col2:
                st.metric("📥 매입부가세", f"{연간_매입부가세:,.0f}원")
            with col3:
                if 연간_납부세액 >= 0:
                    st.metric("💸 납부할 부가세", f"{연간_납부세액:,.0f}원")
                else:
                    st.metric("💰 환급받을 부가세", f"{abs(연간_납부세액):,.0f}원")
            
            st.markdown("---")
            
            # 월별 상세 테이블 (st.dataframe 사용)
            st.markdown("#### 월별 상세")
            
            display_df = 월별_df.copy()
            for col in ['총매출액', '계산서매출', '매출부가세', '현금매출', '매입액', '매입부가세', '납부세액']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=700)
            
            # 차트
            st.markdown("---")
            st.markdown("#### 월별 부가세 추이")
            월_only = 월별_df[~월별_df['구분'].str.contains('합계')]
            fig = go.Figure()
            fig.add_trace(go.Bar(name='매출부가세', x=월_only['구분'], y=월_only['매출부가세'], marker_color='#1976D2'))
            fig.add_trace(go.Bar(name='매입부가세', x=월_only['구분'], y=월_only['매입부가세'], marker_color='#FF5722'))
            fig.add_trace(go.Scatter(name='납부세액', x=월_only['구분'], y=월_only['납부세액'], mode='lines+markers', line=dict(color='#43A047', width=3)))
            fig.update_layout(barmode='group', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # ===== 탭3: 마진 분석 =====
        with tab3:
            st.markdown("### 💹 월별 마진 분석")
            
            col1, col2 = st.columns(2)
            with col1:
                선택_연도_마진 = st.selectbox("연도 선택", 연도_목록, format_func=lambda x: f"{x}년", key="margin_year")
            
            df['연도'] = df['날짜'].dt.year
            df['월'] = df['날짜'].dt.month
            연도_df = df[df['연도'] == 선택_연도_마진]
            
            # 월별 마진 계산
            월별_마진 = []
            for 월 in range(1, 13):
                월_df = 연도_df[(연도_df['월'] == 월) & (연도_df['참조'] == '=외출')]
                
                매출 = 월_df['공급가액'].sum()
                마진 = 월_df['마진'].sum() if '마진' in 월_df.columns else 0
                마진율 = (마진 / 매출 * 100) if 매출 > 0 else 0
                
                월별_마진.append({
                    '월': f"{월}월",
                    '매출': 매출,
                    '마진': 마진,
                    '마진율': 마진율
                })
            
            월별_마진_df = pd.DataFrame(월별_마진)
            
            # 차트
            fig = go.Figure()
            fig.add_trace(go.Bar(name='매출', x=월별_마진_df['월'], y=월별_마진_df['매출'], marker_color='#1976D2', yaxis='y'))
            fig.add_trace(go.Bar(name='마진', x=월별_마진_df['월'], y=월별_마진_df['마진'], marker_color='#43A047', yaxis='y'))
            fig.add_trace(go.Scatter(name='마진율', x=월별_마진_df['월'], y=월별_마진_df['마진율'], mode='lines+markers', line=dict(color='#FF5722', width=3), yaxis='y2'))
            
            fig.update_layout(
                barmode='group',
                height=450,
                title=f'{선택_연도_마진}년 월별 매출/마진',
                yaxis=dict(title='금액 (원)'),
                yaxis2=dict(title='마진율 (%)', overlaying='y', side='right', range=[0, 50])
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 테이블
            display_마진 = 월별_마진_df.copy()
            display_마진['매출'] = display_마진['매출'].apply(lambda x: f"{x:,.0f}")
            display_마진['마진'] = display_마진['마진'].apply(lambda x: f"{x:,.0f}")
            display_마진['마진율'] = display_마진['마진율'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_마진, use_container_width=True, hide_index=True)
            
            # 연간 합계
            총매출 = 월별_마진_df['매출'].sum()
            총마진 = 월별_마진_df['마진'].sum()
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("연간 총매출", f"{총매출:,.0f}원")
            with col2:
                st.metric("연간 총마진", f"{총마진:,.0f}원")
            with col3:
                st.metric("연간 평균 마진율", f"{(총마진/총매출*100):.1f}%" if 총매출 > 0 else "0%")
        
        # ===== 탭4: 거래처별 마진 =====
        with tab4:
            st.markdown("### 🏢 거래처별 마진 분석")
            
            col1, col2 = st.columns(2)
            with col1:
                선택_연도_거래처 = st.selectbox("연도 선택", 연도_목록, format_func=lambda x: f"{x}년", key="customer_margin_year")
            
            df['연도'] = df['날짜'].dt.year
            연도_df = df[(df['연도'] == 선택_연도_거래처) & (df['참조'] == '=외출')]
            
            # 거래처별 마진 계산
            거래처별_마진 = 연도_df.groupby('거래처').agg({
                '공급가액': 'sum',
                '마진': 'sum',
                '날짜': 'count'
            }).rename(columns={'날짜': '거래횟수'})
            
            거래처별_마진['마진율'] = (거래처별_마진['마진'] / 거래처별_마진['공급가액'] * 100).round(1)
            거래처별_마진 = 거래처별_마진.sort_values('마진', ascending=False)
            
            # 상위/하위 분석
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 마진 TOP 10")
                top10 = 거래처별_마진.head(10).copy()
                display_top = top10.reset_index()
                display_top['공급가액'] = display_top['공급가액'].apply(lambda x: f"{x:,.0f}")
                display_top['마진'] = display_top['마진'].apply(lambda x: f"{x:,.0f}")
                display_top['마진율'] = display_top['마진율'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_top, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### ⚠️ 마진율 하위 10 (주의 필요)")
                # 마진율 기준 하위 (매출이 있는 거래처만)
                마진율_하위 = 거래처별_마진[거래처별_마진['공급가액'] > 100000].sort_values('마진율').head(10).copy()
                display_bottom = 마진율_하위.reset_index()
                display_bottom['공급가액'] = display_bottom['공급가액'].apply(lambda x: f"{x:,.0f}")
                display_bottom['마진'] = display_bottom['마진'].apply(lambda x: f"{x:,.0f}")
                display_bottom['마진율'] = display_bottom['마진율'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_bottom, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # 마진율 분포 차트
            st.markdown("#### 거래처 마진율 분포")
            fig = px.histogram(거래처별_마진, x='마진율', nbins=20, title='마진율 분포')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            # 전체 거래처 목록
            with st.expander("📋 전체 거래처 마진 보기"):
                display_전체 = 거래처별_마진.reset_index()
                display_전체['공급가액'] = display_전체['공급가액'].apply(lambda x: f"{x:,.0f}")
                display_전체['마진'] = display_전체['마진'].apply(lambda x: f"{x:,.0f}")
                display_전체['마진율'] = display_전체['마진율'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_전체, use_container_width=True, hide_index=True, height=400)
        
        # ===== 탭5: 유영찬 매출 =====
        with tab5:
            st.markdown("### 👤 유영찬 매출 관리")
            
            # 유영찬 거래만 필터
            유영찬_df = df[df['거래처'] == '유영찬'].copy()
            
            if len(유영찬_df) == 0:
                st.info("유영찬 거래 내역이 없습니다.")
            else:
                유영찬_df['연도'] = 유영찬_df['날짜'].dt.year
                유영찬_df['월'] = 유영찬_df['날짜'].dt.month
                
                # 연도 선택
                col1, col2 = st.columns(2)
                with col1:
                    선택_연도_유영찬 = st.selectbox("연도 선택", 연도_목록, format_func=lambda x: f"{x}년", key="yoo_year")
                
                연도_유영찬 = 유영찬_df[유영찬_df['연도'] == 선택_연도_유영찬]
                
                # 거래 유형 분류
                # 1. 제품 출고 (판매) - 입금, 수당, 택배 제외
                제품_df = 연도_유영찬[~연도_유영찬['품목'].str.contains('입금|수당|택배', na=False)]
                제품_df = 제품_df[제품_df['공급가액'] > 0]  # 양수만 (판매)
                
                # 2. 입금 (유영찬이 받아온 돈)
                입금_df = 연도_유영찬[연도_유영찬['품목'].str.contains('입금', na=False)]
                
                # 3. 수당
                수당_df = 연도_유영찬[연도_유영찬['품목'].str.contains('수당', na=False)]
                
                # 요약 지표
                총_제품출고 = 제품_df['공급가액'].sum()
                총_입금 = 입금_df['공급가액'].sum()
                총_수당 = abs(수당_df['공급가액'].sum())
                총_마진 = 제품_df['마진'].sum() if '마진' in 제품_df.columns else 0
                
                st.markdown(f"#### {선택_연도_유영찬}년 유영찬 실적 요약")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📦 제품 출고액", f"{총_제품출고:,.0f}원")
                with col2:
                    st.metric("💰 입금액", f"{총_입금:,.0f}원")
                with col3:
                    st.metric("💵 수당 지급", f"{총_수당:,.0f}원")
                with col4:
                    st.metric("📈 마진", f"{총_마진:,.0f}원")
                
                # 미수금 표시
                기초미수금_dict = st.session_state.base_receivables_df.set_index('거래처')['기초미수금'].to_dict()
                유영찬_미수금 = 기초미수금_dict.get('유영찬', 0)
                
                if 유영찬_미수금 > 0:
                    st.markdown(f"""
                    <div style='background-color: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; padding: 15px; margin: 15px 0;'>
                        <h3 style='color: #e65100; margin: 0;'>⚠️ 유영찬 미수금: {유영찬_미수금:,.0f}원</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # 월별 실적
                st.markdown("#### 📊 월별 실적")
                
                월별_실적 = []
                for 월 in range(1, 13):
                    월_제품 = 제품_df[제품_df['월'] == 월]
                    월_입금 = 입금_df[입금_df['월'] == 월]
                    월_수당 = 수당_df[수당_df['월'] == 월]
                    
                    월별_실적.append({
                        '월': f"{월}월",
                        '제품출고': 월_제품['공급가액'].sum(),
                        '입금': 월_입금['공급가액'].sum(),
                        '수당': abs(월_수당['공급가액'].sum()),
                        '마진': 월_제품['마진'].sum() if '마진' in 월_제품.columns else 0
                    })
                
                월별_df = pd.DataFrame(월별_실적)
                
                # 차트
                fig = go.Figure()
                fig.add_trace(go.Bar(name='제품출고', x=월별_df['월'], y=월별_df['제품출고'], marker_color='#1976D2'))
                fig.add_trace(go.Bar(name='입금', x=월별_df['월'], y=월별_df['입금'], marker_color='#43A047'))
                fig.add_trace(go.Scatter(name='마진', x=월별_df['월'], y=월별_df['마진'], mode='lines+markers', line=dict(color='#FF5722', width=3)))
                fig.update_layout(barmode='group', height=400, title=f'{선택_연도_유영찬}년 월별 실적')
                st.plotly_chart(fig, use_container_width=True)
                
                # 테이블
                display_월별 = 월별_df.copy()
                for col in ['제품출고', '입금', '수당', '마진']:
                    display_월별[col] = display_월별[col].apply(lambda x: f"{x:,.0f}")
                st.dataframe(display_월별, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # 제품별 판매 내역
                st.markdown("#### 📦 제품별 판매 내역")
                
                if len(제품_df) > 0:
                    제품별 = 제품_df.groupby('품목').agg({
                        '수량': 'sum',
                        '공급가액': 'sum',
                        '마진': 'sum'
                    }).reset_index()
                    제품별 = 제품별.sort_values('공급가액', ascending=False)
                    제품별['마진율'] = (제품별['마진'] / 제품별['공급가액'] * 100).round(1)
                    
                    display_제품 = 제품별.copy()
                    display_제품['수량'] = display_제품['수량'].apply(lambda x: f"{x:,.0f}")
                    display_제품['공급가액'] = display_제품['공급가액'].apply(lambda x: f"{x:,.0f}")
                    display_제품['마진'] = display_제품['마진'].apply(lambda x: f"{x:,.0f}")
                    display_제품['마진율'] = display_제품['마진율'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(display_제품, use_container_width=True, hide_index=True, height=400)
                
                st.markdown("---")
                
                # 입금 내역 (어디서 받아온 돈인지)
                st.markdown("#### 💰 입금 내역 (유영찬이 받아온 돈)")
                
                if len(입금_df) > 0:
                    입금_표시 = 입금_df[['날짜', '품목', '공급가액']].copy()
                    입금_표시 = 입금_표시.sort_values('날짜', ascending=False)
                    입금_표시['날짜'] = 입금_표시['날짜'].dt.strftime('%Y-%m-%d')
                    입금_표시['공급가액'] = 입금_표시['공급가액'].apply(lambda x: f"{x:,.0f}")
                    
                    st.dataframe(입금_표시.head(30), use_container_width=True, hide_index=True)

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
                
                # 절단석이 있으면 기본 선택
                기본_인덱스 = 카테고리_list.index("절단석") if "절단석" in 카테고리_list else 0
                
                선택카테고리 = st.radio("", 카테고리_list, index=기본_인덱스, label_visibility="collapsed")
                
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
                    filtered_df = products_df[products_df['카테고리'] == 선택카테고리].copy()
                else:
                    filtered_df = products_df.copy()
                
                # 최근 6개월 거래 횟수 기준 정렬
                from datetime import datetime, timedelta
                기준일_6개월 = datetime.now() - timedelta(days=180)
                
                if len(ledger_df) > 0:
                    최근거래 = ledger_df[ledger_df['날짜'] >= 기준일_6개월]
                    품목별_거래수 = 최근거래.groupby('품목').size().to_dict()
                    
                    filtered_df['최근거래수'] = filtered_df['품목명'].apply(
                        lambda x: sum(cnt for 품목, cnt in 품목별_거래수.items() if str(x) in str(품목))
                    )
                    filtered_df = filtered_df.sort_values('최근거래수', ascending=False)
                
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
                        # 구매 거래 (공급가액 < 0 = 내가 매입)
                        구매_거래 = 품목_거래[품목_거래['공급가액'] < 0]
                        
                        # 판매 거래 (공급가액 > 0 = 내가 판매, 입금/출금 제외)
                        판매_거래 = 품목_거래[(품목_거래['공급가액'] > 0) & (~품목_거래['참조'].str.contains('입금|출금', na=False))]
                        
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

# ==================== 재고 관리 ====================
elif menu == "📋 재고 관리":
    st.title("📋 재고 관리")
    
    inventory_df = st.session_state.inventory_df
    ledger_df = st.session_state.ledger_df
    
    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📊 재고 현황", "➕ 입고/출고", "⚠️ 재고 부족", "⚙️ 재고 설정"])
    
    # ===== 탭1: 재고 현황 =====
    with tab1:
        st.markdown("### 📊 현재 재고 현황")
        st.markdown(f"**기준일:** 2025년 12월 20일")
        
        if len(inventory_df) > 0:
            # 검색 필터
            col1, col2 = st.columns([3, 1])
            with col1:
                검색어 = st.text_input("🔍 품목 검색", placeholder="품목명으로 검색...")
            with col2:
                정렬기준 = st.selectbox("정렬", ["재고 많은 순", "재고 적은 순", "품목명순"])
            
            # 필터링
            display_df = inventory_df.copy()
            if 검색어:
                display_df = display_df[display_df['품목명'].str.contains(검색어, case=False, na=False)]
            
            # 정렬
            if 정렬기준 == "재고 많은 순":
                display_df = display_df.sort_values('현재재고', ascending=False)
            elif 정렬기준 == "재고 적은 순":
                display_df = display_df.sort_values('현재재고', ascending=True)
            else:
                display_df = display_df.sort_values('품목명')
            
            # 통계
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📦 총 품목 수", f"{len(inventory_df)}개")
            with col2:
                st.metric("📊 총 재고 수량", f"{inventory_df['현재재고'].sum():,.0f}개")
            with col3:
                총평가액 = inventory_df['재고평가액'].sum() if '재고평가액' in inventory_df.columns else 0
                st.metric("💰 총 재고평가액", f"{총평가액:,.0f}원")
            with col4:
                재고없음 = len(inventory_df[inventory_df['현재재고'] <= 0])
                st.metric("❌ 재고 없음", f"{재고없음}개")
            
            # 🔥 핵심 제품: 4인치/5인치 절단석 요약
            st.markdown("#### 🔥 핵심 제품 (절단석)")
            
            # 4인치 절단석
            절단석_4인치 = inventory_df[inventory_df['품목명'].str.contains('4.*인치|4"|4인치|@4|@ 4', na=False, regex=True)]
            절단석_4인치 = 절단석_4인치[절단석_4인치['품목명'].str.contains('절단석|절단', na=False)]
            
            # 5인치 절단석
            절단석_5인치 = inventory_df[inventory_df['품목명'].str.contains('5.*인치|5"|5인치|@5|@ 5', na=False, regex=True)]
            절단석_5인치 = 절단석_5인치[절단석_5인치['품목명'].str.contains('절단석|절단', na=False)]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='background-color: #e3f2fd; border: 2px solid #1976d2; border-radius: 10px; padding: 15px; margin: 5px 0;'>
                    <h4 style='color: #1565c0; margin: 0 0 10px 0;'>📦 4인치 절단석</h4>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("품목 수", f"{len(절단석_4인치)}개")
                with c2:
                    st.metric("재고 수량", f"{절단석_4인치['현재재고'].sum():,.0f}개")
                with c3:
                    평가액_4 = 절단석_4인치['재고평가액'].sum() if '재고평가액' in 절단석_4인치.columns else 0
                    st.metric("평가액", f"{평가액_4:,.0f}원")
            
            with col2:
                st.markdown("""
                <div style='background-color: #fff3e0; border: 2px solid #ff9800; border-radius: 10px; padding: 15px; margin: 5px 0;'>
                    <h4 style='color: #e65100; margin: 0 0 10px 0;'>📦 5인치 절단석</h4>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("품목 수", f"{len(절단석_5인치)}개")
                with c2:
                    st.metric("재고 수량", f"{절단석_5인치['현재재고'].sum():,.0f}개")
                with c3:
                    평가액_5 = 절단석_5인치['재고평가액'].sum() if '재고평가액' in 절단석_5인치.columns else 0
                    st.metric("평가액", f"{평가액_5:,.0f}원")
            
            st.markdown("---")
            
            # 재고 목록 표시 (품목명, 재고수량, 매입단가, 재고평가액, 매입업체)
            표시_컬럼 = ['품목명', '현재재고', '매입단가', '재고평가액', '매입업체']
            표시_컬럼 = [col for col in 표시_컬럼 if col in display_df.columns]
            
            # 금액 포맷팅
            display_formatted = display_df[표시_컬럼].copy()
            if '매입단가' in display_formatted.columns:
                display_formatted['매입단가'] = display_formatted['매입단가'].apply(lambda x: f"{x:,.0f}원" if pd.notna(x) else "")
            if '재고평가액' in display_formatted.columns:
                display_formatted['재고평가액'] = display_formatted['재고평가액'].apply(lambda x: f"{x:,.0f}원" if pd.notna(x) else "")
            
            display_formatted = display_formatted.rename(columns={'현재재고': '재고수량'})
            
            st.dataframe(
                display_formatted,
                use_container_width=True,
                height=500
            )
            
            # 다운로드 버튼
            csv = inventory_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 재고 목록 다운로드 (CSV)",
                data=csv,
                file_name="inventory_list.csv",
                mime="text/csv"
            )
        else:
            st.info("등록된 재고가 없습니다. '재고 설정' 탭에서 기초 재고를 등록해주세요.")
    
    # ===== 탭2: 입고/출고 =====
    with tab2:
        st.markdown("### ➕ 수동 입고/출고")
        st.info("💡 일반 거래 입력 시에는 자동으로 재고가 차감됩니다. 이 화면은 수동 조정용입니다.")
        
        if len(inventory_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 품목 선택")
                품목_list = inventory_df['품목명'].tolist()
                선택_품목 = st.selectbox("품목", [""] + 품목_list)
                
                if 선택_품목:
                    현재_재고 = inventory_df[inventory_df['품목명'] == 선택_품목]['현재재고'].values[0]
                    st.info(f"📦 현재 재고: **{현재_재고:,.0f}개**")
            
            with col2:
                st.markdown("#### 수량 입력")
                입출고_유형 = st.radio("유형", ["입고 (+)", "출고 (-)"], horizontal=True)
                수량 = st.number_input("수량", min_value=0, value=0, step=1)
                사유 = st.text_input("사유", placeholder="예: 재고 실사 조정, 파손 등")
            
            if st.button("✅ 적용", type="primary", use_container_width=True):
                if 선택_품목 and 수량 > 0:
                    idx = inventory_df[inventory_df['품목명'] == 선택_품목].index[0]
                    if 입출고_유형 == "입고 (+)":
                        st.session_state.inventory_df.loc[idx, '현재재고'] += 수량
                        st.success(f"✅ {선택_품목} +{수량}개 입고 완료!")
                    else:
                        st.session_state.inventory_df.loc[idx, '현재재고'] -= 수량
                        st.success(f"✅ {선택_품목} -{수량}개 출고 완료!")
                    save_inventory()
                    st.rerun()
                else:
                    st.error("품목과 수량을 입력해주세요.")
        else:
            st.warning("재고 데이터가 없습니다.")
    
    # ===== 탭3: 재고 부족 =====
    with tab3:
        st.markdown("### ⚠️ 재고 부족 알림")
        st.info("💡 최근 10개월 내 거래된 품목만 표시됩니다.")
        
        if len(inventory_df) > 0 and len(ledger_df) > 0:
            # 최근 10개월 거래 품목 필터링
            from datetime import datetime, timedelta
            기준일_10개월 = datetime.now() - timedelta(days=300)
            
            최근거래 = ledger_df[ledger_df['날짜'] >= 기준일_10개월]
            최근거래_품목 = 최근거래['품목'].dropna().unique().tolist()
            
            # 품목별 거래 횟수 계산
            품목별_거래수 = 최근거래.groupby('품목').size().to_dict()
            
            # 재고 부족 기준 설정
            부족_기준 = st.slider("재고 부족 기준 (개)", min_value=0, max_value=1000, value=100, step=10)
            
            # 최근 10개월 거래 품목 중 재고 부족 품목
            부족_df = inventory_df[inventory_df['현재재고'] <= 부족_기준].copy()
            
            # 최근 거래된 품목만 필터링
            부족_df['최근거래'] = 부족_df['품목명'].apply(
                lambda x: any(str(x) in str(품목) for 품목 in 최근거래_품목)
            )
            부족_df = 부족_df[부족_df['최근거래'] == True]
            
            # 거래 횟수 추가 및 정렬
            부족_df['거래횟수'] = 부족_df['품목명'].apply(
                lambda x: sum(cnt for 품목, cnt in 품목별_거래수.items() if str(x) in str(품목))
            )
            부족_df = 부족_df.sort_values('거래횟수', ascending=False)
            
            if len(부족_df) > 0:
                st.error(f"⚠️ 재고 부족 품목: **{len(부족_df)}개** (최근 10개월 거래 품목 중)")
                
                for _, row in 부족_df.iterrows():
                    재고 = row['현재재고']
                    품목 = row['품목명']
                    거래수 = row['거래횟수']
                    
                    if 재고 <= 0:
                        st.markdown(f"❌ **{품목}** - 재고 없음! (거래 {거래수}회)")
                    elif 재고 <= 부족_기준 / 2:
                        st.markdown(f"🔴 **{품목}** - {재고:,.0f}개 (긴급, 거래 {거래수}회)")
                    else:
                        st.markdown(f"🟡 **{품목}** - {재고:,.0f}개 (거래 {거래수}회)")
            else:
                st.success(f"✅ 재고 {부족_기준}개 이하인 품목이 없습니다!")
        else:
            st.info("재고 데이터가 없습니다.")
    
    # ===== 탭4: 재고 설정 =====
    with tab4:
        st.markdown("### ⚙️ 재고 설정")
        
        st.markdown("#### 📥 기초 재고 일괄 등록")
        st.info("CSV 파일을 업로드하여 기초 재고를 등록할 수 있습니다.")
        
        uploaded_file = st.file_uploader("재고 CSV 파일 업로드", type=['csv'])
        
        if uploaded_file:
            try:
                new_inventory = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                st.success(f"✅ {len(new_inventory)}개 품목 로드 완료!")
                st.dataframe(new_inventory.head(10))
                
                if st.button("📥 재고 데이터 적용", type="primary"):
                    # 컬럼명 맞추기
                    if '재고수량' in new_inventory.columns:
                        new_inventory = new_inventory.rename(columns={'재고수량': '현재재고'})
                    if '현재재고' not in new_inventory.columns and '기초재고' in new_inventory.columns:
                        new_inventory['현재재고'] = new_inventory['기초재고']
                    
                    # 필수 컬럼 확인
                    if '품목명' in new_inventory.columns and '현재재고' in new_inventory.columns:
                        new_inventory['기초재고'] = new_inventory['현재재고']
                        new_inventory['기준일자'] = '2025-12-20'
                        if '안전재고' not in new_inventory.columns:
                            new_inventory['안전재고'] = 100
                        if '단위' not in new_inventory.columns:
                            new_inventory['단위'] = '개'
                        
                        st.session_state.inventory_df = new_inventory[['품목명', '기초재고', '현재재고', '기준일자', '안전재고', '단위']]
                        save_inventory()
                        st.success("✅ 재고 데이터가 적용되었습니다!")
                        st.rerun()
                    else:
                        st.error("CSV 파일에 '품목명'과 '현재재고(또는 재고수량)' 컬럼이 필요합니다.")
            except Exception as e:
                st.error(f"파일 읽기 오류: {e}")
        
        st.markdown("---")
        st.markdown("#### 📊 현재 재고 통계")
        if len(inventory_df) > 0:
            st.write(f"- 총 품목 수: {len(inventory_df)}개")
            st.write(f"- 총 재고 수량: {inventory_df['현재재고'].sum():,.0f}개")
            st.write(f"- 기준일자: {inventory_df['기준일자'].iloc[0] if len(inventory_df) > 0 else 'N/A'}")

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
        
        # 구매 주기 임박 품목 수 (3개월 = 90일 내)
        주기_분석 = 구매주기_분석(거래처명, ledger_df)
        임박_품목 = len([x for x in 주기_분석 if x['남은일수'] <= 90])
        
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
        # 최근 6개월 데이터만 사용
        기준일_6개월 = datetime.now() - timedelta(days=180)
        최근_ledger = ledger_df[ledger_df['날짜'] >= 기준일_6개월]
        
        매입업체 = {}  # 내가 사는 곳 (공급가액 마이너스)
        고객업체 = {}  # 내가 파는 곳 (공급가액 플러스)
        
        for _, row in 최근_ledger.iterrows():
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
        
        # 제외할 거래처 (영업직원, 위탁판매 등)
        제외_거래처 = ['유영찬']
        
        # 최근 6개월 데이터
        기준일_6개월 = datetime.now() - timedelta(days=180)
        최근6개월_df = ledger_df[ledger_df['날짜'] >= 기준일_6개월]
        
        # 6개월 내 2회 이상 거래 + 매출 계산
        고객_매출 = []
        for 거래처 in ledger_df['거래처'].dropna().unique():
            if 거래처 in 제외_거래처:
                continue
            
            거래처_df = 최근6개월_df[최근6개월_df['거래처'] == 거래처]
            # 판매 거래만 (공급가액 > 0, 입금/출금 제외)
            판매_df = 거래처_df[(거래처_df['공급가액'] > 0) & (~거래처_df['참조'].str.contains('입금|출금', na=False))]
            
            거래횟수 = len(판매_df)
            if 거래횟수 >= 2:  # 2회 이상 거래
                총매출 = 판매_df['공급가액'].sum() + 판매_df['부가세'].sum()
                고객_매출.append({
                    '거래처': 거래처,
                    '거래횟수': 거래횟수,
                    '총매출': 총매출
                })
        
        # 매출 높은 순 정렬
        고객_매출.sort(key=lambda x: x['총매출'], reverse=True)
        
        if len(고객_매출) > 0:
            st.markdown("---")
            st.markdown("### 📞 오늘 연락 추천 TOP 5")
            st.caption("💡 최근 6개월 내 2회 이상 거래, 매출 높은 순")
            
            for i, item in enumerate(고객_매출[:5]):
                거래처명 = item['거래처']
                총매출 = item['총매출']
                거래횟수 = item['거래횟수']
                
                # 미수금은 base_receivables에서 직접 가져옴 (컴장부 GULREST)
                기초미수금_dict = base_recv_df.set_index('거래처')['기초미수금'].to_dict() if len(base_recv_df) > 0 else {}
                미수금 = 기초미수금_dict.get(거래처명, 0)
                
                # 구매 주기 임박 품목 (최근 6개월 거래 품목 중)
                주기_분석 = 구매주기_분석(거래처명, ledger_df)
                # 최근 6개월 내 거래된 품목만 필터링
                최근_품목 = 최근6개월_df[최근6개월_df['거래처'] == 거래처명]['품목'].dropna().unique()
                주기_분석 = [x for x in 주기_분석 if any(str(x['품목']) in str(p) for p in 최근_품목)]
                
                임박_품목_텍스트 = ""
                if 주기_분석:
                    임박 = 주기_분석[0]
                    if 임박['남은일수'] <= 0:
                        임박_품목_텍스트 = f"📦 {임박['품목']} - 구매 예상일 지남!"
                    elif 임박['남은일수'] <= 14:
                        임박_품목_텍스트 = f"📦 {임박['품목']} - {임박['남은일수']}일 후 예상"
                
                # 순위별 아이콘
                순위_아이콘 = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                
                # 깔끔한 카드 스타일
                with st.container():
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        st.markdown(f"**{순위_아이콘} {거래처명}**")
                    with col2:
                        st.markdown(f"💰 6개월 매출: **{총매출:,.0f}원** | 거래 {거래횟수}회 | 미수금: {미수금:,.0f}원")
                    
                    if 임박_품목_텍스트:
                        st.caption(임박_품목_텍스트)
                    st.markdown("---")
            
            # 구매 주기 임박 품목 - TOP 5 다음 업체 (6~15위)
            st.markdown("### ⏰ 구매 주기 임박 (TOP 6~15 업체)")
            st.caption("💡 TOP 5 다음 순위 업체 중 재구매 예상 품목")
            
            다음_업체 = 고객_매출[5:15] if len(고객_매출) > 5 else []
            
            모든_임박 = []
            for item in 다음_업체:
                거래처 = item['거래처']
                주기_분석 = 구매주기_분석(거래처, ledger_df)
                # 최근 6개월 내 거래된 품목만 필터링
                최근_품목 = 최근6개월_df[최근6개월_df['거래처'] == 거래처]['품목'].dropna().unique()
                주기_분석 = [x for x in 주기_분석 if any(str(x['품목']) in str(p) for p in 최근_품목)]
                
                for 품목 in 주기_분석:
                    if 품목['남은일수'] <= 14:  # 2주 이내
                        모든_임박.append({
                            '거래처': 거래처,
                            '매출': item['총매출'],
                            **품목
                        })
            
            모든_임박.sort(key=lambda x: x['남은일수'])
            
            if 모든_임박:
                임박_df = pd.DataFrame(모든_임박[:15])  # 상위 15개
                임박_df['다음예상'] = pd.to_datetime(임박_df['다음예상']).dt.strftime('%m/%d')
                임박_df['마지막구매'] = pd.to_datetime(임박_df['마지막구매']).dt.strftime('%m/%d')
                임박_df['상태'] = 임박_df['남은일수'].apply(
                    lambda x: '🔴 지남' if x <= 0 else '🟠 임박' if x <= 3 else '🟡 이번주' if x <= 7 else '🟢 여유'
                )
                
                display_df = 임박_df[['상태', '거래처', '품목', '평균주기', '마지막구매', '다음예상', '남은일수']]
                display_df.columns = ['상태', '거래처', '품목', '주기', '마지막', '예상일', 'D-day']
                
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
            
            # ===== 미수금 현황 (base_receivables에서 가져옴) =====
            st.markdown("### 💰 미수금 현황")
            
            # base_receivables에서 미수금 가져오기 (컴장부 GULREST 값)
            기초미수금_dict = base_recv_df.set_index('거래처')['기초미수금'].to_dict() if len(base_recv_df) > 0 else {}
            미수금 = 기초미수금_dict.get(선택_고객, 0)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("총 거래 횟수", f"{len(고객_df)}건")
            with col_b:
                총_판매금액 = 고객_df['공급가액'].sum() + 고객_df['부가세'].sum()
                st.metric("총 판매금액", f"{총_판매금액:,.0f}원")
            with col_c:
                delta_color = "inverse" if 미수금 > 0 else "normal"
                st.metric("현재 미수금", f"{미수금:,.0f}원", delta="미수" if 미수금 > 0 else "완납", delta_color=delta_color)
            
            st.markdown("---")
            
            # ===== 연도별 매출 현황 =====
            st.markdown("### 📅 연도별 매출 현황")
            
            전체_거래처_df = ledger_df[ledger_df['거래처'] == 선택_고객].copy()
            
            if len(전체_거래처_df) > 0:
                # 연도 추출
                전체_거래처_df['연도'] = 전체_거래처_df['날짜'].dt.year
                
                # 당해년도, 전년도
                당해연도 = datetime.now().year
                전년도 = 당해연도 - 1
                
                연도별_데이터 = []
                for 연도 in [당해연도, 전년도]:
                    연도_df = 전체_거래처_df[전체_거래처_df['연도'] == 연도]
                    
                    # 판매 (입금/출금 제외, 공급가액 > 0)
                    판매_df = 연도_df[(연도_df['공급가액'] > 0) & (~연도_df['참조'].str.contains('입금|출금', na=False))]
                    매출액 = 판매_df['공급가액'].sum()
                    부가세 = 판매_df['부가세'].sum()
                    합계 = 매출액 + 부가세
                    
                    # 입금
                    입금_df = 연도_df[연도_df['참조'].str.contains('입금', na=False)]
                    입금액 = abs(입금_df['공급가액'].sum())
                    
                    연도별_데이터.append({
                        '연도': f"{연도}년",
                        '매출액': 매출액,
                        '부가세': 부가세,
                        '합계': 합계,
                        '입금액': 입금액
                    })
                
                # 테이블 형식으로 표시
                col1, col2 = st.columns(2)
                
                for i, data in enumerate(연도별_데이터):
                    with col1 if i == 0 else col2:
                        st.markdown(f"#### {data['연도']} {'(당해)' if i == 0 else '(전년)'}")
                        st.markdown(f"""
                        | 항목 | 금액 |
                        |------|------|
                        | 매출액 | {data['매출액']:,.0f}원 |
                        | 부가세 | {data['부가세']:,.0f}원 |
                        | **합계** | **{data['합계']:,.0f}원** |
                        | 입금액 | {data['입금액']:,.0f}원 |
                        """)
            
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
        
        # 거래처 정보 파일 경로
        from pathlib import Path
        data_dir = Path("data")
        customers_file = data_dir / "customers.csv"
        
        # 거래처 정보 로드
        if customers_file.exists():
            customers_df = pd.read_csv(customers_file)
        else:
            customers_df = pd.DataFrame(columns=[
                '거래처명', '구분', '사업자번호', '대표자명', '업태', '종목',
                '주소', '전화번호', '팩스번호', '휴대폰', '이메일',
                '대신화물_지점', '경동화물_지점', '담당자명', '담당자연락처', '메모'
            ])
        
        # 서브탭
        sub_tab1, sub_tab2 = st.tabs(["📝 거래처 등록/수정", "📋 거래처 목록"])
        
        # ===== 서브탭1: 거래처 등록/수정 =====
        with sub_tab1:
            st.markdown("#### 거래처 정보 입력")
            
            # 기존 거래처 선택 또는 신규 입력
            try:
                ledger_data = st.session_state.get('ledger_df', None)
                if ledger_data is not None and isinstance(ledger_data, pd.DataFrame) and len(ledger_data) > 0 and '거래처' in ledger_data.columns:
                    기존_거래처_list = sorted(ledger_data['거래처'].dropna().unique().tolist())
                else:
                    기존_거래처_list = []
            except:
                기존_거래처_list = []
            
            등록된_거래처_list = customers_df['거래처명'].tolist() if len(customers_df) > 0 else []
            
            입력_방식 = st.radio("입력 방식", ["기존 거래처 선택", "신규 거래처 입력"], horizontal=True, label_visibility="collapsed")
            
            if 입력_방식 == "기존 거래처 선택":
                if 기존_거래처_list:
                    선택_거래처 = st.selectbox("거래처 선택", 기존_거래처_list, key="customer_select")
                    # 이미 등록된 거래처면 기존 정보 불러오기
                    if 선택_거래처 in 등록된_거래처_list:
                        기존_정보 = customers_df[customers_df['거래처명'] == 선택_거래처].iloc[0].to_dict()
                        st.info(f"✅ '{선택_거래처}'의 기존 정보를 불러왔습니다. 수정 후 저장하세요.")
                    else:
                        기존_정보 = {}
                else:
                    st.warning("거래 내역이 없습니다. 먼저 거래를 입력하세요.")
                    선택_거래처 = ""
                    기존_정보 = {}
            else:
                선택_거래처 = st.text_input("거래처명 입력", key="new_customer_name")
                기존_정보 = {}
            
            if 선택_거래처:
                st.markdown("---")
                
                # 구분
                구분_옵션 = ["고객업체 (판매)", "매입업체 (구매)", "혼합 (판매+구매)"]
                구분_기본값 = 구분_옵션.index(기존_정보.get('구분', '고객업체 (판매)')) if 기존_정보.get('구분') in 구분_옵션 else 0
                구분 = st.selectbox("구분", 구분_옵션, index=구분_기본값)
                
                st.markdown("##### 📋 사업자 정보")
                col1, col2 = st.columns(2)
                with col1:
                    사업자번호 = st.text_input("사업자등록번호", value=기존_정보.get('사업자번호', ''), placeholder="000-00-00000")
                    대표자명 = st.text_input("대표자명", value=기존_정보.get('대표자명', ''))
                with col2:
                    업태 = st.text_input("업태", value=기존_정보.get('업태', ''), placeholder="도소매")
                    종목 = st.text_input("종목", value=기존_정보.get('종목', ''), placeholder="공구, 철물")
                
                주소 = st.text_input("사업장 주소", value=기존_정보.get('주소', ''), placeholder="시/도 구/군 상세주소")
                
                st.markdown("##### 📞 연락처 정보")
                col1, col2, col3 = st.columns(3)
                with col1:
                    전화번호 = st.text_input("전화번호", value=기존_정보.get('전화번호', ''), placeholder="043-000-0000")
                with col2:
                    팩스번호 = st.text_input("팩스번호", value=기존_정보.get('팩스번호', ''), placeholder="043-000-0001")
                with col3:
                    휴대폰 = st.text_input("휴대폰", value=기존_정보.get('휴대폰', ''), placeholder="010-0000-0000")
                
                이메일 = st.text_input("이메일 (홈택스용)", value=기존_정보.get('이메일', ''), placeholder="example@email.com")
                
                st.markdown("##### 🚚 화물/배송 정보")
                col1, col2 = st.columns(2)
                with col1:
                    대신화물_지점 = st.text_input("대신화물 지점", value=기존_정보.get('대신화물_지점', ''), placeholder="청주 지점명")
                with col2:
                    경동화물_지점 = st.text_input("경동화물 지점", value=기존_정보.get('경동화물_지점', ''), placeholder="청주 지점명")
                
                st.markdown("##### 👤 담당자 정보")
                col1, col2 = st.columns(2)
                with col1:
                    담당자명 = st.text_input("담당자명", value=기존_정보.get('담당자명', ''))
                with col2:
                    담당자연락처 = st.text_input("담당자 연락처", value=기존_정보.get('담당자연락처', ''), placeholder="010-0000-0000")
                
                메모 = st.text_area("메모", value=기존_정보.get('메모', ''), placeholder="특이사항, 배송 요청사항 등", height=80)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 저장", type="primary", use_container_width=True):
                        # 새 데이터 생성
                        new_data = {
                            '거래처명': 선택_거래처,
                            '구분': 구분,
                            '사업자번호': 사업자번호,
                            '대표자명': 대표자명,
                            '업태': 업태,
                            '종목': 종목,
                            '주소': 주소,
                            '전화번호': 전화번호,
                            '팩스번호': 팩스번호,
                            '휴대폰': 휴대폰,
                            '이메일': 이메일,
                            '대신화물_지점': 대신화물_지점,
                            '경동화물_지점': 경동화물_지점,
                            '담당자명': 담당자명,
                            '담당자연락처': 담당자연락처,
                            '메모': 메모
                        }
                        
                        # 기존 거래처면 업데이트, 신규면 추가
                        if 선택_거래처 in 등록된_거래처_list:
                            customers_df.loc[customers_df['거래처명'] == 선택_거래처] = pd.DataFrame([new_data]).values[0]
                            st.success(f"✅ '{선택_거래처}' 정보가 수정되었습니다!")
                        else:
                            customers_df = pd.concat([customers_df, pd.DataFrame([new_data])], ignore_index=True)
                            st.success(f"✅ '{선택_거래처}' 정보가 등록되었습니다!")
                        
                        # 저장
                        customers_df.to_csv(customers_file, index=False, encoding='utf-8-sig')
                        st.rerun()
                
                with col2:
                    if 선택_거래처 in 등록된_거래처_list:
                        if st.button("🗑️ 삭제", type="secondary", use_container_width=True):
                            customers_df = customers_df[customers_df['거래처명'] != 선택_거래처]
                            customers_df.to_csv(customers_file, index=False, encoding='utf-8-sig')
                            st.success(f"'{선택_거래처}' 정보가 삭제되었습니다.")
                            st.rerun()
        
        # ===== 서브탭2: 거래처 목록 =====
        with sub_tab2:
            st.markdown("#### 등록된 거래처 목록")
            
            if len(customers_df) > 0:
                # 검색
                검색어 = st.text_input("🔍 거래처 검색", placeholder="거래처명, 사업자번호, 담당자명으로 검색")
                
                표시_df = customers_df.copy()
                if 검색어:
                    표시_df = 표시_df[
                        표시_df['거래처명'].str.contains(검색어, na=False) |
                        표시_df['사업자번호'].str.contains(검색어, na=False) |
                        표시_df['담당자명'].str.contains(검색어, na=False)
                    ]
                
                st.markdown(f"**총 {len(표시_df)}개 거래처**")
                
                # 주요 정보만 표시
                표시_컬럼 = ['거래처명', '구분', '사업자번호', '전화번호', '팩스번호', '대신화물_지점', '경동화물_지점', '담당자명']
                표시_df_short = 표시_df[표시_컬럼].fillna('')
                
                st.dataframe(표시_df_short, use_container_width=True, hide_index=True)
                
                # CSV 다운로드
                csv_data = customers_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="📥 거래처 목록 다운로드 (CSV)",
                    data=csv_data,
                    file_name=f"거래처목록_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("등록된 거래처가 없습니다. '거래처 등록/수정' 탭에서 거래처를 등록하세요.")

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