import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import hashlib

# Google Sheets ì—°ë™
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

# í•œêµ­ ì‹œê°„ëŒ€ ì„¤ì • (UTC+9) - timezone-naiveë¡œ ë°˜í™˜
def get_kst_now():
    """í•œêµ­ í˜„ìž¬ ì‹œê°„ ë°˜í™˜ (UTC+9)"""
    import time
    # UTC ì‹œê°„ì— 9ì‹œê°„ ë”í•´ì„œ í•œêµ­ ì‹œê°„ ê³„ì‚°
    utc_now = datetime.utcnow()
    kst_now = utc_now + timedelta(hours=9)
    return kst_now

def get_kst_today():
    """í•œêµ­ ì˜¤ëŠ˜ ë‚ ì§œ ë°˜í™˜"""
    return get_kst_now().date()

# Google Sheets ì—°ê²° í•¨ìˆ˜
def get_google_sheets_connection():
    """Google Sheets API ì—°ê²°"""
    if not GSPREAD_AVAILABLE:
        return None, None
    
    try:
        if "gcp_service_account" not in st.secrets:
            return None, None
        
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(credentials)
        spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        spreadsheet = client.open_by_key(spreadsheet_id)
        return client, spreadsheet
    except Exception as e:
        st.error(f"Google Sheets ì—°ê²° ì˜¤ë¥˜: {e}")
        return None, None

def sync_to_google_sheets(df, sheet_name):
    """ë°ì´í„°í”„ë ˆìž„ì„ Google Sheetsì— ë™ê¸°í™”"""
    try:
        _, spreadsheet = get_google_sheets_connection()
        if spreadsheet is None:
            return False
        
        # ì‹œíŠ¸ ì°¾ê¸° ë˜ëŠ” ìƒì„±
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
        
        # ë°ì´í„°í”„ë ˆìž„ì„ ì‹œíŠ¸ì— ì“°ê¸°
        worksheet.clear()
        
        if len(df) > 0:
            # í—¤ë”ì™€ ë°ì´í„° ì¤€ë¹„
            df_copy = df.copy()
            # ë‚ ì§œ ì»¬ëŸ¼ ë¬¸ìžì—´ë¡œ ë³€í™˜
            for col in df_copy.columns:
                if df_copy[col].dtype == 'datetime64[ns]':
                    df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
                df_copy[col] = df_copy[col].astype(str).replace('nan', '').replace('NaT', '')
            
            # í—¤ë” + ë°ì´í„°
            data = [df_copy.columns.tolist()] + df_copy.values.tolist()
            worksheet.update('A1', data)
        else:
            # ë¹ˆ ë°ì´í„°í”„ë ˆìž„ì´ë©´ í—¤ë”ë§Œ
            worksheet.update('A1', [df.columns.tolist()])
        
        return True
    except Exception as e:
        st.error(f"Google Sheets ë™ê¸°í™” ì˜¤ë¥˜: {e}")
        return False

def load_from_google_sheets(sheet_name):
    """Google Sheetsì—ì„œ ë°ì´í„° ë¶ˆëŸ¬ì˜¤ê¸°"""
    try:
        _, spreadsheet = get_google_sheets_connection()
        if spreadsheet is None:
            return None
        
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            data = worksheet.get_all_records()
            if data:
                return pd.DataFrame(data)
            return None
        except gspread.exceptions.WorksheetNotFound:
            return None
    except Exception as e:
        return None

# íŽ˜ì´ì§€ ì„¤ì •
st.set_page_config(
    page_title="ëˆ„ë¦¬ì— ì•Œì˜¤ ìž¥ë¶€ê´€ë¦¬",
    page_icon="ðŸ“Š",
    layout="wide"
)

# ========== ì „ì²´ UI ìŠ¤íƒ€ì¼ ê°œì„  CSS ==========
st.markdown("""
<style>
/* ëª¨ë“  selectbox ì„ íƒëœ í•­ëª© - ê²€ì •ìƒ‰ ê¸€ìž */
div[data-baseweb="select"] > div {
    color: #000000 !important;
}
div[data-baseweb="select"] span {
    color: #000000 !important;
}

/* selectbox ë“œë¡­ë‹¤ìš´ ì˜µì…˜ - ê²€ì •ìƒ‰ ê¸€ìž */
ul[role="listbox"] li {
    color: #000000 !important;
}

/* multiselect íƒœê·¸ ìŠ¤íƒ€ì¼ ìœ ì§€ (ê±°ëž˜ìœ í˜• íƒœê·¸) */
span[data-baseweb="tag"] {
    background-color: #4a90e2 !important;
    color: white !important;
}

/* text input ê¸€ìžìƒ‰ */
input[type="text"], textarea {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)

# ë¹„ë°€ë²ˆí˜¸ í•´ì‹± í•¨ìˆ˜
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ë¡œê·¸ì¸ ì²´í¬
def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in

# ë¡œê·¸ì¸ í™”ë©´
def login_page():
    st.markdown("<h1 style='text-align: center; color: #4a90e2;'>ðŸ” ëˆ„ë¦¬ì— ì•Œì˜¤ ìž¥ë¶€ê´€ë¦¬</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #cccccc;'>ë¡œê·¸ì¸ì´ í•„ìš”í•©ë‹ˆë‹¤</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        password = st.text_input("ë¹„ë°€ë²ˆí˜¸", type="password", placeholder="ë¹„ë°€ë²ˆí˜¸ë¥¼ ìž…ë ¥í•˜ì„¸ìš”")
        
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("ðŸ”“ ë¡œê·¸ì¸", use_container_width=True, type="primary"):
                # ë¹„ë°€ë²ˆí˜¸: 1248
                correct_hash = hash_password("1248")
                input_hash = hash_password(password)
                
                if input_hash == correct_hash:
                    st.session_state.logged_in = True
                    st.success("âœ… ë¡œê·¸ì¸ ì„±ê³µ!")
                    st.rerun()
                else:
                    st.error("âŒ ë¹„ë°€ë²ˆí˜¸ê°€ í‹€ë ¸ìŠµë‹ˆë‹¤.")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.info("ðŸ’¡ **ë¹„ë°€ë²ˆí˜¸ë¥¼ ìžŠìœ¼ì…¨ë‚˜ìš”?**\n\nê´€ë¦¬ìžì—ê²Œ ë¬¸ì˜í•˜ì„¸ìš”.")

# ë¡œê·¸ì•„ì›ƒ í•¨ìˆ˜
def logout():
    st.session_state.logged_in = False
    st.rerun()

# ì»¤ìŠ¤í…€ CSS - ì„¸ë ¨ëœ ë‹¤í¬ í…Œë§ˆ (ê¸€ìž 2/3 í¬ê¸°)
st.markdown("""
<style>
    /* ==================== ì „ì²´ ë°°ê²½ ==================== */
    .stApp {
        background-color: #0f0f0f !important;
        color: #e0e0e0 !important;
    }
    
    /* ë©”ì¸ ì»¨í…ì¸  ì˜ì—­ */
    .main .block-container {
        background-color: #0f0f0f !important;
        padding: 1.5rem !important;
        max-width: 1400px !important;
    }
    
    /* ì‚¬ì´ë“œë°” */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }
    
    /* ==================== í…ìŠ¤íŠ¸ ìŠ¤íƒ€ì¼ (2/3 í¬ê¸°) ==================== */
    /* ì¼ë°˜ í…ìŠ¤íŠ¸ */
    .stApp p, .stApp span, .stApp div, .stApp label {
        color: #e0e0e0 !important;
        font-size: 1.0rem !important;
        font-weight: 500 !important;
    }
    
    /* ì œëª© */
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
    
    /* ==================== ìž…ë ¥ í•„ë“œ ==================== */
    /* í…ìŠ¤íŠ¸ ìž…ë ¥ */
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
    
    /* í…ìŠ¤íŠ¸ ì˜ì—­ */
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
    
    /* ìˆ«ìž ìž…ë ¥ */
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
    
    /* ë‚ ì§œ ìž…ë ¥ */
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
    
    /* ==================== ë“œë¡­ë‹¤ìš´ (ì…€ë ‰íŠ¸ë°•ìŠ¤) - ì„ íƒê°’ ë³´ì´ê²Œ! ==================== */
    /* ë“œë¡­ë‹¤ìš´ ì»¨í…Œì´ë„ˆ */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 3px solid #666666 !important;
        border-radius: 8px !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ ê¸°ë³¸ ìŠ¤íƒ€ì¼ */
    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ ì„ íƒëœ ê°’ì„ ë‹´ëŠ” ì»¨í…Œì´ë„ˆ */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        padding: 10px !important;
    }
    
    /* ì„ íƒëœ ê°’ í…ìŠ¤íŠ¸ - ìµœìš°ì„  ì ìš©! */
    .stSelectbox [data-baseweb="select"] > div > div {
        color: #000000 !important;
        background-color: transparent !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div > div > div {
        color: #000000 !important;
    }
    
    /* ëª¨ë“  span íƒœê·¸ */
    .stSelectbox [data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* input íƒœê·¸ (ê²€ìƒ‰ìš©) */
    .stSelectbox [data-baseweb="select"] input {
        color: #000000 !important;
        caret-color: #000000 !important;
    }
    
    /* placeholder */
    .stSelectbox [data-baseweb="select"] input::placeholder {
        color: #666666 !important;
    }
    
    /* ì„ íƒëœ ê°’ì„ ë³´ì—¬ì£¼ëŠ” ëª¨ë“  ìš”ì†Œì— ê°•ì œ ì ìš© */
    .stSelectbox div[role="button"] {
        color: #000000 !important;
    }
    
    .stSelectbox div[role="button"] * {
        color: #000000 !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ í™”ì‚´í‘œ */
    .stSelectbox svg {
        fill: #000000 !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ ì—´ë ¸ì„ ë•Œ ë©”ë‰´ */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
        border: 2px solid #666666 !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ ì˜µì…˜ ë¦¬ìŠ¤íŠ¸ */
    [role="listbox"] {
        background-color: #ffffff !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ ê° ì˜µì…˜ */
    [role="option"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ ì˜µì…˜ í˜¸ë²„ */
    [role="option"]:hover {
        background-color: #e8e8e8 !important;
        color: #000000 !important;
    }
    
    /* ë“œë¡­ë‹¤ìš´ ì„ íƒëœ ì˜µì…˜ */
    [role="option"][aria-selected="true"] {
        background-color: #d0d0d0 !important;
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* ==================== ë©€í‹°ì…€ë ‰íŠ¸ ==================== */
    .stMultiSelect [data-baseweb="select"] {
        background-color: #1e1e1e !important;
        border: 2px solid #424242 !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #1e88e5 !important;
        color: #ffffff !important;
        font-size: 0.95rem !important;
    }
    
    /* ==================== ë²„íŠ¼ ==================== */
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
    
    /* ë‹¤ìš´ë¡œë“œ ë²„íŠ¼ */
    .stDownloadButton > button {
        background-color: #17a2b8 !important;
        color: #ffffff !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
    }
    
    /* ==================== ë¼ë””ì˜¤ ë²„íŠ¼ ==================== */
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
    
    /* ë¼ë””ì˜¤ ë²„íŠ¼ ì›í˜• ì•„ì´ì½˜ */
    .stRadio input[type="radio"] {
        width: 20px !important;
        height: 20px !important;
    }
    
    /* ==================== ì²´í¬ë°•ìŠ¤ ==================== */
    .stCheckbox label {
        font-size: 1.0rem !important;
        font-weight: 500 !important;
        color: #e0e0e0 !important;
    }
    
    /* ==================== ë©”íŠ¸ë¦­ (ì§€í‘œ) ==================== */
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
    
    /* ==================== ë°ì´í„°í”„ë ˆìž„ ==================== */
    .stDataFrame {
        font-size: 0.95rem !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background-color: #1a1a1a !important;
        border: 1px solid #424242 !important;
        border-radius: 6px !important;
    }
    
    /* ==================== ì •ë³´ ë°•ìŠ¤ ==================== */
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
    
    /* ==================== íƒ­ ==================== */
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
    
    /* ==================== ë§ˆí¬ë‹¤ìš´ ==================== */
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
    
    /* ==================== ë¡œë”© ìŠ¤í”¼ë„ˆ ==================== */
    .stSpinner > div {
        border-top-color: #1e88e5 !important;
    }
    
    /* ==================== ì‚¬ì´ë“œë°” ë©”ë‰´ ==================== */
    [data-testid="stSidebar"] .stRadio > label {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    
    /* ==================== ì¶”ê°€ ë¯¸ì„¸ ì¡°ì • ==================== */
    input::placeholder, textarea::placeholder {
        color: #757575 !important;
        opacity: 1 !important;
    }
    
    /* í¬ì»¤ìŠ¤ ìƒíƒœ */
    input:focus, textarea:focus, select:focus {
        outline: none !important;
        border-color: #1e88e5 !important;
        box-shadow: 0 0 0 3px rgba(30, 136, 229, 0.2) !important;
    }
    
    /* ìŠ¤í¬ë¡¤ë°” */
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

# ë°ì´í„° íŒŒì¼ ê²½ë¡œ
DATA_FILE = "data/ledger.csv"
BASE_RECEIVABLE_FILE = "data/base_receivables.csv"
PRODUCTS_FILE = "data/products.csv"
INVENTORY_FILE = "data/inventory.csv"
COMPANY_FILE = "data/company_info.csv"

# ì„¸ì…˜ ìƒíƒœ ì´ˆê¸°í™”
if 'ledger_df' not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.ledger_df = pd.read_csv(DATA_FILE, parse_dates=['ë‚ ì§œ'])
        # ê¸°ì¡´ ë°ì´í„°ì— ë¹„ê³  ì»¬ëŸ¼ì´ ì—†ìœ¼ë©´ ì¶”ê°€
        if 'ë¹„ê³ ' not in st.session_state.ledger_df.columns:
            st.session_state.ledger_df['ë¹„ê³ '] = ''
        # âœ… 2019-08-01 ì´ì „ ë¶ˆí•„ìš”í•œ ë°ì´í„° í•„í„°ë§ (ë¡œë”© ì†ë„ í–¥ìƒ)
        st.session_state.ledger_df = st.session_state.ledger_df[
            st.session_state.ledger_df['ë‚ ì§œ'] >= '2019-08-01'
        ].reset_index(drop=True)
    else:
        st.session_state.ledger_df = pd.DataFrame(columns=['ë‚ ì§œ', 'ê±°ëž˜ì²˜', 'í’ˆëª©', 'ìˆ˜ëŸ‰', 'ë‹¨ê°€', 'ê³µê¸‰ê°€ì•¡', 'ë¶€ê°€ì„¸', 'ì°¸ì¡°', 'ë¹„ê³ '])

# ê¸°ì´ˆ ë¯¸ìˆ˜ê¸ˆ ì´ˆê¸°í™”
if 'base_receivables_df' not in st.session_state:
    if os.path.exists(BASE_RECEIVABLE_FILE):
        st.session_state.base_receivables_df = pd.read_csv(BASE_RECEIVABLE_FILE)
    else:
        st.session_state.base_receivables_df = pd.DataFrame(columns=['ê±°ëž˜ì²˜', 'ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ', 'ê¸°ì¤€ì¼ìž'])

# í’ˆëª© ë°ì´í„° ì´ˆê¸°í™”
if 'products_df' not in st.session_state:
    if os.path.exists(PRODUCTS_FILE):
        st.session_state.products_df = pd.read_csv(PRODUCTS_FILE)
    else:
        st.session_state.products_df = pd.DataFrame(columns=['í’ˆëª©ì½”ë“œ', 'í’ˆëª©ëª…', 'ì¹´í…Œê³ ë¦¬', 'ê·œê²©'])

# ìž¬ê³  ë°ì´í„° ì´ˆê¸°í™”
if 'inventory_df' not in st.session_state:
    if os.path.exists(INVENTORY_FILE):
        st.session_state.inventory_df = pd.read_csv(INVENTORY_FILE)
    else:
        st.session_state.inventory_df = pd.DataFrame(columns=['í’ˆëª©ëª…', 'ê¸°ì´ˆìž¬ê³ ', 'í˜„ìž¬ìž¬ê³ ', 'ê¸°ì¤€ì¼ìž', 'ì•ˆì „ìž¬ê³ ', 'ë‹¨ìœ„'])

# ì‚¬ì—…ìž ì •ë³´ ì´ˆê¸°í™”
if 'company_info' not in st.session_state:
    import json
    company_json_file = "data/company_info.json"
    
    # JSON íŒŒì¼ ìš°ì„  ì‹œë„
    if os.path.exists(company_json_file):
        try:
            with open(company_json_file, 'r', encoding='utf-8') as f:
                st.session_state.company_info = json.load(f)
        except:
            st.session_state.company_info = {
                'ìƒí˜¸': 'ëˆ„ë¦¬ì— ì•Œì˜¤',
                'ëŒ€í‘œìž': 'ë°•ìˆ˜ì˜',
                'ì‚¬ì—…ìžë²ˆí˜¸': '320-14-00707',
                'ì£¼ì†Œ': 'ëŒ€ì „ê´‘ì—­ì‹œ ìœ ì„±êµ¬ ë³µìš©ë¡œ11ë²ˆê¸¸ 6-35',
                'ì „í™”ë²ˆí˜¸': '010-6473-1246',
                'íŒ©ìŠ¤ë²ˆí˜¸': '042-367-1246'
            }
    # ê¸°ì¡´ CSV íŒŒì¼ ì‹œë„ (í•˜ìœ„ í˜¸í™˜)
    elif os.path.exists(COMPANY_FILE):
        try:
            company_df = pd.read_csv(COMPANY_FILE)
            if len(company_df) > 0:
                st.session_state.company_info = company_df.iloc[0].to_dict()
            else:
                st.session_state.company_info = {
                    'ìƒí˜¸': 'ëˆ„ë¦¬ì— ì•Œì˜¤',
                    'ëŒ€í‘œìž': 'ë°•ìˆ˜ì˜',
                    'ì‚¬ì—…ìžë²ˆí˜¸': '320-14-00707',
                    'ì£¼ì†Œ': 'ëŒ€ì „ê´‘ì—­ì‹œ ìœ ì„±êµ¬ ë³µìš©ë¡œ11ë²ˆê¸¸ 6-35',
                    'ì „í™”ë²ˆí˜¸': '010-6473-1246',
                    'íŒ©ìŠ¤ë²ˆí˜¸': '042-367-1246'
                }
        except:
            st.session_state.company_info = {
                'ìƒí˜¸': 'ëˆ„ë¦¬ì— ì•Œì˜¤',
                'ëŒ€í‘œìž': 'ë°•ìˆ˜ì˜',
                'ì‚¬ì—…ìžë²ˆí˜¸': '320-14-00707',
                'ì£¼ì†Œ': 'ëŒ€ì „ê´‘ì—­ì‹œ ìœ ì„±êµ¬ ë³µìš©ë¡œ11ë²ˆê¸¸ 6-35',
                'ì „í™”ë²ˆí˜¸': '010-6473-1246',
                'íŒ©ìŠ¤ë²ˆí˜¸': '042-367-1246'
            }
    else:
        st.session_state.company_info = {
            'ìƒí˜¸': 'ëˆ„ë¦¬ì— ì•Œì˜¤',
            'ëŒ€í‘œìž': 'ë°•ìˆ˜ì˜',
            'ì‚¬ì—…ìžë²ˆí˜¸': '320-14-00707',
            'ì£¼ì†Œ': 'ëŒ€ì „ê´‘ì—­ì‹œ ìœ ì„±êµ¬ ë³µìš©ë¡œ11ë²ˆê¸¸ 6-35',
            'ì „í™”ë²ˆí˜¸': '010-6473-1246',
            'íŒ©ìŠ¤ë²ˆí˜¸': '042-367-1246'
        }

# ë°ì´í„° ì €ìž¥ í•¨ìˆ˜
def save_data():
    st.session_state.ledger_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# === NEW OPTIMIZED FUNCTIONS ===
# Column constants
_COL_CUST = '거래처'
_COL_BASE = '기초미수금'
_COL_DATE = '기준일자'
_COL_TDATE = '날짜'
_COL_REF = '참조'
_COL_AMT = '공급가액'
_COL_VAT = '부가세'

def calculate_receivable(cust_name, df=None):
    """Calculate receivables: base + (sales after base_date) - deposits"""
    if df is None:
        df = st.session_state.ledger_df
    
    base_amt = 0
    base_dt = None
    base_df = st.session_state.base_receivables_df
    
    if len(base_df) > 0:
        cb = base_df[base_df[_COL_CUST] == cust_name]
        if len(cb) > 0:
            val = cb[_COL_BASE].values[0]
            if val > 0:
                base_amt = val
            try:
                base_dt = pd.to_datetime(str(cb[_COL_DATE].values[0]))
            except:
                pass
    
    if len(df) == 0:
        return base_amt
    
    cdf = df[df[_COL_CUST] == cust_name].copy()
    if len(cdf) == 0:
        return base_amt
    
    if base_dt is not None:
        cdf[_COL_TDATE] = pd.to_datetime(cdf[_COL_TDATE])
        cdf = cdf[cdf[_COL_TDATE] > base_dt]
    
    if len(cdf) == 0:
        return base_amt
    
    sale_mask = (cdf[_COL_REF] == '=외출') | ((cdf[_COL_AMT] > 0) & (~cdf[_COL_REF].fillna('').str.contains('입금|출금')))
    t_sale = cdf.loc[sale_mask, _COL_AMT].sum()
    t_vat = cdf.loc[sale_mask, _COL_VAT].sum()
    
    dep_mask = (cdf[_COL_REF] == '=입금') | (cdf[_COL_REF].fillna('').str.contains('입금'))
    t_dep = cdf.loc[dep_mask, _COL_AMT].sum()
    
    return base_amt + t_sale + t_vat - t_dep

def calculate_payable(cust_name, df=None):
    """Calculate payables: base + (purchases after base_date) - withdrawals"""
    if df is None:
        df = st.session_state.ledger_df
    
    base_amt = 0
    base_dt = None
    base_df = st.session_state.base_receivables_df
    
    if len(base_df) > 0:
        cb = base_df[base_df[_COL_CUST] == cust_name]
        if len(cb) > 0:
            val = cb[_COL_BASE].values[0]
            if val < 0:
                base_amt = abs(val)
            try:
                base_dt = pd.to_datetime(str(cb[_COL_DATE].values[0]))
            except:
                pass
    
    if len(df) == 0:
        return base_amt
    
    cdf = df[df[_COL_CUST] == cust_name].copy()
    if len(cdf) == 0:
        return base_amt
    
    if base_dt is not None:
        cdf[_COL_TDATE] = pd.to_datetime(cdf[_COL_TDATE])
        cdf = cdf[cdf[_COL_TDATE] > base_dt]
    
    if len(cdf) == 0:
        return base_amt
    
    pur_mask = (cdf[_COL_REF] == '=외입') | ((cdf[_COL_AMT] < 0) & (~cdf[_COL_REF].fillna('').str.contains('출금|입금')))
    t_pur = abs(cdf.loc[pur_mask, _COL_AMT].sum())
    t_vat = abs(cdf.loc[pur_mask, _COL_VAT].sum())
    
    wd_mask = (cdf[_COL_REF] == '=출금') | (cdf[_COL_REF].fillna('').str.contains('출금'))
    t_wd = abs(cdf.loc[wd_mask, _COL_AMT].sum())
    
    return base_amt + t_pur + t_vat - t_wd

def calculate_all_receivables(df=None):
    """Calculate all receivables"""
    if df is None:
        df = st.session_state.ledger_df
    base_df = st.session_state.base_receivables_df.copy()
    
    custs = set()
    if len(base_df) > 0:
        custs.update(base_df[_COL_CUST].unique())
    if len(df) > 0:
        custs.update(df[_COL_CUST].dropna().unique())
    
    res = []
    for c in custs:
        r = calculate_receivable(c, df)
        if r > 0:
            cdf = df[df[_COL_CUST] == c] if len(df) > 0 else pd.DataFrame()
            if len(cdf) > 0:
                ld = pd.to_datetime(cdf[_COL_TDATE]).max().strftime('%Y-%m-%d')
            else:
                cb = base_df[base_df[_COL_CUST] == c] if len(base_df) > 0 else pd.DataFrame()
                ld = cb[_COL_DATE].values[0] if len(cb) > 0 else ''
            res.append({_COL_CUST: c, '미수금': r, '최근거래일': ld})
    
    if not res:
        return pd.DataFrame(columns=[_COL_CUST, '미수금', '최근거래일'])
    return pd.DataFrame(res).sort_values('미수금', ascending=False)

def calculate_all_payables(df=None):
    """Calculate all payables"""
    if df is None:
        df = st.session_state.ledger_df
    base_df = st.session_state.base_receivables_df.copy()
    
    custs = set()
    if len(base_df) > 0:
        custs.update(base_df[_COL_CUST].unique())
    if len(df) > 0:
        custs.update(df[_COL_CUST].dropna().unique())
    
    res = []
    for c in custs:
        p = calculate_payable(c, df)
        if p > 0:
            cdf = df[df[_COL_CUST] == c] if len(df) > 0 else pd.DataFrame()
            if len(cdf) > 0:
                ld = pd.to_datetime(cdf[_COL_TDATE]).max().strftime('%Y-%m-%d')
            else:
                cb = base_df[base_df[_COL_CUST] == c] if len(base_df) > 0 else pd.DataFrame()
                ld = cb[_COL_DATE].values[0] if len(cb) > 0 else ''
            res.append({_COL_CUST: c, '미지급금': p, '최근거래일': ld})
    
    if not res:
        return pd.DataFrame(columns=[_COL_CUST, '미지급금', '최근거래일'])
    return pd.DataFrame(res).sort_values('미지급금', ascending=False)

def save_base_receivables():
    st.session_state.base_receivables_df.to_csv(BASE_RECEIVABLE_FILE, index=False, encoding='utf-8-sig')

def save_products():
    st.session_state.products_df.to_csv(PRODUCTS_FILE, index=False, encoding='utf-8-sig')

def save_inventory():
    st.session_state.inventory_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')

def save_company_info():
    """ì‚¬ì—…ìž ì •ë³´ë¥¼ JSON íŒŒì¼ë¡œ ì €ìž¥"""
    import json
    company_json_file = "data/company_info.json"
    try:
        with open(company_json_file, 'w', encoding='utf-8') as f:
            json.dump(st.session_state.company_info, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"ì‚¬ì—…ìž ì •ë³´ ì €ìž¥ ì˜¤ë¥˜: {e}")

def create_invoice_html(ê±°ëž˜ì²˜, ë‚ ì§œ, ê±°ëž˜_ëª©ë¡):
    """ê±°ëž˜ëª…ì„¸ì„œ HTML ìƒì„± - A4 ì„¸ë¡œ 2ë¶„í•  (ê³µê¸‰ë°›ëŠ”ìžìš©/ê³µê¸‰ìžìš©)"""
    
    # ì‚¬ì—…ìž ì •ë³´ ê°€ì ¸ì˜¤ê¸°
    company = st.session_state.company_info
    
    ì´ê³µê¸‰ê°€ì•¡ = sum([g.get('ê³µê¸‰ê°€ì•¡', 0) for g in ê±°ëž˜_ëª©ë¡])
    ì´ë¶€ê°€ì„¸ = sum([g.get('ë¶€ê°€ì„¸', 0) for g in ê±°ëž˜_ëª©ë¡])
    
    # ê±°ëž˜ í•­ëª© HTML (ìµœëŒ€ 10ê°œ í‘œì‹œ)
    ê±°ëž˜_rows = ""
    for i, ê±°ëž˜ in enumerate(ê±°ëž˜_ëª©ë¡[:10], 1):
        í’ˆëª© = str(ê±°ëž˜.get('í’ˆëª©', ''))[:25]
        ìˆ˜ëŸ‰ = ê±°ëž˜.get('ìˆ˜ëŸ‰', 0)
        ë‹¨ê°€ = ê±°ëž˜.get('ë‹¨ê°€', 0)
        ê¸ˆì•¡ = ê±°ëž˜.get('ê³µê¸‰ê°€ì•¡', 0)
        
        ê±°ëž˜_rows += f"""
        <tr>
            <td class="center">{i}</td>
            <td>{í’ˆëª©}</td>
            <td class="right">{ìˆ˜ëŸ‰:,.0f}</td>
            <td class="right">{ë‹¨ê°€:,.0f}</td>
            <td class="right">{ê¸ˆì•¡:,.0f}</td>
        </tr>
        """
    
    # ë¹ˆ í–‰ ì¶”ê°€ (10í–‰ ë§žì¶”ê¸°)
    for i in range(len(ê±°ëž˜_ëª©ë¡[:10]), 10):
        ê±°ëž˜_rows += """
        <tr>
            <td class="center">&nbsp;</td>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
            <td>&nbsp;</td>
        </tr>
        """
    
    # í•œ ìž¥ì— ë“¤ì–´ê°ˆ ëª…ì„¸ì„œ HTML (ê³µê¸‰ë°›ëŠ”ìžìš© ë˜ëŠ” ê³µê¸‰ìžìš©)
    def make_invoice_section(ìš©ë„):
        return f"""
        <div class="invoice-section">
            <div class="invoice-header">
                <span class="title">ê±° ëž˜ ëª… ì„¸ ì„œ</span>
                <span class="usage">({ìš©ë„})</span>
            </div>
            
            <table class="info-table">
                <tr>
                    <td class="label" style="width:15%;">ê³µê¸‰ë°›ëŠ”ìž</td>
                    <td style="width:35%;">{ê±°ëž˜ì²˜}</td>
                    <td class="label" style="width:15%;">ê³µ ê¸‰ ìž</td>
                    <td style="width:35%;">{company.get('ìƒí˜¸', 'ëˆ„ë¦¬ì— ì•Œì˜¤')}</td>
                </tr>
                <tr>
                    <td class="label">ê±° ëž˜ ì¼</td>
                    <td>{ë‚ ì§œ}</td>
                    <td class="label">ëŒ€ í‘œ ìž</td>
                    <td>{company.get('ëŒ€í‘œìž', '')} (ì¸)</td>
                </tr>
                <tr>
                    <td class="label">ì‚¬ì—…ìžë²ˆí˜¸</td>
                    <td></td>
                    <td class="label">ì‚¬ì—…ìžë²ˆí˜¸</td>
                    <td>{company.get('ì‚¬ì—…ìžë²ˆí˜¸', '320-14-00707')}</td>
                </tr>
                <tr>
                    <td class="label">ì£¼ ì†Œ</td>
                    <td></td>
                    <td class="label">ì£¼ ì†Œ</td>
                    <td style="font-size:9px;">{company.get('ì£¼ì†Œ', '')}</td>
                </tr>
                <tr>
                    <td class="label">ì „ í™”</td>
                    <td></td>
                    <td class="label">ì „ í™”</td>
                    <td>{company.get('ì „í™”ë²ˆí˜¸', '')}</td>
                </tr>
            </table>
            
            <table class="main-table">
                <thead>
                    <tr>
                        <th style="width:8%;">No</th>
                        <th style="width:40%;">í’ˆ ëª©</th>
                        <th style="width:14%;">ìˆ˜ëŸ‰</th>
                        <th style="width:18%;">ë‹¨ê°€</th>
                        <th style="width:20%;">ê¸ˆì•¡</th>
                    </tr>
                </thead>
                <tbody>
                    {ê±°ëž˜_rows}
                </tbody>
            </table>
            
            <table class="summary-table">
                <tr>
                    <td class="label">ê³µê¸‰ê°€ì•¡</td>
                    <td class="right">{ì´ê³µê¸‰ê°€ì•¡:,.0f}</td>
                    <td class="label">ë¶€ê°€ì„¸</td>
                    <td class="right">{ì´ë¶€ê°€ì„¸:,.0f}</td>
                    <td class="label total-label">í•© ê³„</td>
                    <td class="right total-value">{ì´ê³µê¸‰ê°€ì•¡ + ì´ë¶€ê°€ì„¸:,.0f}</td>
                </tr>
            </table>
            
            <div class="footer-text">ìœ„ì™€ ê°™ì´ ê±°ëž˜í•©ë‹ˆë‹¤.</div>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ê±°ëž˜ëª…ì„¸ì„œ - {ê±°ëž˜ì²˜}</title>
        <style>
            @page {{ size: A4 portrait; margin: 5mm; }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Malgun Gothic', 'ë§‘ì€ ê³ ë”•', sans-serif; 
                font-size: 10px;
                width: 210mm;
                background: white;
            }}
            .page {{
                width: 200mm;
                height: 290mm;
                margin: 0 auto;
                padding: 3mm;
            }}
            .invoice-section {{
                height: 143mm;
                border: 1px solid #000;
                padding: 3mm;
                margin-bottom: 2mm;
            }}
            .invoice-header {{
                text-align: center;
                margin-bottom: 3mm;
                border-bottom: 2px solid #000;
                padding-bottom: 2mm;
            }}
            .title {{
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 8px;
            }}
            .usage {{
                font-size: 11px;
                margin-left: 10px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 3mm;
            }}
            .info-table td {{
                border: 1px solid #333;
                padding: 2px 4px;
                height: 18px;
            }}
            .info-table .label {{
                background-color: #f0f0f0;
                font-weight: bold;
                text-align: center;
            }}
            .main-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 3mm;
            }}
            .main-table th, .main-table td {{
                border: 1px solid #333;
                padding: 2px 4px;
                height: 16px;
            }}
            .main-table th {{
                background-color: #f0f0f0;
                font-weight: bold;
            }}
            .summary-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 2mm;
            }}
            .summary-table td {{
                border: 1px solid #333;
                padding: 3px 5px;
                height: 22px;
            }}
            .summary-table .label {{
                background-color: #f0f0f0;
                font-weight: bold;
                text-align: center;
                width: 12%;
            }}
            .summary-table .right {{
                text-align: right;
                width: 18%;
            }}
            .summary-table .total-label {{
                background-color: #ddd;
            }}
            .summary-table .total-value {{
                font-weight: bold;
                font-size: 12px;
            }}
            .center {{ text-align: center; }}
            .right {{ text-align: right; }}
            .footer-text {{
                text-align: center;
                margin-top: 3mm;
                font-size: 10px;
            }}
            @media print {{
                body {{ print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
            }}
        </style>
    </head>
    <body>
        <div class="page">
            {make_invoice_section("ê³µê¸‰ë°›ëŠ”ìž ë³´ê´€ìš©")}
            {make_invoice_section("ê³µê¸‰ìž ë³´ê´€ìš©")}
        </div>
    </body>
    </html>
    """
    return html

# ==================== ë¡œê·¸ì¸ ì²´í¬ ====================
if not check_login():
    login_page()
    st.stop()

# ==================== ë©”ì¸ ì• í”Œë¦¬ì¼€ì´ì…˜ ====================
# ì‚¬ì´ë“œë°” - ë©”ë‰´
st.sidebar.title("ðŸ“‹ ìž¥ë¶€ ê´€ë¦¬ ì‹œìŠ¤í…œ")
st.sidebar.markdown("---")

# ì²« í™”ë©´ì„ ê±°ëž˜ì²˜ ê´€ë¦¬ë¡œ ì„¤ì •
if 'first_load' not in st.session_state:
    st.session_state.first_load = True
    st.session_state.default_menu = "ðŸ‘¥ ê±°ëž˜ì²˜ ê´€ë¦¬"

menu_list = ["ðŸ  ëŒ€ì‹œë³´ë“œ", "âž• ê±°ëž˜ ìž…ë ¥", "ðŸ“„ ê±°ëž˜ ë‚´ì—­", "ðŸ“Š í†µê³„ ë¶„ì„", "ðŸ’° ì™¸ìƒ ê´€ë¦¬", "ðŸ§¾ íšŒê³„ ê´€ë¦¬", "ðŸ“¦ í’ˆëª© ê´€ë¦¬", "ðŸ“‹ ìž¬ê³  ê´€ë¦¬", "ðŸ‘¥ ê±°ëž˜ì²˜ ê´€ë¦¬", "ðŸ“… ë°©ë¬¸ ì¼ì •", "ðŸ“ ì˜ì—… ì¼ì§€", "ðŸ“œ í˜‘ì•½ì„œ ê´€ë¦¬", "ðŸ”§ ì„¤ì •"]
default_index = menu_list.index("ðŸ‘¥ ê±°ëž˜ì²˜ ê´€ë¦¬") if st.session_state.get('first_load', False) else 0

menu = st.sidebar.radio(
    "ë©”ë‰´ ì„ íƒ",
    menu_list,
    index=default_index
)

# ì²« ë¡œë“œ í›„ í”Œëž˜ê·¸ í•´ì œ
if st.session_state.get('first_load', False):
    st.session_state.first_load = False

# ==================== ëŒ€ì‹œë³´ë“œ ====================
if menu == "ðŸ  ëŒ€ì‹œë³´ë“œ":
    st.title("ðŸ“Š ëŒ€ì‹œë³´ë“œ")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("ì•„ì§ ê±°ëž˜ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤. 'ê±°ëž˜ ìž…ë ¥' ë©”ë‰´ì—ì„œ ë°ì´í„°ë¥¼ ì¶”ê°€í•´ì£¼ì„¸ìš”.")
    else:
        # ìµœê·¼ 4ê°œë…„ë„ë§Œ í‘œì‹œ
        ë‹¹í•´ì—°ë„ = get_kst_now().year
        ì—°ë„_ëª©ë¡ = [ë‹¹í•´ì—°ë„, ë‹¹í•´ì—°ë„-1, ë‹¹í•´ì—°ë„-2, ë‹¹í•´ì—°ë„-3]
        ì—°ë„_ë¼ë²¨ = [f"{ë‹¹í•´ì—°ë„}ë…„ (ë‹¹í•´)", f"{ë‹¹í•´ì—°ë„-1}ë…„", f"{ë‹¹í•´ì—°ë„-2}ë…„", f"{ë‹¹í•´ì—°ë„-3}ë…„"]
        
        # ì—°ë„ ì„ íƒ + ì›” ì„ íƒ
        col1, col2 = st.columns(2)
        with col1:
            ì„ íƒ_ì—°ë„_idx = st.selectbox("ì—°ë„ ì„ íƒ", range(len(ì—°ë„_ë¼ë²¨)), format_func=lambda i: ì—°ë„_ë¼ë²¨[i])
            ì„ íƒ_ì—°ë„ = ì—°ë„_ëª©ë¡[ì„ íƒ_ì—°ë„_idx]
        with col2:
            ì›”_ì˜µì…˜ = ["ì „ì²´"] + [f"{m}ì›”" for m in range(1, 13)]
            ì„ íƒ_ì›” = st.selectbox("ì›” ì„ íƒ", ì›”_ì˜µì…˜, index=get_kst_now().month if ì„ íƒ_ì—°ë„ == ë‹¹í•´ì—°ë„ else 0)
        
        # ë‚ ì§œ í•„í„°ë§
        df['ì—°ë„'] = df['ë‚ ì§œ'].dt.year
        df_filtered = df[df['ì—°ë„'] == ì„ íƒ_ì—°ë„].copy()
        
        if ì„ íƒ_ì›” != "ì „ì²´":
            ì›”_ìˆ«ìž = int(ì„ íƒ_ì›”.replace("ì›”", ""))
            df_filtered = df_filtered[df_filtered['ë‚ ì§œ'].dt.month == ì›”_ìˆ«ìž]
        
        # ì£¼ìš” ì§€í‘œ
        st.markdown(f"### ðŸ“ˆ {ì„ íƒ_ì—°ë„}ë…„ {ì„ íƒ_ì›”} ì£¼ìš” ì§€í‘œ")
        
        # ìˆ˜ìž…/ì§€ì¶œ ê³„ì‚°
        ìž…ê¸ˆ_df = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ', na=False)]
        ì¶œê¸ˆ_df = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ì¶œê¸ˆ', na=False)]
        ì™¸ìž…_df = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ì™¸ìž…', na=False)]
        ì™¸ì¶œ_df = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ì™¸ì¶œ', na=False)]
        
        ì´ìˆ˜ìž… = ìž…ê¸ˆ_df['ê³µê¸‰ê°€ì•¡'].sum()
        ì´ì§€ì¶œ = abs(ì¶œê¸ˆ_df['ê³µê¸‰ê°€ì•¡'].sum())
        # ì™¸ìž…ì€ ìŒìˆ˜ì´ë¯€ë¡œ ì ˆëŒ€ê°’ìœ¼ë¡œ ë§¤ìž…ê¸ˆì•¡ ê³„ì‚°
        ì´ë§¤ìž… = abs(ì™¸ìž…_df['ê³µê¸‰ê°€ì•¡'].sum())
        ì´ë§¤ìž…ë¶€ê°€ì„¸ = abs(ì™¸ìž…_df['ë¶€ê°€ì„¸'].sum())
        # ì™¸ì¶œ(íŒë§¤) ê¸ˆì•¡
        ì´ë§¤ì¶œ = ì™¸ì¶œ_df['ê³µê¸‰ê°€ì•¡'].sum() + ì™¸ì¶œ_df['ë¶€ê°€ì„¸'].sum()
        ìˆœì´ìµ = ì´ìˆ˜ìž… - ì´ì§€ì¶œ
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("ðŸ’° ì´ ìˆ˜ìž…", f"{ì´ìˆ˜ìž…:,.0f}ì›")
        with col2:
            st.metric("ðŸ’¸ ì´ ì§€ì¶œ", f"{ì´ì§€ì¶œ:,.0f}ì›")
        with col3:
            st.metric("ðŸ“¦ ì´ ë§¤ìž…", f"{ì´ë§¤ìž…:,.0f}ì›")
        with col4:
            st.metric("ðŸ’µ ìˆœì´ìµ", f"{ìˆœì´ìµ:,.0f}ì›", delta=f"{(ìˆœì´ìµ/ì´ìˆ˜ìž…*100):.1f}%" if ì´ìˆ˜ìž… > 0 else "0%")
        with col5:
            st.metric("ðŸ§¾ ì´ ë§¤ì¶œ", f"{ì´ë§¤ì¶œ:,.0f}ì›")
        
        st.markdown("---")
        
        # ì°¨íŠ¸
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ðŸ“… ì¼ë³„ ìˆ˜ìž…/ì§€ì¶œ ì¶”ì´")
            
            # ì¼ë³„ ì§‘ê³„
            ìž…ê¸ˆ_daily = ìž…ê¸ˆ_df.groupby(ìž…ê¸ˆ_df['ë‚ ì§œ'].dt.date)['ê³µê¸‰ê°€ì•¡'].sum().reset_index()
            ìž…ê¸ˆ_daily.columns = ['ë‚ ì§œ', 'ìˆ˜ìž…']
            
            ì¶œê¸ˆ_daily = ì¶œê¸ˆ_df.groupby(ì¶œê¸ˆ_df['ë‚ ì§œ'].dt.date)['ê³µê¸‰ê°€ì•¡'].sum().abs().reset_index()
            ì¶œê¸ˆ_daily.columns = ['ë‚ ì§œ', 'ì§€ì¶œ']
            
            # ë³‘í•©
            daily_df = pd.merge(ìž…ê¸ˆ_daily, ì¶œê¸ˆ_daily, on='ë‚ ì§œ', how='outer').fillna(0)
            
            if len(daily_df) > 0:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=daily_df['ë‚ ì§œ'], y=daily_df['ìˆ˜ìž…'], name='ìˆ˜ìž…', marker_color='#2E7D32'))
                fig.add_trace(go.Bar(x=daily_df['ë‚ ì§œ'], y=daily_df['ì§€ì¶œ'], name='ì§€ì¶œ', marker_color='#C62828'))
                fig.update_layout(barmode='group', height=400, hovermode='x unified')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("í•´ë‹¹ ê¸°ê°„ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
        
        with col2:
            st.markdown("### ðŸ¢ ì£¼ìš” ê±°ëž˜ì²˜ TOP 10")
            
            # ê±°ëž˜ì²˜ë³„ ì§‘ê³„
            ê±°ëž˜ì²˜_sum = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ', na=False)].groupby('ê±°ëž˜ì²˜')['ê³µê¸‰ê°€ì•¡'].sum().sort_values(ascending=False).head(10)
            
            if len(ê±°ëž˜ì²˜_sum) > 0:
                fig = px.bar(
                    x=ê±°ëž˜ì²˜_sum.values,
                    y=ê±°ëž˜ì²˜_sum.index,
                    orientation='h',
                    labels={'x': 'ê¸ˆì•¡ (ì›)', 'y': 'ê±°ëž˜ì²˜'},
                    color=ê±°ëž˜ì²˜_sum.values,
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("í•´ë‹¹ ê¸°ê°„ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
        
        # ì›”ë³„ í†µê³„
        st.markdown("### ðŸ“† ì›”ë³„ í†µê³„")
        
        df_filtered['ë…„ì›”'] = df_filtered['ë‚ ì§œ'].dt.to_period('M').astype(str)
        
        ì›”ë³„_ìž…ê¸ˆ = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ', na=False)].groupby('ë…„ì›”')['ê³µê¸‰ê°€ì•¡'].sum()
        ì›”ë³„_ì¶œê¸ˆ = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ì¶œê¸ˆ', na=False)].groupby('ë…„ì›”')['ê³µê¸‰ê°€ì•¡'].sum().abs()
        ì›”ë³„_ë§¤ìž… = df_filtered[df_filtered['ì°¸ì¡°'].str.contains('ì™¸ìž…', na=False)].groupby('ë…„ì›”')['ê³µê¸‰ê°€ì•¡'].sum().abs()
        
        ì›”ë³„_df = pd.DataFrame({
            'ìˆ˜ìž…': ì›”ë³„_ìž…ê¸ˆ,
            'ì§€ì¶œ': ì›”ë³„_ì¶œê¸ˆ,
            'ë§¤ìž…': ì›”ë³„_ë§¤ìž…,
            'ìˆœì´ìµ': ì›”ë³„_ìž…ê¸ˆ - ì›”ë³„_ì¶œê¸ˆ
        }).fillna(0)
        
        ì›”ë³„_df = ì›”ë³„_df.applymap(lambda x: f"{x:,.0f}")
        st.dataframe(ì›”ë³„_df, use_container_width=True)

# ==================== ê±°ëž˜ ìž…ë ¥ ====================
elif menu == "âž• ê±°ëž˜ ìž…ë ¥":
    st.title("âž• ê±°ëž˜ ìž…ë ¥")
    
    df = st.session_state.ledger_df
    products_df = st.session_state.products_df
    
    # ê¸°ì¡´ ê±°ëž˜ì²˜ ëª©ë¡
    ê±°ëž˜ì²˜_list = sorted(df['ê±°ëž˜ì²˜'].dropna().unique().tolist()) if len(df) > 0 else []
    
    # ========== ë‹¤ì¤‘ í’ˆëª© ìž…ë ¥ì„ ìœ„í•œ session_state ì´ˆê¸°í™” ==========
    if 'ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸' not in st.session_state:
        st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸ = []
    
    # ========== ìƒë‹¨: ê±°ëž˜ ê¸°ë³¸ ì •ë³´ ==========
    st.markdown("### ðŸ“‹ ê±°ëž˜ ê¸°ë³¸ ì •ë³´")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        ê±°ëž˜ì¼ìž = st.date_input("ê±°ëž˜ ë‚ ì§œ", value=get_kst_now())
    with col2:
        # ê±°ëž˜ì²˜ ìž…ë ¥
        ê±°ëž˜ì²˜_ìž…ë ¥ë°©ì‹ = st.radio("", ["ê¸°ì¡´ ê±°ëž˜ì²˜", "ìƒˆ ê±°ëž˜ì²˜"], horizontal=True, key="ê±°ëž˜ì²˜ë°©ì‹")
        if ê±°ëž˜ì²˜_ìž…ë ¥ë°©ì‹ == "ê¸°ì¡´ ê±°ëž˜ì²˜":
            ê±°ëž˜ì²˜ = st.selectbox("ê±°ëž˜ì²˜ ì„ íƒ", [""] + ê±°ëž˜ì²˜_list, key="ê±°ëž˜ì²˜ì„ íƒ")
        else:
            ê±°ëž˜ì²˜ = st.text_input("ê±°ëž˜ì²˜ëª… ìž…ë ¥", key="ê±°ëž˜ì²˜ìž…ë ¥")
    with col3:
        ê±°ëž˜ìœ í˜• = st.selectbox("ê±°ëž˜ ìœ í˜•", ["=ì™¸ì¶œ (íŒë§¤)", "=ìž…ê¸ˆ (ìˆ˜ê¸ˆ)", "=ì™¸ìž… (ë§¤ìž…)", "=ì¶œê¸ˆ (ê²°ì œ)"])
        ê±°ëž˜ìœ í˜•_ê°’ = ê±°ëž˜ìœ í˜•.split(" ")[0]
    
    # âœ… ì„ íƒëœ ê±°ëž˜ì²˜ í‘œì‹œ + ë¯¸ìˆ˜ê¸ˆ (ì‹œì¸ì„± ê°œì„  - ê²€ì •ìƒ‰ ê¸€ìž)
    if ê±°ëž˜ì²˜:
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"""
            <div style='background-color: #e3f2fd; border: 2px solid #1565c0; border-radius: 10px; padding: 15px;'>
                <h3 style='color: #000000; margin: 0; font-size: 20px;'>ðŸ¢ {ê±°ëž˜ì²˜}</h3>
            </div>
            """, unsafe_allow_html=True)
        with col_info2:
            ë¯¸ìˆ˜ê¸ˆ = calculate_receivable(ê±°ëž˜ì²˜)
            if ë¯¸ìˆ˜ê¸ˆ > 0:
                st.markdown(f"""
                <div style='background-color: #fff3e0; border: 2px solid #e65100; border-radius: 10px; padding: 15px;'>
                    <h3 style='color: #000000; margin: 0; font-size: 20px;'>âš ï¸ ë¯¸ìˆ˜ê¸ˆ: {ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›</h3>
                </div>
                """, unsafe_allow_html=True)
            elif ë¯¸ìˆ˜ê¸ˆ < 0:
                st.markdown(f"""
                <div style='background-color: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px; padding: 15px;'>
                    <h3 style='color: #000000; margin: 0; font-size: 20px;'>ðŸ’° ì„ ìˆ˜ê¸ˆ: {abs(ë¯¸ìˆ˜ê¸ˆ):,.0f}ì›</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px; padding: 15px;'>
                    <h3 style='color: #000000; margin: 0; font-size: 20px;'>âœ… ë¯¸ìˆ˜ê¸ˆ ì—†ìŒ</h3>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========== í’ˆëª© ìž…ë ¥ ì˜ì—­ ==========
    st.markdown("### ðŸ“¦ í’ˆëª© ì¶”ê°€")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # í’ˆëª© ìž…ë ¥ ë°©ì‹
        í’ˆëª©ìž…ë ¥ë°©ì‹ = st.radio("", ["í’ˆëª© ê²€ìƒ‰", "ì§ì ‘ ìž…ë ¥"], horizontal=True, key="í’ˆëª©ë°©ì‹")
        
        # ì„ íƒëœ í’ˆëª©ì˜ ìµœê·¼ ê°€ê²© ì •ë³´ ì €ìž¥ìš©
        if 'ì„ íƒí’ˆëª©_ìµœê·¼ë‹¨ê°€' not in st.session_state:
            st.session_state.ì„ íƒí’ˆëª©_ìµœê·¼ë‹¨ê°€ = 0
        
        if í’ˆëª©ìž…ë ¥ë°©ì‹ == "í’ˆëª© ê²€ìƒ‰":
            ê²€ìƒ‰ì–´ = st.text_input("í’ˆëª©ëª… ë˜ëŠ” ì½”ë“œ ê²€ìƒ‰", placeholder="ì˜ˆ: ì ˆë‹¨ì„, 001", key="í’ˆëª©ê²€ìƒ‰")
            
            if len(products_df) > 0 and ê²€ìƒ‰ì–´:
                if ê²€ìƒ‰ì–´.isdigit():
                    ê²€ìƒ‰ì½”ë“œ = f"P-{ê²€ìƒ‰ì–´.zfill(3)}"
                    ê²€ìƒ‰ê²°ê³¼ = products_df[products_df['í’ˆëª©ì½”ë“œ'].str.contains(ê²€ìƒ‰ì½”ë“œ, case=False, na=False)]
                else:
                    ê²€ìƒ‰ê²°ê³¼ = products_df[
                        products_df['í’ˆëª©ì½”ë“œ'].str.contains(ê²€ìƒ‰ì–´, case=False, na=False) |
                        products_df['í’ˆëª©ëª…'].str.contains(ê²€ìƒ‰ì–´, case=False, na=False)
                    ]
                
                if len(ê²€ìƒ‰ê²°ê³¼) > 0:
                    í’ˆëª©_ì˜µì…˜ = []
                    for _, row in ê²€ìƒ‰ê²°ê³¼.head(20).iterrows():
                        ì½”ë“œìˆ«ìž = row['í’ˆëª©ì½”ë“œ'].replace('P-', '')
                        ì˜µì…˜ = f"[{ì½”ë“œìˆ«ìž}] {row['í’ˆëª©ëª…']}"
                        if pd.notna(row.get('ê·œê²©', '')):
                            ì˜µì…˜ += f" @ {row['ê·œê²©']}"
                        í’ˆëª©_ì˜µì…˜.append((ì˜µì…˜, row))
                    
                    ì„ íƒidx = st.selectbox("ê²€ìƒ‰ ê²°ê³¼", range(len(í’ˆëª©_ì˜µì…˜)+1),
                                          format_func=lambda x: "ì„ íƒí•˜ì„¸ìš”" if x == 0 else í’ˆëª©_ì˜µì…˜[x-1][0],
                                          key="ê²€ìƒ‰ê²°ê³¼")
                    
                    if ì„ íƒidx > 0:
                        ì„ íƒí’ˆëª©ì •ë³´ = í’ˆëª©_ì˜µì…˜[ì„ íƒidx-1][1]
                        í’ˆëª©ëª… = f"{ì„ íƒí’ˆëª©ì •ë³´['í’ˆëª©ëª…']} @ {ì„ íƒí’ˆëª©ì •ë³´.get('ê·œê²©', '')}"
                        
                        # âœ… ì„ íƒëœ í’ˆëª© í‘œì‹œ (ì‹œì¸ì„± ê°œì„  - ê²€ì •ìƒ‰ ê¸€ìž)
                        st.markdown(f"""
                        <div style='background-color: #fff3e0; border: 2px solid #e65100; border-radius: 10px; padding: 12px; margin: 10px 0;'>
                            <h3 style='color: #000000; margin: 0; font-size: 18px;'>ðŸ“¦ {í’ˆëª©ëª…}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # âœ… ìµœê·¼ ê°€ê²© ì¡°íšŒ - í•´ë‹¹ ê±°ëž˜ì²˜ ê¸°ì¤€!
                        í’ˆëª©_ê²€ìƒ‰ëª… = ì„ íƒí’ˆëª©ì •ë³´['í’ˆëª©ëª…']
                        
                        st.markdown("#### ðŸ“Š ìµœê·¼ ê±°ëž˜ ê°€ê²©")
                        
                        # í•´ë‹¹ ê±°ëž˜ì²˜ì˜ ìµœê·¼ íŒë§¤/ë§¤ìž… ë‚´ì—­ë§Œ ì¡°íšŒ
                        if ê±°ëž˜ì²˜:
                            # í•´ë‹¹ ê±°ëž˜ì²˜ + í•´ë‹¹ í’ˆëª©ì˜ ìµœê·¼ íŒë§¤ ë‚´ì—­
                            íŒë§¤ë‚´ì—­ = df[
                                (df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜) &
                                (df['í’ˆëª©'].str.contains(í’ˆëª©_ê²€ìƒ‰ëª…, case=False, na=False)) &
                                (df['ì°¸ì¡°'] == '=ì™¸ì¶œ') &
                                (df['ê³µê¸‰ê°€ì•¡'] > 0)
                            ].sort_values('ë‚ ì§œ', ascending=False)
                            
                            # í•´ë‹¹ ê±°ëž˜ì²˜ + í•´ë‹¹ í’ˆëª©ì˜ ìµœê·¼ ë§¤ìž… ë‚´ì—­
                            ë§¤ìž…ë‚´ì—­ = df[
                                (df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜) &
                                (df['í’ˆëª©'].str.contains(í’ˆëª©_ê²€ìƒ‰ëª…, case=False, na=False)) &
                                (df['ì°¸ì¡°'] == '=ì™¸ìž…')
                            ].sort_values('ë‚ ì§œ', ascending=False)
                        else:
                            íŒë§¤ë‚´ì—­ = pd.DataFrame()
                            ë§¤ìž…ë‚´ì—­ = pd.DataFrame()
                        
                        col_price1, col_price2 = st.columns(2)
                        
                        with col_price1:
                            st.markdown(f"**ðŸ”µ {ê±°ëž˜ì²˜} ìµœê·¼ íŒë§¤**")
                            if len(íŒë§¤ë‚´ì—­) > 0:
                                ìµœê·¼ë‹¨ê°€ = 0
                                for _, row in íŒë§¤ë‚´ì—­.head(3).iterrows():
                                    ë‚ ì§œ_str = row['ë‚ ì§œ'].strftime('%m/%d') if pd.notna(row['ë‚ ì§œ']) else ''
                                    ë‹¨ê°€_ê°’ = abs(row['ë‹¨ê°€']) if row['ë‹¨ê°€'] != 0 else (abs(row['ê³µê¸‰ê°€ì•¡']) / row['ìˆ˜ëŸ‰'] if row['ìˆ˜ëŸ‰'] > 0 else 0)
                                    if ìµœê·¼ë‹¨ê°€ == 0 and ë‹¨ê°€_ê°’ > 0:
                                        ìµœê·¼ë‹¨ê°€ = int(ë‹¨ê°€_ê°’)
                                    st.markdown(f"""
                                    <div style='background-color: #e3f2fd; border-radius: 5px; padding: 8px; margin: 3px 0;'>
                                        <span style='color:#1565c0;'>ðŸ“… {ë‚ ì§œ_str}</span><br>
                                        <b style='color:#1565c0; font-size: 16px;'>ðŸ’µ ë‹¨ê°€: {ë‹¨ê°€_ê°’:,.0f}ì›</b>
                                    </div>
                                    """, unsafe_allow_html=True)
                                st.session_state.ì„ íƒí’ˆëª©_ìµœê·¼ë‹¨ê°€ = ìµœê·¼ë‹¨ê°€
                            else:
                                st.info(f"ðŸ“­ {ê±°ëž˜ì²˜} íŒë§¤ ì´ë ¥ ì—†ìŒ")
                                st.session_state.ì„ íƒí’ˆëª©_ìµœê·¼ë‹¨ê°€ = 0
                        
                        with col_price2:
                            st.markdown(f"**ðŸŸ  {ê±°ëž˜ì²˜} ìµœê·¼ ë§¤ìž…**")
                            if len(ë§¤ìž…ë‚´ì—­) > 0:
                                for _, row in ë§¤ìž…ë‚´ì—­.head(3).iterrows():
                                    ë‚ ì§œ_str = row['ë‚ ì§œ'].strftime('%m/%d') if pd.notna(row['ë‚ ì§œ']) else ''
                                    ë‹¨ê°€_ê°’ = abs(row['ë‹¨ê°€']) if row['ë‹¨ê°€'] != 0 else (abs(row['ê³µê¸‰ê°€ì•¡']) / abs(row['ìˆ˜ëŸ‰']) if row['ìˆ˜ëŸ‰'] != 0 else 0)
                                    st.markdown(f"""
                                    <div style='background-color: #fff3e0; border-radius: 5px; padding: 8px; margin: 3px 0;'>
                                        <span style='color:#e65100;'>ðŸ“… {ë‚ ì§œ_str}</span><br>
                                        <b style='color:#e65100; font-size: 16px;'>ðŸ’µ ë‹¨ê°€: {ë‹¨ê°€_ê°’:,.0f}ì›</b>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info(f"ðŸ“­ {ê±°ëž˜ì²˜} ë§¤ìž… ì´ë ¥ ì—†ìŒ")
                    else:
                        í’ˆëª©ëª… = ""
                        st.session_state.ì„ íƒí’ˆëª©_ìµœê·¼ë‹¨ê°€ = 0
                else:
                    st.warning("ê²€ìƒ‰ ê²°ê³¼ê°€ ì—†ìŠµë‹ˆë‹¤.")
                    í’ˆëª©ëª… = ""
            else:
                í’ˆëª©ëª… = ""
        else:
            í’ˆëª©ëª… = st.text_input("í’ˆëª©ëª… ì§ì ‘ ìž…ë ¥", key="í’ˆëª©ì§ì ‘")
    
    with col_right:
        ìž…ë ¥_ìˆ˜ëŸ‰ = st.number_input("ìˆ˜ëŸ‰", min_value=0, value=1, step=1, key="ìž…ë ¥ìˆ˜ëŸ‰")
        
        # ìµœê·¼ ë‹¨ê°€ê°€ ìžˆìœ¼ë©´ ê¸°ë³¸ê°’ìœ¼ë¡œ ì‚¬ìš©
        ê¸°ë³¸ë‹¨ê°€ = st.session_state.get('ì„ íƒí’ˆëª©_ìµœê·¼ë‹¨ê°€', 0)
        ìž…ë ¥_ë‹¨ê°€ = st.number_input("ë‹¨ê°€", min_value=0, value=ê¸°ë³¸ë‹¨ê°€, step=100, key="ìž…ë ¥ë‹¨ê°€")
        
        # ìµœê·¼ ë‹¨ê°€ ì°¸ê³  í‘œì‹œ
        if ê¸°ë³¸ë‹¨ê°€ > 0:
            st.caption(f"ðŸ’¡ ìµœê·¼ ê±°ëž˜ ë‹¨ê°€: {ê¸°ë³¸ë‹¨ê°€:,}ì›")
        
        # ê³µê¸‰ê°€ì•¡ ìžë™ ê³„ì‚°
        ìž…ë ¥_ê³µê¸‰ê°€ì•¡ = ìž…ë ¥_ìˆ˜ëŸ‰ * ìž…ë ¥_ë‹¨ê°€
        
        # ë¶€ê°€ì„¸
        if ê±°ëž˜ìœ í˜•_ê°’ in ["=ì™¸ì¶œ", "=ì™¸ìž…"]:
            ë¶€ê°€ì„¸_ì ìš© = st.checkbox("ë¶€ê°€ì„¸ 10%", value=True, key="ë¶€ê°€ì„¸ì ìš©")
            ìž…ë ¥_ë¶€ê°€ì„¸ = round(ìž…ë ¥_ê³µê¸‰ê°€ì•¡ * 0.1) if ë¶€ê°€ì„¸_ì ìš© else 0
        else:
            ìž…ë ¥_ë¶€ê°€ì„¸ = 0
        
        st.markdown(f"**ê³µê¸‰ê°€ì•¡:** {ìž…ë ¥_ê³µê¸‰ê°€ì•¡:,.0f}ì›")
        st.markdown(f"**ë¶€ê°€ì„¸:** {ìž…ë ¥_ë¶€ê°€ì„¸:,.0f}ì›")
        st.markdown(f"**í•©ê³„:** {ìž…ë ¥_ê³µê¸‰ê°€ì•¡ + ìž…ë ¥_ë¶€ê°€ì„¸:,.0f}ì›")
    
    # í’ˆëª© ì¶”ê°€ ë²„íŠ¼
    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.button("âž• í’ˆëª© ì¶”ê°€", type="primary", use_container_width=True):
            if í’ˆëª©ëª… and ìž…ë ¥_ê³µê¸‰ê°€ì•¡ > 0:
                ìƒˆí’ˆëª© = {
                    'í’ˆëª©': í’ˆëª©ëª…,
                    'ìˆ˜ëŸ‰': ìž…ë ¥_ìˆ˜ëŸ‰,
                    'ë‹¨ê°€': ìž…ë ¥_ë‹¨ê°€,
                    'ê³µê¸‰ê°€ì•¡': ìž…ë ¥_ê³µê¸‰ê°€ì•¡ if ê±°ëž˜ìœ í˜•_ê°’ != "=ì™¸ìž…" else -ìž…ë ¥_ê³µê¸‰ê°€ì•¡,
                    'ë¶€ê°€ì„¸': ìž…ë ¥_ë¶€ê°€ì„¸ if ê±°ëž˜ìœ í˜•_ê°’ != "=ì™¸ìž…" else -ìž…ë ¥_ë¶€ê°€ì„¸
                }
                st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸.append(ìƒˆí’ˆëª©)
                st.success(f"âœ… '{í’ˆëª©ëª…}' ì¶”ê°€ë¨!")
                st.rerun()
            else:
                st.error("âŒ í’ˆëª©ëª…ê³¼ ê¸ˆì•¡ì„ ìž…ë ¥í•´ì£¼ì„¸ìš”.")
    
    with col_btn2:
        if st.button("ðŸ—‘ï¸ ì „ì²´ ì‚­ì œ", use_container_width=True):
            st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸ = []
            st.rerun()
    
    st.markdown("---")
    
    # ========== ìž…ë ¥ëœ í’ˆëª© ëª©ë¡ ==========
    st.markdown("### ðŸ“‹ ìž…ë ¥ëœ í’ˆëª© ëª©ë¡")
    
    if len(st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸) > 0:
        # í•©ê³„ ê³„ì‚°
        ì´_ê³µê¸‰ê°€ì•¡ = sum(abs(item['ê³µê¸‰ê°€ì•¡']) for item in st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸)
        ì´_ë¶€ê°€ì„¸ = sum(abs(item['ë¶€ê°€ì„¸']) for item in st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸)
        ì´_í•©ê³„ = ì´_ê³µê¸‰ê°€ì•¡ + ì´_ë¶€ê°€ì„¸
        
        # ìš”ì•½ ì •ë³´
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        with col_sum1:
            st.metric("í’ˆëª© ìˆ˜", f"{len(st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸)}ê±´")
        with col_sum2:
            st.metric("ê³µê¸‰ê°€ì•¡", f"{ì´_ê³µê¸‰ê°€ì•¡:,.0f}ì›")
        with col_sum3:
            st.metric("ë¶€ê°€ì„¸", f"{ì´_ë¶€ê°€ì„¸:,.0f}ì›")
        with col_sum4:
            st.metric("ì´ í•©ê³„", f"{ì´_í•©ê³„:,.0f}ì›")
        
        st.markdown("---")
        
        # í’ˆëª© ëª©ë¡ í…Œì´ë¸”
        for i, item in enumerate(st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸):
            col_no, col_item, col_qty, col_price, col_amount, col_del = st.columns([0.5, 3, 1, 1, 1.5, 0.5])
            with col_no:
                st.markdown(f"**{i+1}**")
            with col_item:
                st.markdown(f"ðŸ“¦ {item['í’ˆëª©']}")
            with col_qty:
                st.markdown(f"{item['ìˆ˜ëŸ‰']:,}")
            with col_price:
                st.markdown(f"{item['ë‹¨ê°€']:,}")
            with col_amount:
                st.markdown(f"**{abs(item['ê³µê¸‰ê°€ì•¡']) + abs(item['ë¶€ê°€ì„¸']):,.0f}ì›**")
            with col_del:
                if st.button("âŒ", key=f"del_{i}"):
                    st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸.pop(i)
                    st.rerun()
        
        st.markdown("---")
        
        # ========== ì €ìž¥ ë²„íŠ¼ ==========
        col_save1, col_save2, col_save3 = st.columns([1, 1, 1])
        
        with col_save1:
            ì €ìž¥_ë²„íŠ¼ = st.button("ðŸ’¾ ì¼ê´„ ì €ìž¥", type="primary", use_container_width=True)
        with col_save2:
            ì €ìž¥_ëª…ì„¸ì„œ_ë²„íŠ¼ = st.button("ðŸ’¾ ì €ìž¥ + ðŸ“„ ëª…ì„¸ì„œ", use_container_width=True)
        with col_save3:
            ëª…ì„¸ì„œë§Œ_ë²„íŠ¼ = st.button("ðŸ“„ ëª…ì„¸ì„œë§Œ ì¶œë ¥", use_container_width=True)
        
        # ì €ìž¥ ì²˜ë¦¬
        if ì €ìž¥_ë²„íŠ¼ or ì €ìž¥_ëª…ì„¸ì„œ_ë²„íŠ¼:
            if not ê±°ëž˜ì²˜:
                st.error("âŒ ê±°ëž˜ì²˜ë¥¼ ì„ íƒí•´ì£¼ì„¸ìš”.")
            else:
                # ëª¨ë“  í’ˆëª© ì €ìž¥
                for item in st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸:
                    new_row = pd.DataFrame([{
                        'ë‚ ì§œ': pd.to_datetime(ê±°ëž˜ì¼ìž),
                        'ê±°ëž˜ì²˜': ê±°ëž˜ì²˜,
                        'í’ˆëª©': item['í’ˆëª©'],
                        'ìˆ˜ëŸ‰': item['ìˆ˜ëŸ‰'],
                        'ë‹¨ê°€': item['ë‹¨ê°€'],
                        'ê³µê¸‰ê°€ì•¡': item['ê³µê¸‰ê°€ì•¡'],
                        'ë¶€ê°€ì„¸': item['ë¶€ê°€ì„¸'],
                        'ì°¸ì¡°': ê±°ëž˜ìœ í˜•_ê°’,
                        'ë¹„ê³ ': ''
                    }])
                    st.session_state.ledger_df = pd.concat([st.session_state.ledger_df, new_row], ignore_index=True)
                
                save_data()
                st.success(f"âœ… {len(st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸)}ê±´ ê±°ëž˜ê°€ ì €ìž¥ë˜ì—ˆìŠµë‹ˆë‹¤!")
                
                # ëª…ì„¸ì„œ ì¶œë ¥
                if ì €ìž¥_ëª…ì„¸ì„œ_ë²„íŠ¼:
                    html_content = create_invoice_html(ê±°ëž˜ì²˜, ê±°ëž˜ì¼ìž.strftime('%Y-%m-%d'), st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸)
                    st.download_button(
                        label="ðŸ“„ ê±°ëž˜ëª…ì„¸ì„œ ë‹¤ìš´ë¡œë“œ (HTML)",
                        data=html_content.encode('utf-8'),
                        file_name=f"ê±°ëž˜ëª…ì„¸ì„œ_{ê±°ëž˜ì²˜}_{ê±°ëž˜ì¼ìž.strftime('%Y%m%d')}.html",
                        mime="text/html; charset=utf-8"
                    )
                    st.info("ðŸ’¡ ë‹¤ìš´ë¡œë“œ í›„ ë¸Œë¼ìš°ì €ì—ì„œ ì—´ì–´ Ctrl+Pë¡œ ì¸ì‡„í•˜ì„¸ìš”!")
                
                # ë¦¬ìŠ¤íŠ¸ ì´ˆê¸°í™”
                st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸ = []
                
                if not ì €ìž¥_ëª…ì„¸ì„œ_ë²„íŠ¼:
                    st.balloons()
                    st.rerun()
        
        # ëª…ì„¸ì„œë§Œ ì¶œë ¥
        if ëª…ì„¸ì„œë§Œ_ë²„íŠ¼:
            if not ê±°ëž˜ì²˜:
                st.error("âŒ ê±°ëž˜ì²˜ë¥¼ ì„ íƒí•´ì£¼ì„¸ìš”.")
            else:
                html_content = create_invoice_html(ê±°ëž˜ì²˜, ê±°ëž˜ì¼ìž.strftime('%Y-%m-%d'), st.session_state.ìž…ë ¥ì¤‘_í’ˆëª©_ë¦¬ìŠ¤íŠ¸)
                st.download_button(
                    label="ðŸ“„ ê±°ëž˜ëª…ì„¸ì„œ ë‹¤ìš´ë¡œë“œ (HTML)",
                    data=html_content.encode('utf-8'),
                    file_name=f"ê±°ëž˜ëª…ì„¸ì„œ_{ê±°ëž˜ì²˜}_{ê±°ëž˜ì¼ìž.strftime('%Y%m%d')}.html",
                    mime="text/html; charset=utf-8"
                )
                st.info("ðŸ’¡ ë‹¤ìš´ë¡œë“œ í›„ ë¸Œë¼ìš°ì €ì—ì„œ ì—´ì–´ Ctrl+Pë¡œ ì¸ì‡„í•˜ì„¸ìš”!")
    else:
        st.info("ðŸ“ ìœ„ì—ì„œ í’ˆëª©ì„ ì¶”ê°€í•´ì£¼ì„¸ìš”. ì—¬ëŸ¬ í’ˆëª©ì„ ì¶”ê°€í•œ í›„ ì¼ê´„ ì €ìž¥í•  ìˆ˜ ìžˆìŠµë‹ˆë‹¤.")

# ==================== ê±°ëž˜ ë‚´ì—­ ====================
elif menu == "ðŸ“„ ê±°ëž˜ ë‚´ì—­":
    st.title("ðŸ“„ ê±°ëž˜ ë‚´ì—­")
    
    df = st.session_state.ledger_df.copy()
    products_df = st.session_state.products_df
    
    # ===== ë¹ ë¥¸ ìž…ë ¥ (ì»´ìž¥ë¶€ ìŠ¤íƒ€ì¼) =====
    with st.expander("âž• ë¹ ë¥¸ ê±°ëž˜ ìž…ë ¥", expanded=False):
        st.markdown("##### ì»´ìž¥ë¶€ì²˜ëŸ¼ ë¹ ë¥´ê²Œ ìž…ë ¥í•˜ì„¸ìš”!")
        
        # ê¸°ì¡´ ê±°ëž˜ì²˜ ëª©ë¡
        ê±°ëž˜ì²˜_list = sorted(df['ê±°ëž˜ì²˜'].dropna().unique().tolist()) if len(df) > 0 else []
        
        # ê¸°ì¡´ í’ˆëª© ëª©ë¡ (ledgerì—ì„œ ì¶”ì¶œ)
        í’ˆëª©_list = sorted(df['í’ˆëª©'].dropna().unique().tolist()) if len(df) > 0 else []
        
        # 1ì¤„: ë‚ ì§œ, ê±°ëž˜ì²˜, ê±°ëž˜ìœ í˜•
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            ìž…ë ¥_ë‚ ì§œ = st.date_input("ë‚ ì§œ", value=get_kst_now(), key="quick_date")
        with col2:
            ìž…ë ¥_ê±°ëž˜ì²˜ = st.selectbox("ê±°ëž˜ì²˜", [""] + ê±°ëž˜ì²˜_list, key="quick_customer")
        with col3:
            # ê±°ëž˜ ìœ í˜• (ì™¸ì¶œì´ ê¸°ë³¸ - íŒë§¤ê°€ ë” ë§ŽìŒ)
            ìž…ë ¥_ê±°ëž˜ìœ í˜• = st.selectbox(
                "ìœ í˜•", 
                ["=ì™¸ì¶œ (íŒë§¤)", "=ìž…ê¸ˆ (ìˆ˜ê¸ˆ)", "=ì™¸ìž… (ë§¤ìž…)", "=ì¶œê¸ˆ (ê²°ì œ)"], 
                key="quick_type"
            )
            # ì‹¤ì œ ì €ìž¥í•  ê°’ ì¶”ì¶œ
            ìž…ë ¥_ê±°ëž˜ìœ í˜•_ê°’ = ìž…ë ¥_ê±°ëž˜ìœ í˜•.split(" ")[0]
        
        # 2ì¤„: í’ˆëª©(ìžë™ì™„ì„±), ìˆ˜ëŸ‰, ë‹¨ê°€, ê³µê¸‰ê°€ì•¡(ìžë™ê³„ì‚°)
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            # í’ˆëª© ìžë™ì™„ì„± - selectbox + ê²€ìƒ‰ ê¸°ëŠ¥
            í’ˆëª©_ê²€ìƒ‰ì–´ = st.text_input("í’ˆëª© ê²€ìƒ‰ (2ê¸€ìž ì´ìƒ)", key="quick_product_search", placeholder="í’ˆëª©ëª… ìž…ë ¥...")
            
            # 2ê¸€ìž ì´ìƒ ìž…ë ¥ì‹œ í•„í„°ë§ëœ í’ˆëª© í‘œì‹œ
            if len(í’ˆëª©_ê²€ìƒ‰ì–´) >= 2:
                í•„í„°_í’ˆëª© = [p for p in í’ˆëª©_list if í’ˆëª©_ê²€ìƒ‰ì–´.lower() in p.lower()]
                if í•„í„°_í’ˆëª©:
                    ìž…ë ¥_í’ˆëª© = st.selectbox(
                        f"ðŸ” ê²€ìƒ‰ê²°ê³¼ ({len(í•„í„°_í’ˆëª©)}ê±´)", 
                        ["ì§ì ‘ìž…ë ¥: " + í’ˆëª©_ê²€ìƒ‰ì–´] + í•„í„°_í’ˆëª©[:20],  # ìµœëŒ€ 20ê°œ
                        key="quick_product_select"
                    )
                    # "ì§ì ‘ìž…ë ¥:" ì„ íƒì‹œ ê²€ìƒ‰ì–´ ê·¸ëŒ€ë¡œ ì‚¬ìš©
                    if ìž…ë ¥_í’ˆëª©.startswith("ì§ì ‘ìž…ë ¥:"):
                        ìž…ë ¥_í’ˆëª© = í’ˆëª©_ê²€ìƒ‰ì–´
                else:
                    ìž…ë ¥_í’ˆëª© = í’ˆëª©_ê²€ìƒ‰ì–´
                    st.caption("ê²€ìƒ‰ ê²°ê³¼ ì—†ìŒ - ì§ì ‘ ìž…ë ¥ë©ë‹ˆë‹¤")
            else:
                ìž…ë ¥_í’ˆëª© = í’ˆëª©_ê²€ìƒ‰ì–´
                if í’ˆëª©_ê²€ìƒ‰ì–´:
                    st.caption("2ê¸€ìž ì´ìƒ ìž…ë ¥í•˜ë©´ í’ˆëª© ê²€ìƒ‰")
        
        with col2:
            ìž…ë ¥_ìˆ˜ëŸ‰ = st.number_input("ìˆ˜ëŸ‰", min_value=0, value=0, step=1, format="%d", key="quick_qty")
        with col3:
            ìž…ë ¥_ë‹¨ê°€ = st.number_input("ë‹¨ê°€", min_value=0, value=0, step=100, format="%d", key="quick_price")
        with col4:
            # ê³µê¸‰ê°€ì•¡ ìžë™ ê³„ì‚° (ìˆ˜ì • ë¶ˆê°€)
            ìžë™_ê³µê¸‰ê°€ì•¡ = ìž…ë ¥_ìˆ˜ëŸ‰ * ìž…ë ¥_ë‹¨ê°€
            st.text_input("ê³µê¸‰ê°€ì•¡", value=f"{ìžë™_ê³µê¸‰ê°€ì•¡:,}", disabled=True, key="quick_amount_display")
            ìž…ë ¥_ê³µê¸‰ê°€ì•¡ = ìžë™_ê³µê¸‰ê°€ì•¡
        
        # ë¶€ê°€ì„¸ ë° ì €ìž¥
        col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
        with col1:
            ë¶€ê°€ì„¸_ì ìš© = st.checkbox("ë¶€ê°€ì„¸ 10%", value=True if ìž…ë ¥_ê±°ëž˜ìœ í˜•_ê°’ in ["=ì™¸ì¶œ", "=ì™¸ìž…"] else False, key="quick_tax")
            ìž…ë ¥_ë¶€ê°€ì„¸ = round(ìž…ë ¥_ê³µê¸‰ê°€ì•¡ * 0.1) if ë¶€ê°€ì„¸_ì ìš© else 0
        with col2:
            st.metric("í•©ê³„", f"{ìž…ë ¥_ê³µê¸‰ê°€ì•¡ + ìž…ë ¥_ë¶€ê°€ì„¸:,.0f}ì›")
        with col3:
            ìž…ë ¥_ë¹„ê³  = st.text_input("ðŸ“ ë¹„ê³ ", key="quick_memo", placeholder="íŠ¹ì´ì‚¬í•­")
        with col4:
            if st.button("ðŸ’¾ ì €ìž¥", type="primary", use_container_width=True, key="quick_save"):
                if not ìž…ë ¥_ê±°ëž˜ì²˜:
                    st.error("âŒ ê±°ëž˜ì²˜ë¥¼ ì„ íƒí•´ì£¼ì„¸ìš”.")
                else:
                    new_row = pd.DataFrame([{
                        'ë‚ ì§œ': pd.to_datetime(ìž…ë ¥_ë‚ ì§œ),
                        'ê±°ëž˜ì²˜': ìž…ë ¥_ê±°ëž˜ì²˜,
                        'í’ˆëª©': ìž…ë ¥_í’ˆëª© if ìž…ë ¥_í’ˆëª© else ìž…ë ¥_ê±°ëž˜ìœ í˜•_ê°’.replace("=", ""),
                        'ìˆ˜ëŸ‰': ìž…ë ¥_ìˆ˜ëŸ‰,
                        'ë‹¨ê°€': ìž…ë ¥_ë‹¨ê°€,
                        'ê³µê¸‰ê°€ì•¡': ìž…ë ¥_ê³µê¸‰ê°€ì•¡,
                        'ë¶€ê°€ì„¸': ìž…ë ¥_ë¶€ê°€ì„¸,
                        'ì°¸ì¡°': ìž…ë ¥_ê±°ëž˜ìœ í˜•_ê°’,
                        'ë¹„ê³ ': ìž…ë ¥_ë¹„ê³ 
                    }])
                    
                    st.session_state.ledger_df = pd.concat([st.session_state.ledger_df, new_row], ignore_index=True)
                    save_data()
                    st.success(f"âœ… ì €ìž¥ ì™„ë£Œ! {ìž…ë ¥_ê±°ëž˜ì²˜} - {ìž…ë ¥_ê³µê¸‰ê°€ì•¡ + ìž…ë ¥_ë¶€ê°€ì„¸:,.0f}ì›")
                    st.rerun()
    
    st.markdown("---")
    
    if len(df) == 0:
        st.info("ì•„ì§ ê±°ëž˜ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
    else:
        # í•„í„°
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ê±°ëž˜ìœ í˜•_í•„í„° = st.multiselect("ê±°ëž˜ ìœ í˜•", df['ì°¸ì¡°'].unique(), default=df['ì°¸ì¡°'].unique())
        with col2:
            ê±°ëž˜ì²˜_í•„í„° = st.multiselect("ê±°ëž˜ì²˜", ["ì „ì²´"] + sorted(df['ê±°ëž˜ì²˜'].dropna().unique().tolist()), default=["ì „ì²´"])
        with col3:
            ê²€ìƒ‰ì–´ = st.text_input("í’ˆëª© ê²€ìƒ‰", "")
        
        # ë¯¸ìˆ˜ê¸ˆ ì‹¤ì‹œê°„ í‘œì‹œ - base_receivablesì—ì„œ GULREST ê°’ ì§ì ‘ ì‚¬ìš©
        if "ì „ì²´" not in ê±°ëž˜ì²˜_í•„í„° and len(ê±°ëž˜ì²˜_í•„í„°) == 1:
            ì„ íƒê±°ëž˜ì²˜ = ê±°ëž˜ì²˜_í•„í„°[0]
            
            # ë¯¸ìˆ˜ê¸ˆì€ base_receivablesì—ì„œ ì§ì ‘ ê°€ì ¸ì˜´ (ì»´ìž¥ë¶€ GULREST)
            ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict = st.session_state.base_receivables_df.set_index('ê±°ëž˜ì²˜')['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].to_dict() if len(st.session_state.base_receivables_df) > 0 else {}
            ë¯¸ìˆ˜ê¸ˆ = ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict.get(ì„ íƒê±°ëž˜ì²˜, 0)
            
            # ë¯¸ìˆ˜ê¸ˆ í‘œì‹œ (ê²€ì •ìƒ‰ ê¸€ìž)
            if ë¯¸ìˆ˜ê¸ˆ > 0:
                st.markdown(f"""
                <div style='background-color: #fff3e0; border: 2px solid #e65100; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #000000; margin: 0;'>âš ï¸ ë¯¸ìˆ˜ê¸ˆ: {ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›</h3>
                </div>
                """, unsafe_allow_html=True)
            elif ë¯¸ìˆ˜ê¸ˆ < 0:
                st.markdown(f"""
                <div style='background-color: #e3f2fd; border: 2px solid #1e88e5; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #000000; margin: 0;'>ðŸ’° ì„ ìˆ˜ê¸ˆ: {abs(ë¯¸ìˆ˜ê¸ˆ):,.0f}ì›</h3>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px; padding: 15px; margin: 10px 0;'>
                    <h3 style='color: #000000; margin: 0;'>âœ… ë¯¸ìˆ˜ê¸ˆ ì—†ìŒ</h3>
                </div>
                """, unsafe_allow_html=True)
        
        # í•„í„°ë§
        df_filtered = df[df['ì°¸ì¡°'].isin(ê±°ëž˜ìœ í˜•_í•„í„°)]
        
        if "ì „ì²´" not in ê±°ëž˜ì²˜_í•„í„°:
            df_filtered = df_filtered[df_filtered['ê±°ëž˜ì²˜'].isin(ê±°ëž˜ì²˜_í•„í„°)]
        
        if ê²€ìƒ‰ì–´:
            df_filtered = df_filtered[df_filtered['í’ˆëª©'].str.contains(ê²€ìƒ‰ì–´, na=False)]
        
        # ì •ë ¬
        df_filtered = df_filtered.sort_values('ë‚ ì§œ', ascending=False)
        
        st.markdown(f"### ì´ {len(df_filtered)}ê±´")
        
        # ë¯¸ìˆ˜ê¸ˆ ê³„ì‚° í•¨ìˆ˜ - base_receivablesì—ì„œ GULREST ê°’ ì‚¬ìš©
        def ê±°ëž˜ì²˜ë³„_ë¯¸ìˆ˜ê¸ˆ_ê³„ì‚°(ê±°ëž˜ì²˜ëª…):
            """ê±°ëž˜ì²˜ë³„ í˜„ìž¬ ë¯¸ìˆ˜ê¸ˆ = ì»´ìž¥ë¶€ GULREST ê°’"""
            ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict = st.session_state.base_receivables_df.set_index('ê±°ëž˜ì²˜')['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].to_dict() if len(st.session_state.base_receivables_df) > 0 else {}
            return ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict.get(ê±°ëž˜ì²˜ëª…, 0)
        
        # ë°ì´í„° í‘œì‹œ
        display_df = df_filtered.copy()
        display_df['ë‚ ì§œ'] = display_df['ë‚ ì§œ'].dt.strftime('%Y-%m-%d')
        
        # ë¯¸ìˆ˜ê¸ˆ ì»¬ëŸ¼ ì¶”ê°€ (ê±°ëž˜ì²˜ë³„ í˜„ìž¬ ë¯¸ìˆ˜ê¸ˆ)
        display_df['ë¯¸ìˆ˜ê¸ˆ'] = display_df['ê±°ëž˜ì²˜'].apply(ê±°ëž˜ì²˜ë³„_ë¯¸ìˆ˜ê¸ˆ_ê³„ì‚°)
        display_df['ë¯¸ìˆ˜ê¸ˆ'] = display_df['ë¯¸ìˆ˜ê¸ˆ'].apply(lambda x: f"{x:,.0f}" if x != 0 else "")
        
        display_df['ê³µê¸‰ê°€ì•¡'] = display_df['ê³µê¸‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}")
        display_df['ë¶€ê°€ì„¸'] = display_df['ë¶€ê°€ì„¸'].apply(lambda x: f"{x:,.0f}")
        
        # ë¹„ê³  ì»¬ëŸ¼ì´ ì—†ìœ¼ë©´ ì¶”ê°€
        if 'ë¹„ê³ ' not in display_df.columns:
            display_df['ë¹„ê³ '] = ''
        
        # ì»¬ëŸ¼ ìˆœì„œ ì •ë¦¬
        í‘œì‹œ_ì»¬ëŸ¼ = ['ë‚ ì§œ', 'ê±°ëž˜ì²˜', 'í’ˆëª©', 'ìˆ˜ëŸ‰', 'ë‹¨ê°€', 'ê³µê¸‰ê°€ì•¡', 'ë¶€ê°€ì„¸', 'ì°¸ì¡°', 'ë¯¸ìˆ˜ê¸ˆ', 'ë¹„ê³ ']
        í‘œì‹œ_ì»¬ëŸ¼ = [col for col in í‘œì‹œ_ì»¬ëŸ¼ if col in display_df.columns]
        display_df = display_df[í‘œì‹œ_ì»¬ëŸ¼]
        
        st.dataframe(display_df, use_container_width=True, height=500)
        
        # ðŸ—‘ï¸ ê±°ëž˜ ì‚­ì œ ê¸°ëŠ¥
        st.markdown("---")
        with st.expander("ðŸ—‘ï¸ ê±°ëž˜ ì‚­ì œ", expanded=False):
            st.warning("âš ï¸ ì‚­ì œëœ ê±°ëž˜ëŠ” ë³µêµ¬í•  ìˆ˜ ì—†ìŠµë‹ˆë‹¤!")
            
            # ìµœê·¼ ê±°ëž˜ ëª©ë¡ (ì‚­ì œìš©)
            ìµœê·¼_ê±°ëž˜ = df_filtered.head(20).copy()
            ìµœê·¼_ê±°ëž˜['ì‚­ì œìš©_í‘œì‹œ'] = ìµœê·¼_ê±°ëž˜.apply(
                lambda x: f"{x['ë‚ ì§œ'].strftime('%Y-%m-%d') if isinstance(x['ë‚ ì§œ'], pd.Timestamp) else x['ë‚ ì§œ']} | {x['ê±°ëž˜ì²˜']} | {x['í’ˆëª©'][:20] if pd.notna(x['í’ˆëª©']) else ''} | {x['ê³µê¸‰ê°€ì•¡']}", 
                axis=1
            )
            
            ì‚­ì œ_ì„ íƒ = st.selectbox(
                "ì‚­ì œí•  ê±°ëž˜ ì„ íƒ (ìµœê·¼ 20ê±´)",
                ["ì„ íƒí•˜ì„¸ìš”"] + ìµœê·¼_ê±°ëž˜['ì‚­ì œìš©_í‘œì‹œ'].tolist(),
                key="delete_select"
            )
            
            if ì‚­ì œ_ì„ íƒ != "ì„ íƒí•˜ì„¸ìš”":
                # ì„ íƒëœ ê±°ëž˜ì˜ ì¸ë±ìŠ¤ ì°¾ê¸°
                ì„ íƒ_idx = ìµœê·¼_ê±°ëž˜[ìµœê·¼_ê±°ëž˜['ì‚­ì œìš©_í‘œì‹œ'] == ì‚­ì œ_ì„ íƒ].index[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    ì‚­ì œ_í™•ì¸ = st.checkbox("ì •ë§ ì‚­ì œí•˜ì‹œê² ìŠµë‹ˆê¹Œ?", key="delete_confirm")
                with col2:
                    if ì‚­ì œ_í™•ì¸:
                        if st.button("ðŸ—‘ï¸ ì‚­ì œ ì‹¤í–‰", type="primary", use_container_width=True):
                            st.session_state.ledger_df = st.session_state.ledger_df.drop(ì„ íƒ_idx).reset_index(drop=True)
                            save_data()
                            st.success("âœ… ì‚­ì œ ì™„ë£Œ!")
                            st.rerun()
        
        # ê±°ëž˜ëª…ì„¸ì„œ ì¶œë ¥ (ê±°ëž˜ì²˜ 1ê°œ ì„ íƒ ì‹œ)
        st.markdown("---")
        
        if "ì „ì²´" not in ê±°ëž˜ì²˜_í•„í„° and len(ê±°ëž˜ì²˜_í•„í„°) == 1:
            ì„ íƒê±°ëž˜ì²˜_ëª…ì„¸ = ê±°ëž˜ì²˜_í•„í„°[0]
            
            st.markdown("#### ðŸ“„ ê±°ëž˜ëª…ì„¸ì„œ ì¶œë ¥")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                ëª…ì„¸ì„œ_ì‹œìž‘ì¼ = st.date_input("ì‹œìž‘ì¼", value=get_kst_now().replace(day=1), key="invoice_start")
            with col2:
                ëª…ì„¸ì„œ_ì¢…ë£Œì¼ = st.date_input("ì¢…ë£Œì¼", value=get_kst_now(), key="invoice_end")
            with col3:
                ëª…ì„¸ì„œ_ì¶œë ¥ = st.button("ðŸ“„ ê±°ëž˜ëª…ì„¸ì„œ ìƒì„±", type="primary", use_container_width=True)
            
            if ëª…ì„¸ì„œ_ì¶œë ¥:
                # í•´ë‹¹ ê¸°ê°„ + ê±°ëž˜ì²˜ + íŒë§¤(ì™¸ì¶œ)ë§Œ í•„í„°
                ëª…ì„¸_df = df_filtered[
                    (df_filtered['ì°¸ì¡°'] == '=ì™¸ì¶œ')
                ].copy()
                
                # ë‚ ì§œ í•„í„° (ì›ë³¸ df_filtered ì‚¬ìš©)
                ì›ë³¸_df = st.session_state.ledger_df.copy()
                ì›ë³¸_df = ì›ë³¸_df[
                    (ì›ë³¸_df['ê±°ëž˜ì²˜'] == ì„ íƒê±°ëž˜ì²˜_ëª…ì„¸) &
                    (ì›ë³¸_df['ì°¸ì¡°'] == '=ì™¸ì¶œ') &
                    (ì›ë³¸_df['ë‚ ì§œ'] >= pd.to_datetime(ëª…ì„¸ì„œ_ì‹œìž‘ì¼)) &
                    (ì›ë³¸_df['ë‚ ì§œ'] <= pd.to_datetime(ëª…ì„¸ì„œ_ì¢…ë£Œì¼))
                ]
                
                if len(ì›ë³¸_df) > 0:
                    ê±°ëž˜_ëª©ë¡ = []
                    for _, row in ì›ë³¸_df.iterrows():
                        ê±°ëž˜_ëª©ë¡.append({
                            'í’ˆëª©': row['í’ˆëª©'],
                            'ìˆ˜ëŸ‰': row['ìˆ˜ëŸ‰'],
                            'ë‹¨ê°€': row['ë‹¨ê°€'],
                            'ê³µê¸‰ê°€ì•¡': row['ê³µê¸‰ê°€ì•¡'],
                            'ë¶€ê°€ì„¸': row['ë¶€ê°€ì„¸']
                        })
                    
                    ë‚ ì§œ_ë¬¸ìžì—´ = f"{ëª…ì„¸ì„œ_ì‹œìž‘ì¼.strftime('%Y-%m-%d')} ~ {ëª…ì„¸ì„œ_ì¢…ë£Œì¼.strftime('%Y-%m-%d')}"
                    html_content = create_invoice_html(ì„ íƒê±°ëž˜ì²˜_ëª…ì„¸, ë‚ ì§œ_ë¬¸ìžì—´, ê±°ëž˜_ëª©ë¡)
                    
                    st.download_button(
                        label="ðŸ“¥ ê±°ëž˜ëª…ì„¸ì„œ ë‹¤ìš´ë¡œë“œ (HTML)",
                        data=html_content.encode('utf-8'),
                        file_name=f"ê±°ëž˜ëª…ì„¸ì„œ_{ì„ íƒê±°ëž˜ì²˜_ëª…ì„¸}_{ëª…ì„¸ì„œ_ì‹œìž‘ì¼.strftime('%Y%m%d')}_{ëª…ì„¸ì„œ_ì¢…ë£Œì¼.strftime('%Y%m%d')}.html",
                        mime="text/html; charset=utf-8"
                    )
                    st.success(f"âœ… {ì„ íƒê±°ëž˜ì²˜_ëª…ì„¸} ê±°ëž˜ëª…ì„¸ì„œ ìƒì„± ì™„ë£Œ! ({len(ì›ë³¸_df)}ê±´)")
                    st.info("ðŸ’¡ ë‹¤ìš´ë¡œë“œ í›„ ë¸Œë¼ìš°ì €ì—ì„œ ì—´ì–´ Ctrl+Pë¡œ ì¸ì‡„í•˜ì„¸ìš”!")
                else:
                    st.warning("í•´ë‹¹ ê¸°ê°„ì— íŒë§¤ ê±°ëž˜ê°€ ì—†ìŠµë‹ˆë‹¤.")
        
        # ì—‘ì…€ ë‹¤ìš´ë¡œë“œ
        st.markdown("---")
        
        @st.cache_data
        def convert_to_excel(dataframe):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                dataframe.to_excel(writer, index=False, sheet_name='ê±°ëž˜ë‚´ì—­')
            return output.getvalue()
        
        excel_data = convert_to_excel(df_filtered)
        
        st.download_button(
            label="ðŸ“¥ ì—‘ì…€ ë‹¤ìš´ë¡œë“œ",
            data=excel_data,
            file_name=f"ê±°ëž˜ë‚´ì—­_{get_kst_now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ==================== í†µê³„ ë¶„ì„ ====================
elif menu == "ðŸ“Š í†µê³„ ë¶„ì„":
    st.title("ðŸ“Š í†µê³„ ë¶„ì„")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("ì•„ì§ ê±°ëž˜ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
    else:
        # ìµœê·¼ 4ê°œë…„ë„ í•„í„°
        ë‹¹í•´ì—°ë„ = get_kst_now().year
        ì—°ë„_ëª©ë¡ = [ë‹¹í•´ì—°ë„, ë‹¹í•´ì—°ë„-1, ë‹¹í•´ì—°ë„-2, ë‹¹í•´ì—°ë„-3]
        
        col1, col2 = st.columns(2)
        with col1:
            ë¶„ì„ìœ í˜• = st.selectbox("ë¶„ì„ ìœ í˜•", ["ì›”ë³„ ë¶„ì„", "ê±°ëž˜ì²˜ë³„ ë¶„ì„", "í’ˆëª©ë³„ ë¶„ì„", "ë¶€ê°€ì„¸ ë¶„ì„"])
        with col2:
            ì„ íƒ_ì—°ë„ = st.selectbox("ì—°ë„ ì„ íƒ", ["ì „ì²´ (ìµœê·¼4ë…„)"] + [f"{y}ë…„" for y in ì—°ë„_ëª©ë¡])
        
        # ì—°ë„ í•„í„°ë§
        df['ì—°ë„'] = df['ë‚ ì§œ'].dt.year
        if ì„ íƒ_ì—°ë„ == "ì „ì²´ (ìµœê·¼4ë…„)":
            df = df[df['ì—°ë„'].isin(ì—°ë„_ëª©ë¡)]
        else:
            ì„ íƒ_ì—°ë„_ìˆ«ìž = int(ì„ íƒ_ì—°ë„.replace("ë…„", ""))
            df = df[df['ì—°ë„'] == ì„ íƒ_ì—°ë„_ìˆ«ìž]
        
        if ë¶„ì„ìœ í˜• == "ì›”ë³„ ë¶„ì„":
            st.markdown("### ðŸ“† ì›”ë³„ ìˆ˜ìž…/ì§€ì¶œ ë¶„ì„")
            
            df['ë…„ì›”'] = df['ë‚ ì§œ'].dt.to_period('M').astype(str)
            
            ìž…ê¸ˆ_df = df[df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ', na=False)].groupby('ë…„ì›”')['ê³µê¸‰ê°€ì•¡'].sum()
            ì¶œê¸ˆ_df = df[df['ì°¸ì¡°'].str.contains('ì¶œê¸ˆ', na=False)].groupby('ë…„ì›”')['ê³µê¸‰ê°€ì•¡'].sum().abs()
            # ì™¸ìž…ì€ ìŒìˆ˜ì´ë¯€ë¡œ ì ˆëŒ€ê°’
            ë§¤ìž…_df = df[df['ì°¸ì¡°'].str.contains('ì™¸ìž…', na=False)].groupby('ë…„ì›”')['ê³µê¸‰ê°€ì•¡'].sum().abs()
            ë¶€ê°€ì„¸_df = df[df['ì°¸ì¡°'].str.contains('ì™¸ìž…', na=False)].groupby('ë…„ì›”')['ë¶€ê°€ì„¸'].sum().abs()
            # ì™¸ì¶œ(íŒë§¤)
            ë§¤ì¶œ_df = df[df['ì°¸ì¡°'].str.contains('ì™¸ì¶œ', na=False)].groupby('ë…„ì›”').apply(
                lambda x: x['ê³µê¸‰ê°€ì•¡'].sum() + x['ë¶€ê°€ì„¸'].sum()
            )
            
            ì›”ë³„_df = pd.DataFrame({
                'ìˆ˜ìž…': ìž…ê¸ˆ_df,
                'ì§€ì¶œ': ì¶œê¸ˆ_df,
                'ë§¤ìž…': ë§¤ìž…_df,
                'ë§¤ì¶œ': ë§¤ì¶œ_df,
                'ìˆœì´ìµ': ìž…ê¸ˆ_df - ì¶œê¸ˆ_df
            }).fillna(0)
            
            # ìµœì‹ ìˆœ ì •ë ¬ (ì—­ìˆœ)
            ì›”ë³„_df = ì›”ë³„_df.sort_index(ascending=False)
            
            # ê·¸ëž˜í”„
            fig = go.Figure()
            fig.add_trace(go.Bar(name='ìˆ˜ìž…', x=ì›”ë³„_df.index, y=ì›”ë³„_df['ìˆ˜ìž…'], marker_color='#2E7D32'))
            fig.add_trace(go.Bar(name='ì§€ì¶œ', x=ì›”ë³„_df.index, y=ì›”ë³„_df['ì§€ì¶œ'], marker_color='#C62828'))
            fig.add_trace(go.Scatter(name='ìˆœì´ìµ', x=ì›”ë³„_df.index, y=ì›”ë³„_df['ìˆœì´ìµ'], mode='lines+markers', line=dict(color='#1976D2', width=3)))
            
            fig.update_layout(height=500, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)
            
            # í…Œì´ë¸”
            st.dataframe(ì›”ë³„_df.applymap(lambda x: f"{x:,.0f}"), use_container_width=True)
        
        elif ë¶„ì„ìœ í˜• == "ê±°ëž˜ì²˜ë³„ ë¶„ì„":
            st.markdown("### ðŸ¢ ê±°ëž˜ì²˜ë³„ ë¶„ì„")
            
            ê±°ëž˜ì²˜ë³„ = df[df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ', na=False)].groupby('ê±°ëž˜ì²˜').agg({
                'ê³µê¸‰ê°€ì•¡': 'sum',
                'ë‚ ì§œ': 'count'
            }).rename(columns={'ë‚ ì§œ': 'ê±°ëž˜íšŸìˆ˜'}).sort_values('ê³µê¸‰ê°€ì•¡', ascending=False)
            
            ê±°ëž˜ì²˜ë³„['í‰ê· ê±°ëž˜ì•¡'] = ê±°ëž˜ì²˜ë³„['ê³µê¸‰ê°€ì•¡'] / ê±°ëž˜ì²˜ë³„['ê±°ëž˜íšŸìˆ˜']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### TOP 20 ê±°ëž˜ì²˜")
                top20 = ê±°ëž˜ì²˜ë³„.head(20).copy()
                top20['ê³µê¸‰ê°€ì•¡'] = top20['ê³µê¸‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}")
                top20['í‰ê· ê±°ëž˜ì•¡'] = top20['í‰ê· ê±°ëž˜ì•¡'].apply(lambda x: f"{x:,.0f}")
                st.dataframe(top20, use_container_width=True)
            
            with col2:
                st.markdown("#### ê±°ëž˜ì²˜ë³„ ë§¤ì¶œ ë¹„ì¤‘")
                fig = px.pie(ê±°ëž˜ì²˜ë³„.head(10), values='ê³µê¸‰ê°€ì•¡', names=ê±°ëž˜ì²˜ë³„.head(10).index, hole=0.4)
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        elif ë¶„ì„ìœ í˜• == "í’ˆëª©ë³„ ë¶„ì„":
            st.markdown("### ðŸ“¦ í’ˆëª©ë³„ ë§¤ì¶œ ë¶„ì„")
            
            # í’ˆëª©ì—ì„œ í‚¤ì›Œë“œ ì¶”ì¶œ (ê°„ë‹¨ížˆ)
            df_ìž…ê¸ˆ = df[df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ', na=False)].copy()
            
            if len(df_ìž…ê¸ˆ) > 0:
                í’ˆëª©ë³„ = df_ìž…ê¸ˆ.groupby('í’ˆëª©')['ê³µê¸‰ê°€ì•¡'].sum().sort_values(ascending=False).head(20)
                
                st.bar_chart(í’ˆëª©ë³„)
                
                st.dataframe(í’ˆëª©ë³„.apply(lambda x: f"{x:,.0f}"), use_container_width=True)
            else:
                st.info("ìž…ê¸ˆ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
        
        elif ë¶„ì„ìœ í˜• == "ë¶€ê°€ì„¸ ë¶„ì„":
            st.markdown("### ðŸ§¾ ë¶€ê°€ì„¸ ë¶„ì„")
            
            df['ë…„ì›”'] = df['ë‚ ì§œ'].dt.to_period('M').astype(str)
            
            # ì™¸ìž…(ë§¤ìž…)ì€ ìŒìˆ˜ì´ë¯€ë¡œ ì ˆëŒ€ê°’
            ë§¤ìž…ë¶€ê°€ì„¸ = df[df['ì°¸ì¡°'].str.contains('ì™¸ìž…', na=False)].groupby('ë…„ì›”')['ë¶€ê°€ì„¸'].sum().abs()
            # ì™¸ì¶œ(ë§¤ì¶œ) ë¶€ê°€ì„¸
            ë§¤ì¶œë¶€ê°€ì„¸ = df[df['ì°¸ì¡°'].str.contains('ì™¸ì¶œ', na=False)].groupby('ë…„ì›”')['ë¶€ê°€ì„¸'].sum()
            
            ë¶€ê°€ì„¸_df = pd.DataFrame({
                'ë§¤ìž…ë¶€ê°€ì„¸': ë§¤ìž…ë¶€ê°€ì„¸,
                'ë§¤ì¶œë¶€ê°€ì„¸': ë§¤ì¶œë¶€ê°€ì„¸,
                'ë‚©ë¶€ì„¸ì•¡': ë§¤ì¶œë¶€ê°€ì„¸ - ë§¤ìž…ë¶€ê°€ì„¸
            }).fillna(0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ì›”ë³„ ë¶€ê°€ì„¸")
                fig = go.Figure()
                fig.add_trace(go.Bar(name='ë§¤ì¶œë¶€ê°€ì„¸', x=ë¶€ê°€ì„¸_df.index, y=ë¶€ê°€ì„¸_df['ë§¤ì¶œë¶€ê°€ì„¸'], marker_color='#2E7D32'))
                fig.add_trace(go.Bar(name='ë§¤ìž…ë¶€ê°€ì„¸', x=ë¶€ê°€ì„¸_df.index, y=ë¶€ê°€ì„¸_df['ë§¤ìž…ë¶€ê°€ì„¸'], marker_color='#C62828'))
                fig.update_layout(barmode='group', height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### í†µê³„")
                st.metric("ì´ ë§¤ì¶œë¶€ê°€ì„¸", f"{ë¶€ê°€ì„¸_df['ë§¤ì¶œë¶€ê°€ì„¸'].sum():,.0f}ì›")
                st.metric("ì´ ë§¤ìž…ë¶€ê°€ì„¸", f"{ë¶€ê°€ì„¸_df['ë§¤ìž…ë¶€ê°€ì„¸'].sum():,.0f}ì›")
                st.metric("ë‚©ë¶€ì„¸ì•¡ (ë§¤ì¶œ-ë§¤ìž…)", f"{ë¶€ê°€ì„¸_df['ë‚©ë¶€ì„¸ì•¡'].sum():,.0f}ì›")

# ==================== ì™¸ìƒ ê´€ë¦¬ ====================
elif menu == "ðŸ’° ì™¸ìƒ ê´€ë¦¬":
    st.title("ðŸ’° ì™¸ìƒ ê´€ë¦¬")
    
    df = st.session_state.ledger_df.copy()
    base_recv = st.session_state.base_receivables_df.copy()
    
    if len(base_recv) == 0:
        st.info("ì•„ì§ ë¯¸ìˆ˜ê¸ˆ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
    else:
        # íƒ­ìœ¼ë¡œ ë¯¸ìˆ˜ê¸ˆ/ë¯¸ì§€ê¸‰ê¸ˆ ë¶„ë¦¬
        tab_recv, tab_pay = st.tabs(["ðŸ“¤ ë¯¸ìˆ˜ê¸ˆ (ë°›ì„ ëˆ)", "ðŸ“¥ ë¯¸ì§€ê¸‰ê¸ˆ (ì¤„ ëˆ)"])
        
        # ===== ë¯¸ìˆ˜ê¸ˆ íƒ­ (íŒë§¤ì²˜) =====
        with tab_recv:
            st.markdown("### ðŸ“¤ ì™¸ìƒ ë§¤ì¶œê¸ˆ (ë¯¸ìˆ˜ê¸ˆ)")
            st.caption("ðŸ’¡ ë¯¸ìˆ˜ê¸ˆ = ì»´ìž¥ë¶€ GULREST ê°’ (2025.12.20 ê¸°ì¤€)")
            
            # base_receivablesì—ì„œ ë¯¸ìˆ˜ê¸ˆ ê°€ì ¸ì˜¤ê¸° (ì–‘ìˆ˜)
            ë¯¸ìˆ˜ê¸ˆ_df = base_recv[base_recv['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'] > 0].copy()
            ë¯¸ìˆ˜ê¸ˆ_df = ë¯¸ìˆ˜ê¸ˆ_df.sort_values('ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ', ascending=False)
            
            if len(ë¯¸ìˆ˜ê¸ˆ_df) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ì´ ë¯¸ìˆ˜ê¸ˆ", f"{ë¯¸ìˆ˜ê¸ˆ_df['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].sum():,.0f}ì›")
                with col2:
                    st.metric("ë¯¸ìˆ˜ ê±°ëž˜ì²˜ ìˆ˜", f"{len(ë¯¸ìˆ˜ê¸ˆ_df)}ê°œ")
                with col3:
                    st.metric("ìµœëŒ€ ë¯¸ìˆ˜ê¸ˆ", f"{ë¯¸ìˆ˜ê¸ˆ_df['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].max():,.0f}ì›")
                
                st.markdown("---")
                
                # í‘œì‹œìš© ë°ì´í„°í”„ë ˆìž„
                display_df = ë¯¸ìˆ˜ê¸ˆ_df[['ê±°ëž˜ì²˜', 'ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ', 'ê¸°ì¤€ì¼ìž']].copy()
                display_df.columns = ['ê±°ëž˜ì²˜', 'ë¯¸ìˆ˜ê¸ˆ', 'ê¸°ì¤€ì¼ìž']
                display_df['ë¯¸ìˆ˜ê¸ˆ'] = display_df['ë¯¸ìˆ˜ê¸ˆ'].apply(lambda x: f"{x:,.0f}")
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # ë‹¤ìš´ë¡œë“œ ë²„íŠ¼
                csv = ë¯¸ìˆ˜ê¸ˆ_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="ðŸ“¥ ë¯¸ìˆ˜ê¸ˆ ëª©ë¡ ë‹¤ìš´ë¡œë“œ (CSV)",
                    data=csv,
                    file_name=f"ë¯¸ìˆ˜ê¸ˆëª©ë¡_{get_kst_now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.success("âœ… ë¯¸ìˆ˜ê¸ˆì´ ì—†ìŠµë‹ˆë‹¤!")
        
        # ===== ë¯¸ì§€ê¸‰ê¸ˆ íƒ­ (ë§¤ìž…ì²˜) =====
        with tab_pay:
            st.markdown("### ðŸ“¥ ì™¸ìƒ ë§¤ìž…ê¸ˆ (ë¯¸ì§€ê¸‰ê¸ˆ)")
            st.caption("ðŸ’¡ ë¯¸ì§€ê¸‰ê¸ˆ = ì»´ìž¥ë¶€ GULREST ê°’ (ìŒìˆ˜, 2025.12.20 ê¸°ì¤€)")
            
            # base_receivablesì—ì„œ ë¯¸ì§€ê¸‰ê¸ˆ ê°€ì ¸ì˜¤ê¸° (ìŒìˆ˜)
            ë¯¸ì§€ê¸‰ê¸ˆ_raw = base_recv[base_recv['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'] < 0].copy()
            
            if len(ë¯¸ì§€ê¸‰ê¸ˆ_raw) > 0:
                ë¯¸ì§€ê¸‰ê¸ˆ_df = ë¯¸ì§€ê¸‰ê¸ˆ_raw.copy()
                ë¯¸ì§€ê¸‰ê¸ˆ_df['ë¯¸ì§€ê¸‰ê¸ˆ'] = ë¯¸ì§€ê¸‰ê¸ˆ_df['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].abs()
                ë¯¸ì§€ê¸‰ê¸ˆ_df = ë¯¸ì§€ê¸‰ê¸ˆ_df.sort_values('ë¯¸ì§€ê¸‰ê¸ˆ', ascending=False)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("ì´ ë¯¸ì§€ê¸‰ê¸ˆ", f"{ë¯¸ì§€ê¸‰ê¸ˆ_df['ë¯¸ì§€ê¸‰ê¸ˆ'].sum():,.0f}ì›")
                with col2:
                    st.metric("ë¯¸ì§€ê¸‰ ê±°ëž˜ì²˜ ìˆ˜", f"{len(ë¯¸ì§€ê¸‰ê¸ˆ_df)}ê°œ")
                with col3:
                    st.metric("ìµœëŒ€ ë¯¸ì§€ê¸‰ê¸ˆ", f"{ë¯¸ì§€ê¸‰ê¸ˆ_df['ë¯¸ì§€ê¸‰ê¸ˆ'].max():,.0f}ì›")
                
                st.markdown("---")
                
                # í‘œì‹œìš© ë°ì´í„°í”„ë ˆìž„
                display_df = ë¯¸ì§€ê¸‰ê¸ˆ_df[['ê±°ëž˜ì²˜', 'ë¯¸ì§€ê¸‰ê¸ˆ', 'ê¸°ì¤€ì¼ìž']].copy()
                display_df['ë¯¸ì§€ê¸‰ê¸ˆ'] = display_df['ë¯¸ì§€ê¸‰ê¸ˆ'].apply(lambda x: f"{x:,.0f}")
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # ë‹¤ìš´ë¡œë“œ ë²„íŠ¼
                csv = ë¯¸ì§€ê¸‰ê¸ˆ_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="ðŸ“¥ ë¯¸ì§€ê¸‰ê¸ˆ ëª©ë¡ ë‹¤ìš´ë¡œë“œ (CSV)",
                    data=csv,
                    file_name=f"ë¯¸ì§€ê¸‰ê¸ˆëª©ë¡_{get_kst_now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.success("âœ… ë¯¸ì§€ê¸‰ê¸ˆì´ ì—†ìŠµë‹ˆë‹¤!")

# ==================== íšŒê³„ ê´€ë¦¬ ====================
elif menu == "ðŸ§¾ íšŒê³„ ê´€ë¦¬":
    st.title("ðŸ§¾ íšŒê³„ ê´€ë¦¬")
    
    df = st.session_state.ledger_df.copy()
    
    if len(df) == 0:
        st.info("ì•„ì§ ê±°ëž˜ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
    else:
        # ìµœê·¼ 4ê°œë…„ë„ í•„í„°
        ë‹¹í•´ì—°ë„ = get_kst_now().year
        ì—°ë„_ëª©ë¡ = [ë‹¹í•´ì—°ë„, ë‹¹í•´ì—°ë„-1, ë‹¹í•´ì—°ë„-2, ë‹¹í•´ì—°ë„-3]
        
        # íƒ­ ìƒì„± (ìœ ì˜ì°¬ ë§¤ì¶œ íƒ­ ì¶”ê°€)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["ðŸ“Š ì†ìµ í˜„í™©", "ðŸ§¾ ë¶€ê°€ì„¸ í˜„í™©", "ðŸ’¹ ë§ˆì§„ ë¶„ì„", "ðŸ¢ ê±°ëž˜ì²˜ë³„ ë§ˆì§„", "ðŸ‘¤ ìœ ì˜ì°¬ ë§¤ì¶œ"])
        
        # ===== íƒ­1: ì†ìµ í˜„í™© =====
        with tab1:
            st.markdown("### ðŸ“Š ì—°ë„ë³„ ì†ìµ í˜„í™©")
            
            df['ì—°ë„'] = df['ë‚ ì§œ'].dt.year
            df_4ë…„ = df[df['ì—°ë„'].isin(ì—°ë„_ëª©ë¡)]
            
            ì†ìµ_ë°ì´í„° = []
            for ì—°ë„ in sorted(ì—°ë„_ëª©ë¡, reverse=True):
                ì—°ë„_df = df_4ë…„[df_4ë…„['ì—°ë„'] == ì—°ë„]
                
                # ìˆ˜ìž… (ìž…ê¸ˆ)
                ìˆ˜ìž… = ì—°ë„_df[ì—°ë„_df['ì°¸ì¡°'] == '=ìž…ê¸ˆ']['ê³µê¸‰ê°€ì•¡'].sum()
                
                # ì§€ì¶œ (ì¶œê¸ˆ) - ìŒìˆ˜ì´ë¯€ë¡œ ì ˆëŒ€ê°’
                ì§€ì¶œ = abs(ì—°ë„_df[ì—°ë„_df['ì°¸ì¡°'] == '=ì¶œê¸ˆ']['ê³µê¸‰ê°€ì•¡'].sum())
                
                # ë§¤ì¶œ (ì™¸ì¶œ)
                ì™¸ì¶œ_df = ì—°ë„_df[ì—°ë„_df['ì°¸ì¡°'] == '=ì™¸ì¶œ']
                ë§¤ì¶œ = ì™¸ì¶œ_df['ê³µê¸‰ê°€ì•¡'].sum()
                ë§¤ì¶œë¶€ê°€ì„¸ = ì™¸ì¶œ_df['ë¶€ê°€ì„¸'].sum()
                
                # ë§¤ìž… (ì™¸ìž…) - ìŒìˆ˜ì´ë¯€ë¡œ ì ˆëŒ€ê°’
                ì™¸ìž…_df = ì—°ë„_df[ì—°ë„_df['ì°¸ì¡°'] == '=ì™¸ìž…']
                ë§¤ìž… = abs(ì™¸ìž…_df['ê³µê¸‰ê°€ì•¡'].sum())
                ë§¤ìž…ë¶€ê°€ì„¸ = abs(ì™¸ìž…_df['ë¶€ê°€ì„¸'].sum())
                
                # ë§ˆì§„ (ë§¤ìž…ë‹¨ê°€ê°€ ìžˆëŠ” ê²½ìš°)
                ë§ˆì§„ = ì™¸ì¶œ_df['ë§ˆì§„'].sum() if 'ë§ˆì§„' in ì™¸ì¶œ_df.columns else 0
                
                ì†ìµ_ë°ì´í„°.append({
                    'ì—°ë„': f"{ì—°ë„}ë…„",
                    'ë§¤ì¶œ': ë§¤ì¶œ,
                    'ë§¤ìž…': ë§¤ìž…,
                    'ë§ˆì§„': ë§ˆì§„,
                    'ë§ˆì§„ìœ¨': (ë§ˆì§„ / ë§¤ì¶œ * 100) if ë§¤ì¶œ > 0 else 0,
                    'ìˆ˜ìž…(ìž…ê¸ˆ)': ìˆ˜ìž…,
                    'ì§€ì¶œ(ì¶œê¸ˆ)': ì§€ì¶œ,
                    'ìˆœì´ìµ': ìˆ˜ìž… - ì§€ì¶œ
                })
            
            ì†ìµ_df = pd.DataFrame(ì†ìµ_ë°ì´í„°)
            
            # ìš”ì•½ ì§€í‘œ
            col1, col2, col3, col4 = st.columns(4)
            ë‹¹í•´_ë°ì´í„° = ì†ìµ_df[ì†ìµ_df['ì—°ë„'] == f"{ë‹¹í•´ì—°ë„}ë…„"].iloc[0] if len(ì†ìµ_df[ì†ìµ_df['ì—°ë„'] == f"{ë‹¹í•´ì—°ë„}ë…„"]) > 0 else None
            
            if ë‹¹í•´_ë°ì´í„° is not None:
                with col1:
                    st.metric(f"{ë‹¹í•´ì—°ë„}ë…„ ë§¤ì¶œ", f"{ë‹¹í•´_ë°ì´í„°['ë§¤ì¶œ']:,.0f}ì›")
                with col2:
                    st.metric(f"{ë‹¹í•´ì—°ë„}ë…„ ë§ˆì§„", f"{ë‹¹í•´_ë°ì´í„°['ë§ˆì§„']:,.0f}ì›", delta=f"{ë‹¹í•´_ë°ì´í„°['ë§ˆì§„ìœ¨']:.1f}%")
                with col3:
                    st.metric(f"{ë‹¹í•´ì—°ë„}ë…„ ìˆ˜ìž…", f"{ë‹¹í•´_ë°ì´í„°['ìˆ˜ìž…(ìž…ê¸ˆ)']:,.0f}ì›")
                with col4:
                    st.metric(f"{ë‹¹í•´ì—°ë„}ë…„ ìˆœì´ìµ", f"{ë‹¹í•´_ë°ì´í„°['ìˆœì´ìµ']:,.0f}ì›")
            
            st.markdown("---")
            
            # ì—°ë„ë³„ ë¹„êµ ì°¨íŠ¸
            fig = go.Figure()
            fig.add_trace(go.Bar(name='ë§¤ì¶œ', x=ì†ìµ_df['ì—°ë„'], y=ì†ìµ_df['ë§¤ì¶œ'], marker_color='#1976D2'))
            fig.add_trace(go.Bar(name='ë§ˆì§„', x=ì†ìµ_df['ì—°ë„'], y=ì†ìµ_df['ë§ˆì§„'], marker_color='#43A047'))
            fig.add_trace(go.Bar(name='ìˆœì´ìµ', x=ì†ìµ_df['ì—°ë„'], y=ì†ìµ_df['ìˆœì´ìµ'], marker_color='#FF9800'))
            fig.update_layout(barmode='group', height=400, title='ì—°ë„ë³„ ì†ìµ ë¹„êµ')
            st.plotly_chart(fig, use_container_width=True)
            
            # ìƒì„¸ í…Œì´ë¸”
            display_ì†ìµ = ì†ìµ_df.copy()
            for col in ['ë§¤ì¶œ', 'ë§¤ìž…', 'ë§ˆì§„', 'ìˆ˜ìž…(ìž…ê¸ˆ)', 'ì§€ì¶œ(ì¶œê¸ˆ)', 'ìˆœì´ìµ']:
                display_ì†ìµ[col] = display_ì†ìµ[col].apply(lambda x: f"{x:,.0f}")
            display_ì†ìµ['ë§ˆì§„ìœ¨'] = display_ì†ìµ['ë§ˆì§„ìœ¨'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_ì†ìµ, use_container_width=True, hide_index=True)
        
        # ===== íƒ­2: ë¶€ê°€ì„¸ í˜„í™© =====
        with tab2:
            st.markdown("### ðŸ§¾ ì›”ë³„ ë¶€ê°€ì„¸ ìž¥ë¶€")
            
            ì„ íƒ_ì—°ë„_ë¶€ê°€ì„¸ = st.selectbox("ì—°ë„ ì„ íƒ", ì—°ë„_ëª©ë¡, format_func=lambda x: f"{x}ë…„", key="vat_year")
            
            df['ì—°ë„'] = df['ë‚ ì§œ'].dt.year
            df['ì›”'] = df['ë‚ ì§œ'].dt.month
            ì—°ë„_df = df[df['ì—°ë„'] == ì„ íƒ_ì—°ë„_ë¶€ê°€ì„¸]
            
            # ì›”ë³„ ë¶€ê°€ì„¸ ê³„ì‚°
            ì›”ë³„_ë°ì´í„° = []
            
            # ë¶„ê¸°/ë°˜ê¸° ëˆ„ì ìš©
            q1_data = {'ì´ë§¤ì¶œì•¡': 0, 'ê³„ì‚°ì„œë§¤ì¶œ': 0, 'ë§¤ì¶œë¶€ê°€ì„¸': 0, 'í˜„ê¸ˆë§¤ì¶œ': 0, 'ë§¤ìž…ì•¡': 0, 'ë§¤ìž…ë¶€ê°€ì„¸': 0, 'ë‚©ë¶€ì„¸ì•¡': 0}
            q2_data = {'ì´ë§¤ì¶œì•¡': 0, 'ê³„ì‚°ì„œë§¤ì¶œ': 0, 'ë§¤ì¶œë¶€ê°€ì„¸': 0, 'í˜„ê¸ˆë§¤ì¶œ': 0, 'ë§¤ìž…ì•¡': 0, 'ë§¤ìž…ë¶€ê°€ì„¸': 0, 'ë‚©ë¶€ì„¸ì•¡': 0}
            q3_data = {'ì´ë§¤ì¶œì•¡': 0, 'ê³„ì‚°ì„œë§¤ì¶œ': 0, 'ë§¤ì¶œë¶€ê°€ì„¸': 0, 'í˜„ê¸ˆë§¤ì¶œ': 0, 'ë§¤ìž…ì•¡': 0, 'ë§¤ìž…ë¶€ê°€ì„¸': 0, 'ë‚©ë¶€ì„¸ì•¡': 0}
            q4_data = {'ì´ë§¤ì¶œì•¡': 0, 'ê³„ì‚°ì„œë§¤ì¶œ': 0, 'ë§¤ì¶œë¶€ê°€ì„¸': 0, 'í˜„ê¸ˆë§¤ì¶œ': 0, 'ë§¤ìž…ì•¡': 0, 'ë§¤ìž…ë¶€ê°€ì„¸': 0, 'ë‚©ë¶€ì„¸ì•¡': 0}
            
            for ì›” in range(1, 13):
                ì›”_df = ì—°ë„_df[ì—°ë„_df['ì›”'] == ì›”]
                
                # ë§¤ì¶œ
                ì™¸ì¶œ_df = ì›”_df[ì›”_df['ì°¸ì¡°'] == '=ì™¸ì¶œ']
                ì´ë§¤ì¶œì•¡ = ì™¸ì¶œ_df['ê³µê¸‰ê°€ì•¡'].sum() + ì™¸ì¶œ_df['ë¶€ê°€ì„¸'].sum()
                ê³„ì‚°ì„œë§¤ì¶œ = ì™¸ì¶œ_df[ì™¸ì¶œ_df['ë¶€ê°€ì„¸'] > 0]['ê³µê¸‰ê°€ì•¡'].sum()
                ë§¤ì¶œë¶€ê°€ì„¸ = ì™¸ì¶œ_df['ë¶€ê°€ì„¸'].sum()
                í˜„ê¸ˆë§¤ì¶œ = ì™¸ì¶œ_df[ì™¸ì¶œ_df['ë¶€ê°€ì„¸'] == 0]['ê³µê¸‰ê°€ì•¡'].sum()
                
                # ë§¤ìž…
                ì™¸ìž…_df = ì›”_df[ì›”_df['ì°¸ì¡°'] == '=ì™¸ìž…']
                ë§¤ìž…ì•¡ = abs(ì™¸ìž…_df['ê³µê¸‰ê°€ì•¡'].sum())
                ë§¤ìž…ë¶€ê°€ì„¸ = abs(ì™¸ìž…_df['ë¶€ê°€ì„¸'].sum())
                
                # ë‚©ë¶€ì„¸ì•¡
                ë‚©ë¶€ì„¸ì•¡ = ë§¤ì¶œë¶€ê°€ì„¸ - ë§¤ìž…ë¶€ê°€ì„¸
                
                row_data = {
                    'êµ¬ë¶„': f"{ì›”}ì›”",
                    'ì´ë§¤ì¶œì•¡': ì´ë§¤ì¶œì•¡,
                    'ê³„ì‚°ì„œë§¤ì¶œ': ê³„ì‚°ì„œë§¤ì¶œ,
                    'ë§¤ì¶œë¶€ê°€ì„¸': ë§¤ì¶œë¶€ê°€ì„¸,
                    'í˜„ê¸ˆë§¤ì¶œ': í˜„ê¸ˆë§¤ì¶œ,
                    'ë§¤ìž…ì•¡': ë§¤ìž…ì•¡,
                    'ë§¤ìž…ë¶€ê°€ì„¸': ë§¤ìž…ë¶€ê°€ì„¸,
                    'ë‚©ë¶€ì„¸ì•¡': ë‚©ë¶€ì„¸ì•¡
                }
                ì›”ë³„_ë°ì´í„°.append(row_data)
                
                # ë¶„ê¸°ë³„ ëˆ„ì 
                if ì›” <= 3:
                    for k in q1_data: q1_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                elif ì›” <= 6:
                    for k in q2_data: q2_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                elif ì›” <= 9:
                    for k in q3_data: q3_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                else:
                    for k in q4_data: q4_data[k] += row_data.get(k, 0) if isinstance(row_data.get(k, 0), (int, float)) else 0
                
                # 3ì›” í›„ 1ë¶„ê¸° í•©ì‚°
                if ì›” == 3:
                    ì›”ë³„_ë°ì´í„°.append({'êµ¬ë¶„': 'â–¶ 1ë¶„ê¸° í•©ê³„', **q1_data})
                
                # 6ì›” í›„ 2ë¶„ê¸° + ìƒë°˜ê¸° í•©ì‚°
                if ì›” == 6:
                    ì›”ë³„_ë°ì´í„°.append({'êµ¬ë¶„': 'â–¶ 2ë¶„ê¸° í•©ê³„', **q2_data})
                    ìƒë°˜ê¸° = {k: q1_data[k] + q2_data[k] for k in q1_data}
                    ì›”ë³„_ë°ì´í„°.append({'êµ¬ë¶„': 'â˜… ìƒë°˜ê¸° í•©ê³„', **ìƒë°˜ê¸°})
                
                # 9ì›” í›„ 3ë¶„ê¸° í•©ì‚°
                if ì›” == 9:
                    ì›”ë³„_ë°ì´í„°.append({'êµ¬ë¶„': 'â–¶ 3ë¶„ê¸° í•©ê³„', **q3_data})
                
                # 12ì›” í›„ 4ë¶„ê¸° + í•˜ë°˜ê¸° + ì—°ê°„ í•©ì‚°
                if ì›” == 12:
                    ì›”ë³„_ë°ì´í„°.append({'êµ¬ë¶„': 'â–¶ 4ë¶„ê¸° í•©ê³„', **q4_data})
                    í•˜ë°˜ê¸° = {k: q3_data[k] + q4_data[k] for k in q3_data}
                    ì›”ë³„_ë°ì´í„°.append({'êµ¬ë¶„': 'â˜… í•˜ë°˜ê¸° í•©ê³„', **í•˜ë°˜ê¸°})
                    ì—°ê°„ = {k: q1_data[k] + q2_data[k] + q3_data[k] + q4_data[k] for k in q1_data}
                    ì›”ë³„_ë°ì´í„°.append({'êµ¬ë¶„': 'â—† ì—°ê°„ í•©ê³„', **ì—°ê°„})
            
            ì›”ë³„_df = pd.DataFrame(ì›”ë³„_ë°ì´í„°)
            
            # ì—°ê°„ ìš”ì•½ (ìƒë‹¨)
            ì—°ê°„_ë§¤ì¶œë¶€ê°€ì„¸ = q1_data['ë§¤ì¶œë¶€ê°€ì„¸'] + q2_data['ë§¤ì¶œë¶€ê°€ì„¸'] + q3_data['ë§¤ì¶œë¶€ê°€ì„¸'] + q4_data['ë§¤ì¶œë¶€ê°€ì„¸']
            ì—°ê°„_ë§¤ìž…ë¶€ê°€ì„¸ = q1_data['ë§¤ìž…ë¶€ê°€ì„¸'] + q2_data['ë§¤ìž…ë¶€ê°€ì„¸'] + q3_data['ë§¤ìž…ë¶€ê°€ì„¸'] + q4_data['ë§¤ìž…ë¶€ê°€ì„¸']
            ì—°ê°„_ë‚©ë¶€ì„¸ì•¡ = ì—°ê°„_ë§¤ì¶œë¶€ê°€ì„¸ - ì—°ê°„_ë§¤ìž…ë¶€ê°€ì„¸
            
            st.markdown(f"#### {ì„ íƒ_ì—°ë„_ë¶€ê°€ì„¸}ë…„ ì—°ê°„ ìš”ì•½")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ðŸ“¤ ë§¤ì¶œë¶€ê°€ì„¸", f"{ì—°ê°„_ë§¤ì¶œë¶€ê°€ì„¸:,.0f}ì›")
            with col2:
                st.metric("ðŸ“¥ ë§¤ìž…ë¶€ê°€ì„¸", f"{ì—°ê°„_ë§¤ìž…ë¶€ê°€ì„¸:,.0f}ì›")
            with col3:
                if ì—°ê°„_ë‚©ë¶€ì„¸ì•¡ >= 0:
                    st.metric("ðŸ’¸ ë‚©ë¶€í•  ë¶€ê°€ì„¸", f"{ì—°ê°„_ë‚©ë¶€ì„¸ì•¡:,.0f}ì›")
                else:
                    st.metric("ðŸ’° í™˜ê¸‰ë°›ì„ ë¶€ê°€ì„¸", f"{abs(ì—°ê°„_ë‚©ë¶€ì„¸ì•¡):,.0f}ì›")
            
            st.markdown("---")
            
            # ì›”ë³„ ìƒì„¸ í…Œì´ë¸” (st.dataframe ì‚¬ìš©)
            st.markdown("#### ì›”ë³„ ìƒì„¸")
            
            display_df = ì›”ë³„_df.copy()
            for col in ['ì´ë§¤ì¶œì•¡', 'ê³„ì‚°ì„œë§¤ì¶œ', 'ë§¤ì¶œë¶€ê°€ì„¸', 'í˜„ê¸ˆë§¤ì¶œ', 'ë§¤ìž…ì•¡', 'ë§¤ìž…ë¶€ê°€ì„¸', 'ë‚©ë¶€ì„¸ì•¡']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=700)
            
            # ì°¨íŠ¸
            st.markdown("---")
            st.markdown("#### ì›”ë³„ ë¶€ê°€ì„¸ ì¶”ì´")
            ì›”_only = ì›”ë³„_df[~ì›”ë³„_df['êµ¬ë¶„'].str.contains('í•©ê³„')]
            fig = go.Figure()
            fig.add_trace(go.Bar(name='ë§¤ì¶œë¶€ê°€ì„¸', x=ì›”_only['êµ¬ë¶„'], y=ì›”_only['ë§¤ì¶œë¶€ê°€ì„¸'], marker_color='#1976D2'))
            fig.add_trace(go.Bar(name='ë§¤ìž…ë¶€ê°€ì„¸', x=ì›”_only['êµ¬ë¶„'], y=ì›”_only['ë§¤ìž…ë¶€ê°€ì„¸'], marker_color='#FF5722'))
            fig.add_trace(go.Scatter(name='ë‚©ë¶€ì„¸ì•¡', x=ì›”_only['êµ¬ë¶„'], y=ì›”_only['ë‚©ë¶€ì„¸ì•¡'], mode='lines+markers', line=dict(color='#43A047', width=3)))
            fig.update_layout(barmode='group', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # ===== íƒ­3: ë§ˆì§„ ë¶„ì„ =====
        with tab3:
            st.markdown("### ðŸ’¹ ì›”ë³„ ë§ˆì§„ ë¶„ì„")
            
            col1, col2 = st.columns(2)
            with col1:
                ì„ íƒ_ì—°ë„_ë§ˆì§„ = st.selectbox("ì—°ë„ ì„ íƒ", ì—°ë„_ëª©ë¡, format_func=lambda x: f"{x}ë…„", key="margin_year")
            
            df['ì—°ë„'] = df['ë‚ ì§œ'].dt.year
            df['ì›”'] = df['ë‚ ì§œ'].dt.month
            ì—°ë„_df = df[df['ì—°ë„'] == ì„ íƒ_ì—°ë„_ë§ˆì§„]
            
            # ì›”ë³„ ë§ˆì§„ ê³„ì‚°
            ì›”ë³„_ë§ˆì§„ = []
            for ì›” in range(1, 13):
                ì›”_df = ì—°ë„_df[(ì—°ë„_df['ì›”'] == ì›”) & (ì—°ë„_df['ì°¸ì¡°'] == '=ì™¸ì¶œ')]
                
                ë§¤ì¶œ = ì›”_df['ê³µê¸‰ê°€ì•¡'].sum()
                ë§ˆì§„ = ì›”_df['ë§ˆì§„'].sum() if 'ë§ˆì§„' in ì›”_df.columns else 0
                ë§ˆì§„ìœ¨ = (ë§ˆì§„ / ë§¤ì¶œ * 100) if ë§¤ì¶œ > 0 else 0
                
                ì›”ë³„_ë§ˆì§„.append({
                    'ì›”': f"{ì›”}ì›”",
                    'ë§¤ì¶œ': ë§¤ì¶œ,
                    'ë§ˆì§„': ë§ˆì§„,
                    'ë§ˆì§„ìœ¨': ë§ˆì§„ìœ¨
                })
            
            ì›”ë³„_ë§ˆì§„_df = pd.DataFrame(ì›”ë³„_ë§ˆì§„)
            
            # ì°¨íŠ¸
            fig = go.Figure()
            fig.add_trace(go.Bar(name='ë§¤ì¶œ', x=ì›”ë³„_ë§ˆì§„_df['ì›”'], y=ì›”ë³„_ë§ˆì§„_df['ë§¤ì¶œ'], marker_color='#1976D2', yaxis='y'))
            fig.add_trace(go.Bar(name='ë§ˆì§„', x=ì›”ë³„_ë§ˆì§„_df['ì›”'], y=ì›”ë³„_ë§ˆì§„_df['ë§ˆì§„'], marker_color='#43A047', yaxis='y'))
            fig.add_trace(go.Scatter(name='ë§ˆì§„ìœ¨', x=ì›”ë³„_ë§ˆì§„_df['ì›”'], y=ì›”ë³„_ë§ˆì§„_df['ë§ˆì§„ìœ¨'], mode='lines+markers', line=dict(color='#FF5722', width=3), yaxis='y2'))
            
            fig.update_layout(
                barmode='group',
                height=450,
                title=f'{ì„ íƒ_ì—°ë„_ë§ˆì§„}ë…„ ì›”ë³„ ë§¤ì¶œ/ë§ˆì§„',
                yaxis=dict(title='ê¸ˆì•¡ (ì›)'),
                yaxis2=dict(title='ë§ˆì§„ìœ¨ (%)', overlaying='y', side='right', range=[0, 50])
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # í…Œì´ë¸”
            display_ë§ˆì§„ = ì›”ë³„_ë§ˆì§„_df.copy()
            display_ë§ˆì§„['ë§¤ì¶œ'] = display_ë§ˆì§„['ë§¤ì¶œ'].apply(lambda x: f"{x:,.0f}")
            display_ë§ˆì§„['ë§ˆì§„'] = display_ë§ˆì§„['ë§ˆì§„'].apply(lambda x: f"{x:,.0f}")
            display_ë§ˆì§„['ë§ˆì§„ìœ¨'] = display_ë§ˆì§„['ë§ˆì§„ìœ¨'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(display_ë§ˆì§„, use_container_width=True, hide_index=True)
            
            # ì—°ê°„ í•©ê³„
            ì´ë§¤ì¶œ = ì›”ë³„_ë§ˆì§„_df['ë§¤ì¶œ'].sum()
            ì´ë§ˆì§„ = ì›”ë³„_ë§ˆì§„_df['ë§ˆì§„'].sum()
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ì—°ê°„ ì´ë§¤ì¶œ", f"{ì´ë§¤ì¶œ:,.0f}ì›")
            with col2:
                st.metric("ì—°ê°„ ì´ë§ˆì§„", f"{ì´ë§ˆì§„:,.0f}ì›")
            with col3:
                st.metric("ì—°ê°„ í‰ê·  ë§ˆì§„ìœ¨", f"{(ì´ë§ˆì§„/ì´ë§¤ì¶œ*100):.1f}%" if ì´ë§¤ì¶œ > 0 else "0%")
        
        # ===== íƒ­4: ê±°ëž˜ì²˜ë³„ ë§ˆì§„ =====
        with tab4:
            st.markdown("### ðŸ¢ ê±°ëž˜ì²˜ë³„ ë§ˆì§„ ë¶„ì„")
            
            col1, col2 = st.columns(2)
            with col1:
                ì„ íƒ_ì—°ë„_ê±°ëž˜ì²˜ = st.selectbox("ì—°ë„ ì„ íƒ", ì—°ë„_ëª©ë¡, format_func=lambda x: f"{x}ë…„", key="customer_margin_year")
            
            df['ì—°ë„'] = df['ë‚ ì§œ'].dt.year
            ì—°ë„_df = df[(df['ì—°ë„'] == ì„ íƒ_ì—°ë„_ê±°ëž˜ì²˜) & (df['ì°¸ì¡°'] == '=ì™¸ì¶œ')]
            
            # ê±°ëž˜ì²˜ë³„ ë§ˆì§„ ê³„ì‚°
            ê±°ëž˜ì²˜ë³„_ë§ˆì§„ = ì—°ë„_df.groupby('ê±°ëž˜ì²˜').agg({
                'ê³µê¸‰ê°€ì•¡': 'sum',
                'ë§ˆì§„': 'sum',
                'ë‚ ì§œ': 'count'
            }).rename(columns={'ë‚ ì§œ': 'ê±°ëž˜íšŸìˆ˜'})
            
            ê±°ëž˜ì²˜ë³„_ë§ˆì§„['ë§ˆì§„ìœ¨'] = (ê±°ëž˜ì²˜ë³„_ë§ˆì§„['ë§ˆì§„'] / ê±°ëž˜ì²˜ë³„_ë§ˆì§„['ê³µê¸‰ê°€ì•¡'] * 100).round(1)
            ê±°ëž˜ì²˜ë³„_ë§ˆì§„ = ê±°ëž˜ì²˜ë³„_ë§ˆì§„.sort_values('ë§ˆì§„', ascending=False)
            
            # ìƒìœ„/í•˜ìœ„ ë¶„ì„
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ðŸ† ë§ˆì§„ TOP 10")
                top10 = ê±°ëž˜ì²˜ë³„_ë§ˆì§„.head(10).copy()
                display_top = top10.reset_index()
                display_top['ê³µê¸‰ê°€ì•¡'] = display_top['ê³µê¸‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}")
                display_top['ë§ˆì§„'] = display_top['ë§ˆì§„'].apply(lambda x: f"{x:,.0f}")
                display_top['ë§ˆì§„ìœ¨'] = display_top['ë§ˆì§„ìœ¨'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_top, use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("#### âš ï¸ ë§ˆì§„ìœ¨ í•˜ìœ„ 10 (ì£¼ì˜ í•„ìš”)")
                # ë§ˆì§„ìœ¨ ê¸°ì¤€ í•˜ìœ„ (ë§¤ì¶œì´ ìžˆëŠ” ê±°ëž˜ì²˜ë§Œ)
                ë§ˆì§„ìœ¨_í•˜ìœ„ = ê±°ëž˜ì²˜ë³„_ë§ˆì§„[ê±°ëž˜ì²˜ë³„_ë§ˆì§„['ê³µê¸‰ê°€ì•¡'] > 100000].sort_values('ë§ˆì§„ìœ¨').head(10).copy()
                display_bottom = ë§ˆì§„ìœ¨_í•˜ìœ„.reset_index()
                display_bottom['ê³µê¸‰ê°€ì•¡'] = display_bottom['ê³µê¸‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}")
                display_bottom['ë§ˆì§„'] = display_bottom['ë§ˆì§„'].apply(lambda x: f"{x:,.0f}")
                display_bottom['ë§ˆì§„ìœ¨'] = display_bottom['ë§ˆì§„ìœ¨'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_bottom, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # ë§ˆì§„ìœ¨ ë¶„í¬ ì°¨íŠ¸
            st.markdown("#### ê±°ëž˜ì²˜ ë§ˆì§„ìœ¨ ë¶„í¬")
            fig = px.histogram(ê±°ëž˜ì²˜ë³„_ë§ˆì§„, x='ë§ˆì§„ìœ¨', nbins=20, title='ë§ˆì§„ìœ¨ ë¶„í¬')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            # ì „ì²´ ê±°ëž˜ì²˜ ëª©ë¡
            with st.expander("ðŸ“‹ ì „ì²´ ê±°ëž˜ì²˜ ë§ˆì§„ ë³´ê¸°"):
                display_ì „ì²´ = ê±°ëž˜ì²˜ë³„_ë§ˆì§„.reset_index()
                display_ì „ì²´['ê³µê¸‰ê°€ì•¡'] = display_ì „ì²´['ê³µê¸‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}")
                display_ì „ì²´['ë§ˆì§„'] = display_ì „ì²´['ë§ˆì§„'].apply(lambda x: f"{x:,.0f}")
                display_ì „ì²´['ë§ˆì§„ìœ¨'] = display_ì „ì²´['ë§ˆì§„ìœ¨'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_ì „ì²´, use_container_width=True, hide_index=True, height=400)
        
        # ===== íƒ­5: ìœ ì˜ì°¬ ë§¤ì¶œ =====
        with tab5:
            st.markdown("### ðŸ‘¤ ìœ ì˜ì°¬ ë§¤ì¶œ ê´€ë¦¬")
            
            # ìœ ì˜ì°¬ ê±°ëž˜ë§Œ í•„í„°
            ìœ ì˜ì°¬_df = df[df['ê±°ëž˜ì²˜'] == 'ìœ ì˜ì°¬'].copy()
            
            if len(ìœ ì˜ì°¬_df) == 0:
                st.info("ìœ ì˜ì°¬ ê±°ëž˜ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
            else:
                ìœ ì˜ì°¬_df['ì—°ë„'] = ìœ ì˜ì°¬_df['ë‚ ì§œ'].dt.year
                ìœ ì˜ì°¬_df['ì›”'] = ìœ ì˜ì°¬_df['ë‚ ì§œ'].dt.month
                
                # ì—°ë„ ì„ íƒ
                col1, col2 = st.columns(2)
                with col1:
                    ì„ íƒ_ì—°ë„_ìœ ì˜ì°¬ = st.selectbox("ì—°ë„ ì„ íƒ", ì—°ë„_ëª©ë¡, format_func=lambda x: f"{x}ë…„", key="yoo_year")
                
                ì—°ë„_ìœ ì˜ì°¬ = ìœ ì˜ì°¬_df[ìœ ì˜ì°¬_df['ì—°ë„'] == ì„ íƒ_ì—°ë„_ìœ ì˜ì°¬]
                
                # ê±°ëž˜ ìœ í˜• ë¶„ë¥˜
                # 1. ì œí’ˆ ì¶œê³  (íŒë§¤) - ìž…ê¸ˆ, ìˆ˜ë‹¹, íƒë°° ì œì™¸
                ì œí’ˆ_df = ì—°ë„_ìœ ì˜ì°¬[~ì—°ë„_ìœ ì˜ì°¬['í’ˆëª©'].str.contains('ìž…ê¸ˆ|ìˆ˜ë‹¹|íƒë°°', na=False)]
                ì œí’ˆ_df = ì œí’ˆ_df[ì œí’ˆ_df['ê³µê¸‰ê°€ì•¡'] > 0]  # ì–‘ìˆ˜ë§Œ (íŒë§¤)
                
                # 2. ìž…ê¸ˆ (ìœ ì˜ì°¬ì´ ë°›ì•„ì˜¨ ëˆ)
                ìž…ê¸ˆ_df = ì—°ë„_ìœ ì˜ì°¬[ì—°ë„_ìœ ì˜ì°¬['í’ˆëª©'].str.contains('ìž…ê¸ˆ', na=False)]
                
                # 3. ìˆ˜ë‹¹
                ìˆ˜ë‹¹_df = ì—°ë„_ìœ ì˜ì°¬[ì—°ë„_ìœ ì˜ì°¬['í’ˆëª©'].str.contains('ìˆ˜ë‹¹', na=False)]
                
                # ìš”ì•½ ì§€í‘œ
                ì´_ì œí’ˆì¶œê³  = ì œí’ˆ_df['ê³µê¸‰ê°€ì•¡'].sum()
                ì´_ìž…ê¸ˆ = ìž…ê¸ˆ_df['ê³µê¸‰ê°€ì•¡'].sum()
                ì´_ìˆ˜ë‹¹ = abs(ìˆ˜ë‹¹_df['ê³µê¸‰ê°€ì•¡'].sum())
                ì´_ë§ˆì§„ = ì œí’ˆ_df['ë§ˆì§„'].sum() if 'ë§ˆì§„' in ì œí’ˆ_df.columns else 0
                
                st.markdown(f"#### {ì„ íƒ_ì—°ë„_ìœ ì˜ì°¬}ë…„ ìœ ì˜ì°¬ ì‹¤ì  ìš”ì•½")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("ðŸ“¦ ì œí’ˆ ì¶œê³ ì•¡", f"{ì´_ì œí’ˆì¶œê³ :,.0f}ì›")
                with col2:
                    st.metric("ðŸ’° ìž…ê¸ˆì•¡", f"{ì´_ìž…ê¸ˆ:,.0f}ì›")
                with col3:
                    st.metric("ðŸ’µ ìˆ˜ë‹¹ ì§€ê¸‰", f"{ì´_ìˆ˜ë‹¹:,.0f}ì›")
                with col4:
                    st.metric("ðŸ“ˆ ë§ˆì§„", f"{ì´_ë§ˆì§„:,.0f}ì›")
                
                # ë¯¸ìˆ˜ê¸ˆ í‘œì‹œ - base_receivablesì—ì„œ ì§ì ‘ ê°€ì ¸ì˜´
                ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict = st.session_state.base_receivables_df.set_index('ê±°ëž˜ì²˜')['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].to_dict() if len(st.session_state.base_receivables_df) > 0 else {}
                ìœ ì˜ì°¬_ë¯¸ìˆ˜ê¸ˆ = ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict.get('ìœ ì˜ì°¬', 0)
                
                if ìœ ì˜ì°¬_ë¯¸ìˆ˜ê¸ˆ > 0:
                    st.markdown(f"""
                    <div style='background-color: #fff3e0; border: 2px solid #ff9800; border-radius: 8px; padding: 15px; margin: 15px 0;'>
                        <h3 style='color: #000000; margin: 0;'>âš ï¸ ìœ ì˜ì°¬ ë¯¸ìˆ˜ê¸ˆ: {ìœ ì˜ì°¬_ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›</h3>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # ì›”ë³„ ì‹¤ì 
                st.markdown("#### ðŸ“Š ì›”ë³„ ì‹¤ì ")
                
                ì›”ë³„_ì‹¤ì  = []
                for ì›” in range(1, 13):
                    ì›”_ì œí’ˆ = ì œí’ˆ_df[ì œí’ˆ_df['ì›”'] == ì›”]
                    ì›”_ìž…ê¸ˆ = ìž…ê¸ˆ_df[ìž…ê¸ˆ_df['ì›”'] == ì›”]
                    ì›”_ìˆ˜ë‹¹ = ìˆ˜ë‹¹_df[ìˆ˜ë‹¹_df['ì›”'] == ì›”]
                    
                    ì›”ë³„_ì‹¤ì .append({
                        'ì›”': f"{ì›”}ì›”",
                        'ì œí’ˆì¶œê³ ': ì›”_ì œí’ˆ['ê³µê¸‰ê°€ì•¡'].sum(),
                        'ìž…ê¸ˆ': ì›”_ìž…ê¸ˆ['ê³µê¸‰ê°€ì•¡'].sum(),
                        'ìˆ˜ë‹¹': abs(ì›”_ìˆ˜ë‹¹['ê³µê¸‰ê°€ì•¡'].sum()),
                        'ë§ˆì§„': ì›”_ì œí’ˆ['ë§ˆì§„'].sum() if 'ë§ˆì§„' in ì›”_ì œí’ˆ.columns else 0
                    })
                
                ì›”ë³„_df = pd.DataFrame(ì›”ë³„_ì‹¤ì )
                
                # ì°¨íŠ¸
                fig = go.Figure()
                fig.add_trace(go.Bar(name='ì œí’ˆì¶œê³ ', x=ì›”ë³„_df['ì›”'], y=ì›”ë³„_df['ì œí’ˆì¶œê³ '], marker_color='#1976D2'))
                fig.add_trace(go.Bar(name='ìž…ê¸ˆ', x=ì›”ë³„_df['ì›”'], y=ì›”ë³„_df['ìž…ê¸ˆ'], marker_color='#43A047'))
                fig.add_trace(go.Scatter(name='ë§ˆì§„', x=ì›”ë³„_df['ì›”'], y=ì›”ë³„_df['ë§ˆì§„'], mode='lines+markers', line=dict(color='#FF5722', width=3)))
                fig.update_layout(barmode='group', height=400, title=f'{ì„ íƒ_ì—°ë„_ìœ ì˜ì°¬}ë…„ ì›”ë³„ ì‹¤ì ')
                st.plotly_chart(fig, use_container_width=True)
                
                # í…Œì´ë¸”
                display_ì›”ë³„ = ì›”ë³„_df.copy()
                for col in ['ì œí’ˆì¶œê³ ', 'ìž…ê¸ˆ', 'ìˆ˜ë‹¹', 'ë§ˆì§„']:
                    display_ì›”ë³„[col] = display_ì›”ë³„[col].apply(lambda x: f"{x:,.0f}")
                st.dataframe(display_ì›”ë³„, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # ì œí’ˆë³„ íŒë§¤ ë‚´ì—­
                st.markdown("#### ðŸ“¦ ì œí’ˆë³„ íŒë§¤ ë‚´ì—­")
                
                if len(ì œí’ˆ_df) > 0:
                    ì œí’ˆë³„ = ì œí’ˆ_df.groupby('í’ˆëª©').agg({
                        'ìˆ˜ëŸ‰': 'sum',
                        'ê³µê¸‰ê°€ì•¡': 'sum',
                        'ë§ˆì§„': 'sum'
                    }).reset_index()
                    ì œí’ˆë³„ = ì œí’ˆë³„.sort_values('ê³µê¸‰ê°€ì•¡', ascending=False)
                    ì œí’ˆë³„['ë§ˆì§„ìœ¨'] = (ì œí’ˆë³„['ë§ˆì§„'] / ì œí’ˆë³„['ê³µê¸‰ê°€ì•¡'] * 100).round(1)
                    
                    display_ì œí’ˆ = ì œí’ˆë³„.copy()
                    display_ì œí’ˆ['ìˆ˜ëŸ‰'] = display_ì œí’ˆ['ìˆ˜ëŸ‰'].apply(lambda x: f"{x:,.0f}")
                    display_ì œí’ˆ['ê³µê¸‰ê°€ì•¡'] = display_ì œí’ˆ['ê³µê¸‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}")
                    display_ì œí’ˆ['ë§ˆì§„'] = display_ì œí’ˆ['ë§ˆì§„'].apply(lambda x: f"{x:,.0f}")
                    display_ì œí’ˆ['ë§ˆì§„ìœ¨'] = display_ì œí’ˆ['ë§ˆì§„ìœ¨'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(display_ì œí’ˆ, use_container_width=True, hide_index=True, height=400)
                
                st.markdown("---")
                
                # ìž…ê¸ˆ ë‚´ì—­ (ì–´ë””ì„œ ë°›ì•„ì˜¨ ëˆì¸ì§€)
                st.markdown("#### ðŸ’° ìž…ê¸ˆ ë‚´ì—­ (ìœ ì˜ì°¬ì´ ë°›ì•„ì˜¨ ëˆ)")
                
                if len(ìž…ê¸ˆ_df) > 0:
                    ìž…ê¸ˆ_í‘œì‹œ = ìž…ê¸ˆ_df[['ë‚ ì§œ', 'í’ˆëª©', 'ê³µê¸‰ê°€ì•¡']].copy()
                    ìž…ê¸ˆ_í‘œì‹œ = ìž…ê¸ˆ_í‘œì‹œ.sort_values('ë‚ ì§œ', ascending=False)
                    ìž…ê¸ˆ_í‘œì‹œ['ë‚ ì§œ'] = ìž…ê¸ˆ_í‘œì‹œ['ë‚ ì§œ'].dt.strftime('%Y-%m-%d')
                    ìž…ê¸ˆ_í‘œì‹œ['ê³µê¸‰ê°€ì•¡'] = ìž…ê¸ˆ_í‘œì‹œ['ê³µê¸‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}")
                    
                    st.dataframe(ìž…ê¸ˆ_í‘œì‹œ.head(30), use_container_width=True, hide_index=True)

# ==================== í’ˆëª© ê´€ë¦¬ ====================
elif menu == "ðŸ“¦ í’ˆëª© ê´€ë¦¬":
    st.title("ðŸ“¦ í’ˆëª© ê´€ë¦¬")
    
    products_df = st.session_state.products_df
    ledger_df = st.session_state.ledger_df
    
    # íƒ­ ìƒì„±
    tab1, tab2, tab3 = st.tabs(["ðŸ“‹ í’ˆëª© ëª©ë¡", "âž• í’ˆëª© ì¶”ê°€", "ðŸ” í’ˆëª© ê²€ìƒ‰"])
    
    # ===== íƒ­1: í’ˆëª© ëª©ë¡ (3ë‹¨ ë ˆì´ì•„ì›ƒ) =====
    with tab1:
        if len(products_df) > 0:
            # ========== 3ë‹¨ ë ˆì´ì•„ì›ƒ: ì¹´í…Œê³ ë¦¬ | í’ˆëª© | ìƒì„¸ì •ë³´ ==========
            col_category, col_product, col_detail = st.columns([1, 1.5, 2.5])
            
            # ========== 1ë‹¨: ì¹´í…Œê³ ë¦¬ ì„ íƒ ==========
            with col_category:
                st.markdown("### ðŸ“‚ ì¹´í…Œê³ ë¦¬")
                
                # NaN ê°’ ì œê±° í›„ ì •ë ¬
                ì¹´í…Œê³ ë¦¬_unique = products_df['ì¹´í…Œê³ ë¦¬'].dropna().unique().tolist()
                ì¹´í…Œê³ ë¦¬_list = ["ì „ì²´"] + sorted([x for x in ì¹´í…Œê³ ë¦¬_unique if x])
                
                # ì ˆë‹¨ì„ì´ ìžˆìœ¼ë©´ ê¸°ë³¸ ì„ íƒ
                ê¸°ë³¸_ì¸ë±ìŠ¤ = ì¹´í…Œê³ ë¦¬_list.index("ì ˆë‹¨ì„") if "ì ˆë‹¨ì„" in ì¹´í…Œê³ ë¦¬_list else 0
                
                ì„ íƒì¹´í…Œê³ ë¦¬ = st.radio("", ì¹´í…Œê³ ë¦¬_list, index=ê¸°ë³¸_ì¸ë±ìŠ¤, label_visibility="collapsed")
                
                st.markdown("---")
                
                # ì¹´í…Œê³ ë¦¬ë³„ ê°œìˆ˜ í‘œì‹œ
                if ì„ íƒì¹´í…Œê³ ë¦¬ == "ì „ì²´":
                    st.info(f"ðŸ“¦ ì „ì²´ {len(products_df)}ê°œ í’ˆëª©")
                else:
                    ê°œìˆ˜ = len(products_df[products_df['ì¹´í…Œê³ ë¦¬'] == ì„ íƒì¹´í…Œê³ ë¦¬])
                    st.info(f"ðŸ“¦ {ê°œìˆ˜}ê°œ í’ˆëª©")
            
            # ========== 2ë‹¨: í’ˆëª© ì„ íƒ ==========
            with col_product:
                st.markdown("### ðŸ“¦ í’ˆëª© ì„ íƒ")
                
                # ì¹´í…Œê³ ë¦¬ í•„í„°ë§
                if ì„ íƒì¹´í…Œê³ ë¦¬ != "ì „ì²´":
                    filtered_df = products_df[products_df['ì¹´í…Œê³ ë¦¬'] == ì„ íƒì¹´í…Œê³ ë¦¬].copy()
                else:
                    filtered_df = products_df.copy()
                
                # ìµœê·¼ 6ê°œì›” ê±°ëž˜ íšŸìˆ˜ ê¸°ì¤€ ì •ë ¬
                ê¸°ì¤€ì¼_6ê°œì›” = get_kst_now() - timedelta(days=180)
                
                if len(ledger_df) > 0:
                    ìµœê·¼ê±°ëž˜ = ledger_df[ledger_df['ë‚ ì§œ'] >= ê¸°ì¤€ì¼_6ê°œì›”]
                    í’ˆëª©ë³„_ê±°ëž˜ìˆ˜ = ìµœê·¼ê±°ëž˜.groupby('í’ˆëª©').size().to_dict()
                    
                    filtered_df['ìµœê·¼ê±°ëž˜ìˆ˜'] = filtered_df['í’ˆëª©ëª…'].apply(
                        lambda x: sum(cnt for í’ˆëª©, cnt in í’ˆëª©ë³„_ê±°ëž˜ìˆ˜.items() if str(x) in str(í’ˆëª©))
                    )
                    filtered_df = filtered_df.sort_values('ìµœê·¼ê±°ëž˜ìˆ˜', ascending=False)
                
                if len(filtered_df) > 0:
                    # í’ˆëª© ë¦¬ìŠ¤íŠ¸ë¥¼ ë¼ë””ì˜¤ ë²„íŠ¼ìœ¼ë¡œ
                    í’ˆëª©_ì˜µì…˜ = []
                    for _, row in filtered_df.iterrows():
                        ì˜µì…˜ = f"{row['í’ˆëª©ëª…']}"
                        if pd.notna(row['ê·œê²©']):
                            ì˜µì…˜ += f" ({row['ê·œê²©']})"
                        í’ˆëª©_ì˜µì…˜.append((ì˜µì…˜, row['í’ˆëª©ì½”ë“œ']))
                    
                    # ì„ íƒ ìƒíƒœ ì €ìž¥
                    if 'selected_product' not in st.session_state:
                        st.session_state.selected_product = None
                    
                    ì„ íƒëœ_ì¸ë±ìŠ¤ = 0
                    if st.session_state.selected_product:
                        try:
                            ì„ íƒëœ_ì¸ë±ìŠ¤ = [x[1] for x in í’ˆëª©_ì˜µì…˜].index(st.session_state.selected_product)
                        except:
                            ì„ íƒëœ_ì¸ë±ìŠ¤ = 0
                    
                    ì„ íƒí’ˆëª© = st.radio(
                        "",
                        range(len(í’ˆëª©_ì˜µì…˜)),
                        format_func=lambda x: í’ˆëª©_ì˜µì…˜[x][0],
                        index=ì„ íƒëœ_ì¸ë±ìŠ¤,
                        label_visibility="collapsed"
                    )
                    
                    if ì„ íƒí’ˆëª© is not None:
                        st.session_state.selected_product = í’ˆëª©_ì˜µì…˜[ì„ íƒí’ˆëª©][1]
                else:
                    st.warning("í•´ë‹¹ ì¹´í…Œê³ ë¦¬ì— í’ˆëª©ì´ ì—†ìŠµë‹ˆë‹¤.")
                    st.session_state.selected_product = None
            
            # ========== 3ë‹¨: í’ˆëª© ìƒì„¸ ì •ë³´ ==========
            with col_detail:
                if st.session_state.selected_product:
                    í’ˆëª©ì½”ë“œ = st.session_state.selected_product
                    í’ˆëª©ì •ë³´ = products_df[products_df['í’ˆëª©ì½”ë“œ'] == í’ˆëª©ì½”ë“œ].iloc[0]
                    
                    st.markdown("### ðŸ“Š í’ˆëª© ìƒì„¸ ì •ë³´")
                    
                    # ê¸°ë³¸ ì •ë³´
                    st.markdown("#### ðŸ“¦ ê¸°ë³¸ ì •ë³´")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**í’ˆëª©ì½”ë“œ:** `{í’ˆëª©ì •ë³´['í’ˆëª©ì½”ë“œ']}`")
                        st.markdown(f"**í’ˆëª©ëª…:** **{í’ˆëª©ì •ë³´['í’ˆëª©ëª…']}**")
                    with col2:
                        st.markdown(f"**ì¹´í…Œê³ ë¦¬:** {í’ˆëª©ì •ë³´['ì¹´í…Œê³ ë¦¬']}")
                        st.markdown(f"**ê·œê²©:** {í’ˆëª©ì •ë³´['ê·œê²©']}")
                    
                    st.markdown("---")
                    
                    # ì´ í’ˆëª©ì˜ ê±°ëž˜ ë‚´ì—­ í•„í„°ë§
                    í’ˆëª©ëª… = í’ˆëª©ì •ë³´['í’ˆëª©ëª…']
                    í’ˆëª©_ê±°ëž˜ = ledger_df[ledger_df['í’ˆëª©'].str.contains(í’ˆëª©ëª…, na=False)]
                    
                    if len(í’ˆëª©_ê±°ëž˜) > 0:
                        # êµ¬ë§¤ ê±°ëž˜ (ê³µê¸‰ê°€ì•¡ < 0 = ë‚´ê°€ ë§¤ìž…)
                        êµ¬ë§¤_ê±°ëž˜ = í’ˆëª©_ê±°ëž˜[í’ˆëª©_ê±°ëž˜['ê³µê¸‰ê°€ì•¡'] < 0]
                        
                        # íŒë§¤ ê±°ëž˜ (ê³µê¸‰ê°€ì•¡ > 0 = ë‚´ê°€ íŒë§¤, ìž…ê¸ˆ/ì¶œê¸ˆ ì œì™¸)
                        íŒë§¤_ê±°ëž˜ = í’ˆëª©_ê±°ëž˜[(í’ˆëª©_ê±°ëž˜['ê³µê¸‰ê°€ì•¡'] > 0) & (~í’ˆëª©_ê±°ëž˜['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ|ì¶œê¸ˆ', na=False))]
                        
                        # ðŸ’° êµ¬ë§¤ ì •ë³´
                        st.markdown("#### ðŸ’° êµ¬ë§¤ ì •ë³´ (ë‚´ê°€ ì‚¬ëŠ” ê°€ê²©)")
                        
                        if len(êµ¬ë§¤_ê±°ëž˜) > 0:
                            í‰ê· _êµ¬ë§¤ê°€ = êµ¬ë§¤_ê±°ëž˜['ë‹¨ê°€'].mean()
                            ìµœì €_êµ¬ë§¤ê°€ = êµ¬ë§¤_ê±°ëž˜['ë‹¨ê°€'].min()
                            ìµœê³ _êµ¬ë§¤ê°€ = êµ¬ë§¤_ê±°ëž˜['ë‹¨ê°€'].max()
                            ì´_êµ¬ë§¤ìˆ˜ëŸ‰ = êµ¬ë§¤_ê±°ëž˜['ìˆ˜ëŸ‰'].sum()
                            
                            # ìµœì €ê°€/ìµœê³ ê°€ ê±°ëž˜ì²˜
                            ìµœì €ê°€_row = êµ¬ë§¤_ê±°ëž˜[êµ¬ë§¤_ê±°ëž˜['ë‹¨ê°€'] == ìµœì €_êµ¬ë§¤ê°€].iloc[0]
                            ìµœê³ ê°€_row = êµ¬ë§¤_ê±°ëž˜[êµ¬ë§¤_ê±°ëž˜['ë‹¨ê°€'] == ìµœê³ _êµ¬ë§¤ê°€].iloc[0]
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("í‰ê·  êµ¬ë§¤ê°€", f"{í‰ê· _êµ¬ë§¤ê°€:,.0f}ì›")
                            with col2:
                                st.metric("ìµœì €ê°€", f"{ìµœì €_êµ¬ë§¤ê°€:,.0f}ì›")
                            with col3:
                                st.metric("ìµœê³ ê°€", f"{ìµœê³ _êµ¬ë§¤ê°€:,.0f}ì›")
                            
                            st.markdown(f"""
                            - **ìµœì €ê°€ ê±°ëž˜ì²˜:** {ìµœì €ê°€_row['ê±°ëž˜ì²˜']} ({ìµœì €ê°€_row['ë‚ ì§œ'].strftime('%m/%d')})
                            - **ìµœê³ ê°€ ê±°ëž˜ì²˜:** {ìµœê³ ê°€_row['ê±°ëž˜ì²˜']} ({ìµœê³ ê°€_row['ë‚ ì§œ'].strftime('%m/%d')})
                            - **ì´ êµ¬ë§¤ íšŸìˆ˜:** {len(êµ¬ë§¤_ê±°ëž˜)}ê±´
                            - **ì´ êµ¬ë§¤ ìˆ˜ëŸ‰:** {ì´_êµ¬ë§¤ìˆ˜ëŸ‰:,.0f}ê°œ
                            """)
                        else:
                            st.info("êµ¬ë§¤ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
                        
                        st.markdown("---")
                        
                        # ðŸ¢ íŒë§¤ í˜„í™©
                        st.markdown("#### ðŸ¢ íŒë§¤ í˜„í™© (ë‚´ê°€ íŒ ê±°ëž˜ì²˜)")
                        
                        if len(íŒë§¤_ê±°ëž˜) > 0:
                            # ë‹¹ì›” íŒë§¤ìˆ˜ëŸ‰
                            í˜„ìž¬ì›” = get_kst_now().month
                            ë‹¹ì›”_íŒë§¤ = íŒë§¤_ê±°ëž˜[íŒë§¤_ê±°ëž˜['ë‚ ì§œ'].dt.month == í˜„ìž¬ì›”]
                            ë‹¹ì›”_íŒë§¤ìˆ˜ëŸ‰ = ë‹¹ì›”_íŒë§¤['ìˆ˜ëŸ‰'].sum()
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("ë‹¹ì›” íŒë§¤ìˆ˜ëŸ‰", f"{ë‹¹ì›”_íŒë§¤ìˆ˜ëŸ‰:,.0f}ê°œ", f"{get_kst_now().month}ì›”")
                            with col2:
                                st.metric("ì´ íŒë§¤ìˆ˜ëŸ‰", f"{íŒë§¤_ê±°ëž˜['ìˆ˜ëŸ‰'].sum():,.0f}ê°œ")
                            
                            # ìµœê·¼ íŒë§¤ ê±°ëž˜ì²˜ (ìµœê·¼ 5ê±´)
                            st.markdown("**ìµœê·¼ íŒë§¤ ê±°ëž˜ì²˜:**")
                            ìµœê·¼_íŒë§¤ = íŒë§¤_ê±°ëž˜.sort_values('ë‚ ì§œ', ascending=False).head(5)
                            
                            for idx, row in ìµœê·¼_íŒë§¤.iterrows():
                                st.markdown(f"- **{row['ê±°ëž˜ì²˜']}** - {row['ìˆ˜ëŸ‰']:,.0f}ê°œ ({row['ë‚ ì§œ'].strftime('%m/%d')})")
                        else:
                            st.info("íŒë§¤ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
                        
                        st.markdown("---")
                        
                        # ðŸ“… ìµœê·¼ ê±°ëž˜ ë‚´ì—­
                        st.markdown("#### ðŸ“… ìµœê·¼ ê±°ëž˜ ë‚´ì—­ (ìµœê·¼ 10ê±´)")
                        
                        ìµœê·¼_ê±°ëž˜ = í’ˆëª©_ê±°ëž˜.sort_values('ë‚ ì§œ', ascending=False).head(10)
                        
                        # ê±°ëž˜ ë‚´ì—­ì„ í‘œë¡œ í‘œì‹œ
                        display_df = ìµœê·¼_ê±°ëž˜[['ë‚ ì§œ', 'ê±°ëž˜ì²˜', 'ì°¸ì¡°', 'ìˆ˜ëŸ‰', 'ë‹¨ê°€']].copy()
                        display_df['ë‚ ì§œ'] = display_df['ë‚ ì§œ'].dt.strftime('%Y-%m-%d')
                        display_df['êµ¬ë¶„'] = display_df['ì°¸ì¡°'].apply(lambda x: 'êµ¬ë§¤' if 'ì™¸ìž…' in x else 'íŒë§¤' if 'ì™¸ì¶œ' in x else x)
                        display_df['ìˆ˜ëŸ‰'] = display_df['ìˆ˜ëŸ‰'].apply(lambda x: f"{x:,.0f}ê°œ")
                        display_df['ë‹¨ê°€'] = display_df['ë‹¨ê°€'].apply(lambda x: f"{x:,.0f}ì›")
                        display_df = display_df[['ë‚ ì§œ', 'ê±°ëž˜ì²˜', 'êµ¬ë¶„', 'ìˆ˜ëŸ‰', 'ë‹¨ê°€']]
                        
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        
                    else:
                        st.info("ì´ í’ˆëª©ì˜ ê±°ëž˜ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
                else:
                    st.info("ðŸ‘ˆ ì¢Œì¸¡ì—ì„œ í’ˆëª©ì„ ì„ íƒí•˜ì„¸ìš”.")
        else:
            st.info("ë“±ë¡ëœ í’ˆëª©ì´ ì—†ìŠµë‹ˆë‹¤. 'í’ˆëª© ì¶”ê°€' íƒ­ì—ì„œ í’ˆëª©ì„ ì¶”ê°€í•˜ì„¸ìš”.")
    
    # ===== íƒ­2: í’ˆëª© ì¶”ê°€ =====
    with tab2:
        st.markdown("### âž• ìƒˆ í’ˆëª© ì¶”ê°€")
        
        col1, col2 = st.columns(2)
        
        with col1:
            ìƒˆí’ˆëª©ì½”ë“œ = st.text_input("í’ˆëª©ì½”ë“œ", placeholder="ì˜ˆ: P-001")
            ìƒˆí’ˆëª©ëª… = st.text_input("í’ˆëª©ëª…", placeholder="ì˜ˆ: TURBO Premium ì ˆë‹¨ì„")
        
        with col2:
            ìƒˆì¹´í…Œê³ ë¦¬ = st.text_input("ì¹´í…Œê³ ë¦¬", placeholder="ì˜ˆ: ì ˆë‹¨ì„")
            ìƒˆê·œê²© = st.text_input("ê·œê²©", placeholder="ì˜ˆ: 4ì¸ì¹˜")
        
        if st.button("ðŸ’¾ í’ˆëª© ì¶”ê°€", type="primary", use_container_width=True):
            if not ìƒˆí’ˆëª©ì½”ë“œ or not ìƒˆí’ˆëª©ëª…:
                st.error("í’ˆëª©ì½”ë“œì™€ í’ˆëª©ëª…ì€ í•„ìˆ˜ìž…ë‹ˆë‹¤!")
            elif ìƒˆí’ˆëª©ì½”ë“œ in products_df['í’ˆëª©ì½”ë“œ'].values:
                st.error(f"í’ˆëª©ì½”ë“œ '{ìƒˆí’ˆëª©ì½”ë“œ}'ëŠ” ì´ë¯¸ ì¡´ìž¬í•©ë‹ˆë‹¤!")
            else:
                new_row = pd.DataFrame([{
                    'í’ˆëª©ì½”ë“œ': ìƒˆí’ˆëª©ì½”ë“œ,
                    'í’ˆëª©ëª…': ìƒˆí’ˆëª©ëª…,
                    'ì¹´í…Œê³ ë¦¬': ìƒˆì¹´í…Œê³ ë¦¬,
                    'ê·œê²©': ìƒˆê·œê²©
                }])
                st.session_state.products_df = pd.concat([products_df, new_row], ignore_index=True)
                save_products()
                st.success(f"âœ… í’ˆëª© '{ìƒˆí’ˆëª©ëª…}' (ì½”ë“œ: {ìƒˆí’ˆëª©ì½”ë“œ})ì´ ì¶”ê°€ë˜ì—ˆìŠµë‹ˆë‹¤!")
                st.rerun()
    
    # ===== íƒ­3: í’ˆëª© ê²€ìƒ‰ =====
    with tab3:
        st.markdown("### ðŸ” í’ˆëª© ê²€ìƒ‰")
        
        ê²€ìƒ‰ì–´ = st.text_input("ê²€ìƒ‰ì–´ ìž…ë ¥", placeholder="í’ˆëª©ëª…, í’ˆëª©ì½”ë“œ, ì¹´í…Œê³ ë¦¬ë¡œ ê²€ìƒ‰...")
        
        if ê²€ìƒ‰ì–´:
            ê²€ìƒ‰ê²°ê³¼ = products_df[
                products_df['í’ˆëª©ì½”ë“œ'].str.contains(ê²€ìƒ‰ì–´, case=False, na=False) |
                products_df['í’ˆëª©ëª…'].str.contains(ê²€ìƒ‰ì–´, case=False, na=False) |
                products_df['ì¹´í…Œê³ ë¦¬'].str.contains(ê²€ìƒ‰ì–´, case=False, na=False) |
                products_df['ê·œê²©'].str.contains(ê²€ìƒ‰ì–´, case=False, na=False)
            ]
            
            if len(ê²€ìƒ‰ê²°ê³¼) > 0:
                st.success(f"ðŸ” {len(ê²€ìƒ‰ê²°ê³¼)}ê°œ í’ˆëª©ì„ ì°¾ì•˜ìŠµë‹ˆë‹¤!")
                st.dataframe(ê²€ìƒ‰ê²°ê³¼, use_container_width=True)
            else:
                st.warning("ê²€ìƒ‰ ê²°ê³¼ê°€ ì—†ìŠµë‹ˆë‹¤.")

# ==================== ìž¬ê³  ê´€ë¦¬ ====================
elif menu == "ðŸ“‹ ìž¬ê³  ê´€ë¦¬":
    st.title("ðŸ“‹ ìž¬ê³  ê´€ë¦¬")
    
    inventory_df = st.session_state.inventory_df
    ledger_df = st.session_state.ledger_df
    
    # íƒ­ êµ¬ì„±
    tab1, tab2, tab3, tab4 = st.tabs(["ðŸ“Š ìž¬ê³  í˜„í™©", "âž• ìž…ê³ /ì¶œê³ ", "âš ï¸ ìž¬ê³  ë¶€ì¡±", "ðŸ”§ ìž¬ê³  ì„¤ì •"])
    
    # ===== íƒ­1: ìž¬ê³  í˜„í™© =====
    with tab1:
        st.markdown("### ðŸ“Š í˜„ìž¬ ìž¬ê³  í˜„í™©")
        st.markdown(f"**ê¸°ì¤€ì¼:** 2025ë…„ 12ì›” 20ì¼")
        
        if len(inventory_df) > 0:
            # ê²€ìƒ‰ í•„í„°
            col1, col2 = st.columns([3, 1])
            with col1:
                ê²€ìƒ‰ì–´ = st.text_input("ðŸ” í’ˆëª© ê²€ìƒ‰", placeholder="í’ˆëª©ëª…ìœ¼ë¡œ ê²€ìƒ‰...")
            with col2:
                ì •ë ¬ê¸°ì¤€ = st.selectbox("ì •ë ¬", ["ìž¬ê³  ë§Žì€ ìˆœ", "ìž¬ê³  ì ì€ ìˆœ", "í’ˆëª©ëª…ìˆœ"])
            
            # í•„í„°ë§
            display_df = inventory_df.copy()
            if ê²€ìƒ‰ì–´:
                display_df = display_df[display_df['í’ˆëª©ëª…'].str.contains(ê²€ìƒ‰ì–´, case=False, na=False)]
            
            # ì •ë ¬
            if ì •ë ¬ê¸°ì¤€ == "ìž¬ê³  ë§Žì€ ìˆœ":
                display_df = display_df.sort_values('í˜„ìž¬ìž¬ê³ ', ascending=False)
            elif ì •ë ¬ê¸°ì¤€ == "ìž¬ê³  ì ì€ ìˆœ":
                display_df = display_df.sort_values('í˜„ìž¬ìž¬ê³ ', ascending=True)
            else:
                display_df = display_df.sort_values('í’ˆëª©ëª…')
            
            # í†µê³„
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("ðŸ“¦ ì´ í’ˆëª© ìˆ˜", f"{len(inventory_df)}ê°œ")
            with col2:
                st.metric("ðŸ“Š ì´ ìž¬ê³  ìˆ˜ëŸ‰", f"{inventory_df['í˜„ìž¬ìž¬ê³ '].sum():,.0f}ê°œ")
            with col3:
                ì´í‰ê°€ì•¡ = inventory_df['ìž¬ê³ í‰ê°€ì•¡'].sum() if 'ìž¬ê³ í‰ê°€ì•¡' in inventory_df.columns else 0
                st.metric("ðŸ’° ì´ ìž¬ê³ í‰ê°€ì•¡", f"{ì´í‰ê°€ì•¡:,.0f}ì›")
            with col4:
                ìž¬ê³ ì—†ìŒ = len(inventory_df[inventory_df['í˜„ìž¬ìž¬ê³ '] <= 0])
                st.metric("âŒ ìž¬ê³  ì—†ìŒ", f"{ìž¬ê³ ì—†ìŒ}ê°œ")
            
            # ðŸ”¥ í•µì‹¬ ì œí’ˆ: 4ì¸ì¹˜/5ì¸ì¹˜ ì ˆë‹¨ì„ ìš”ì•½
            st.markdown("#### ðŸ”¥ í•µì‹¬ ì œí’ˆ (ì ˆë‹¨ì„)")
            
            # 4ì¸ì¹˜ ì ˆë‹¨ì„
            ì ˆë‹¨ì„_4ì¸ì¹˜ = inventory_df[inventory_df['í’ˆëª©ëª…'].str.contains('4.*ì¸ì¹˜|4"|4ì¸ì¹˜|@4|@ 4', na=False, regex=True)]
            ì ˆë‹¨ì„_4ì¸ì¹˜ = ì ˆë‹¨ì„_4ì¸ì¹˜[ì ˆë‹¨ì„_4ì¸ì¹˜['í’ˆëª©ëª…'].str.contains('ì ˆë‹¨ì„|ì ˆë‹¨', na=False)]
            
            # 5ì¸ì¹˜ ì ˆë‹¨ì„
            ì ˆë‹¨ì„_5ì¸ì¹˜ = inventory_df[inventory_df['í’ˆëª©ëª…'].str.contains('5.*ì¸ì¹˜|5"|5ì¸ì¹˜|@5|@ 5', na=False, regex=True)]
            ì ˆë‹¨ì„_5ì¸ì¹˜ = ì ˆë‹¨ì„_5ì¸ì¹˜[ì ˆë‹¨ì„_5ì¸ì¹˜['í’ˆëª©ëª…'].str.contains('ì ˆë‹¨ì„|ì ˆë‹¨', na=False)]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='background-color: #e3f2fd; border: 2px solid #1976d2; border-radius: 10px; padding: 15px; margin: 5px 0;'>
                    <h4 style='color: #000000; margin: 0 0 10px 0;'>ðŸ“¦ 4ì¸ì¹˜ ì ˆë‹¨ì„</h4>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("í’ˆëª© ìˆ˜", f"{len(ì ˆë‹¨ì„_4ì¸ì¹˜)}ê°œ")
                with c2:
                    st.metric("ìž¬ê³  ìˆ˜ëŸ‰", f"{ì ˆë‹¨ì„_4ì¸ì¹˜['í˜„ìž¬ìž¬ê³ '].sum():,.0f}ê°œ")
                with c3:
                    í‰ê°€ì•¡_4 = ì ˆë‹¨ì„_4ì¸ì¹˜['ìž¬ê³ í‰ê°€ì•¡'].sum() if 'ìž¬ê³ í‰ê°€ì•¡' in ì ˆë‹¨ì„_4ì¸ì¹˜.columns else 0
                    st.metric("í‰ê°€ì•¡", f"{í‰ê°€ì•¡_4:,.0f}ì›")
            
            with col2:
                st.markdown("""
                <div style='background-color: #fff3e0; border: 2px solid #ff9800; border-radius: 10px; padding: 15px; margin: 5px 0;'>
                    <h4 style='color: #000000; margin: 0 0 10px 0;'>ðŸ“¦ 5ì¸ì¹˜ ì ˆë‹¨ì„</h4>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("í’ˆëª© ìˆ˜", f"{len(ì ˆë‹¨ì„_5ì¸ì¹˜)}ê°œ")
                with c2:
                    st.metric("ìž¬ê³  ìˆ˜ëŸ‰", f"{ì ˆë‹¨ì„_5ì¸ì¹˜['í˜„ìž¬ìž¬ê³ '].sum():,.0f}ê°œ")
                with c3:
                    í‰ê°€ì•¡_5 = ì ˆë‹¨ì„_5ì¸ì¹˜['ìž¬ê³ í‰ê°€ì•¡'].sum() if 'ìž¬ê³ í‰ê°€ì•¡' in ì ˆë‹¨ì„_5ì¸ì¹˜.columns else 0
                    st.metric("í‰ê°€ì•¡", f"{í‰ê°€ì•¡_5:,.0f}ì›")
            
            st.markdown("---")
            
            # ìž¬ê³  ëª©ë¡ í‘œì‹œ (í’ˆëª©ëª…, ìž¬ê³ ìˆ˜ëŸ‰, ë§¤ìž…ë‹¨ê°€, ìž¬ê³ í‰ê°€ì•¡, ë§¤ìž…ì—…ì²´)
            í‘œì‹œ_ì»¬ëŸ¼ = ['í’ˆëª©ëª…', 'í˜„ìž¬ìž¬ê³ ', 'ë§¤ìž…ë‹¨ê°€', 'ìž¬ê³ í‰ê°€ì•¡', 'ë§¤ìž…ì—…ì²´']
            í‘œì‹œ_ì»¬ëŸ¼ = [col for col in í‘œì‹œ_ì»¬ëŸ¼ if col in display_df.columns]
            
            # ê¸ˆì•¡ í¬ë§·íŒ…
            display_formatted = display_df[í‘œì‹œ_ì»¬ëŸ¼].copy()
            if 'ë§¤ìž…ë‹¨ê°€' in display_formatted.columns:
                display_formatted['ë§¤ìž…ë‹¨ê°€'] = display_formatted['ë§¤ìž…ë‹¨ê°€'].apply(lambda x: f"{x:,.0f}ì›" if pd.notna(x) else "")
            if 'ìž¬ê³ í‰ê°€ì•¡' in display_formatted.columns:
                display_formatted['ìž¬ê³ í‰ê°€ì•¡'] = display_formatted['ìž¬ê³ í‰ê°€ì•¡'].apply(lambda x: f"{x:,.0f}ì›" if pd.notna(x) else "")
            
            display_formatted = display_formatted.rename(columns={'í˜„ìž¬ìž¬ê³ ': 'ìž¬ê³ ìˆ˜ëŸ‰'})
            
            st.dataframe(
                display_formatted,
                use_container_width=True,
                height=500
            )
            
            # ë‹¤ìš´ë¡œë“œ ë²„íŠ¼
            csv = inventory_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="ðŸ“¥ ìž¬ê³  ëª©ë¡ ë‹¤ìš´ë¡œë“œ (CSV)",
                data=csv,
                file_name="inventory_list.csv",
                mime="text/csv"
            )
        else:
            st.info("ë“±ë¡ëœ ìž¬ê³ ê°€ ì—†ìŠµë‹ˆë‹¤. 'ìž¬ê³  ì„¤ì •' íƒ­ì—ì„œ ê¸°ì´ˆ ìž¬ê³ ë¥¼ ë“±ë¡í•´ì£¼ì„¸ìš”.")
    
    # ===== íƒ­2: ìž…ê³ /ì¶œê³  =====
    with tab2:
        st.markdown("### âž• ìˆ˜ë™ ìž…ê³ /ì¶œê³ ")
        st.info("ðŸ’¡ ì¼ë°˜ ê±°ëž˜ ìž…ë ¥ ì‹œì—ëŠ” ìžë™ìœ¼ë¡œ ìž¬ê³ ê°€ ì°¨ê°ë©ë‹ˆë‹¤. ì´ í™”ë©´ì€ ìˆ˜ë™ ì¡°ì •ìš©ìž…ë‹ˆë‹¤.")
        
        if len(inventory_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### í’ˆëª© ì„ íƒ")
                í’ˆëª©_list = inventory_df['í’ˆëª©ëª…'].tolist()
                ì„ íƒ_í’ˆëª© = st.selectbox("í’ˆëª©", [""] + í’ˆëª©_list)
                
                if ì„ íƒ_í’ˆëª©:
                    í˜„ìž¬_ìž¬ê³  = inventory_df[inventory_df['í’ˆëª©ëª…'] == ì„ íƒ_í’ˆëª©]['í˜„ìž¬ìž¬ê³ '].values[0]
                    st.info(f"ðŸ“¦ í˜„ìž¬ ìž¬ê³ : **{í˜„ìž¬_ìž¬ê³ :,.0f}ê°œ**")
            
            with col2:
                st.markdown("#### ìˆ˜ëŸ‰ ìž…ë ¥")
                ìž…ì¶œê³ _ìœ í˜• = st.radio("ìœ í˜•", ["ìž…ê³  (+)", "ì¶œê³  (-)"], horizontal=True)
                ìˆ˜ëŸ‰ = st.number_input("ìˆ˜ëŸ‰", min_value=0, value=0, step=1)
                ì‚¬ìœ  = st.text_input("ì‚¬ìœ ", placeholder="ì˜ˆ: ìž¬ê³  ì‹¤ì‚¬ ì¡°ì •, íŒŒì† ë“±")
            
            if st.button("âœ… ì ìš©", type="primary", use_container_width=True):
                if ì„ íƒ_í’ˆëª© and ìˆ˜ëŸ‰ > 0:
                    idx = inventory_df[inventory_df['í’ˆëª©ëª…'] == ì„ íƒ_í’ˆëª©].index[0]
                    if ìž…ì¶œê³ _ìœ í˜• == "ìž…ê³  (+)":
                        st.session_state.inventory_df.loc[idx, 'í˜„ìž¬ìž¬ê³ '] += ìˆ˜ëŸ‰
                        st.success(f"âœ… {ì„ íƒ_í’ˆëª©} +{ìˆ˜ëŸ‰}ê°œ ìž…ê³  ì™„ë£Œ!")
                    else:
                        st.session_state.inventory_df.loc[idx, 'í˜„ìž¬ìž¬ê³ '] -= ìˆ˜ëŸ‰
                        st.success(f"âœ… {ì„ íƒ_í’ˆëª©} -{ìˆ˜ëŸ‰}ê°œ ì¶œê³  ì™„ë£Œ!")
                    save_inventory()
                    st.rerun()
                else:
                    st.error("í’ˆëª©ê³¼ ìˆ˜ëŸ‰ì„ ìž…ë ¥í•´ì£¼ì„¸ìš”.")
        else:
            st.warning("ìž¬ê³  ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
    
    # ===== íƒ­3: ìž¬ê³  ë¶€ì¡± =====
    with tab3:
        st.markdown("### âš ï¸ ìž¬ê³  ë¶€ì¡± ì•Œë¦¼")
        st.info("ðŸ’¡ ìµœê·¼ 10ê°œì›” ë‚´ ê±°ëž˜ëœ í’ˆëª©ë§Œ í‘œì‹œë©ë‹ˆë‹¤.")
        
        if len(inventory_df) > 0 and len(ledger_df) > 0:
            # ìµœê·¼ 10ê°œì›” ê±°ëž˜ í’ˆëª© í•„í„°ë§
            ê¸°ì¤€ì¼_10ê°œì›” = get_kst_now() - timedelta(days=300)
            
            ìµœê·¼ê±°ëž˜ = ledger_df[ledger_df['ë‚ ì§œ'] >= ê¸°ì¤€ì¼_10ê°œì›”]
            ìµœê·¼ê±°ëž˜_í’ˆëª© = ìµœê·¼ê±°ëž˜['í’ˆëª©'].dropna().unique().tolist()
            
            # í’ˆëª©ë³„ ê±°ëž˜ íšŸìˆ˜ ê³„ì‚°
            í’ˆëª©ë³„_ê±°ëž˜ìˆ˜ = ìµœê·¼ê±°ëž˜.groupby('í’ˆëª©').size().to_dict()
            
            # ìž¬ê³  ë¶€ì¡± ê¸°ì¤€ ì„¤ì •
            ë¶€ì¡±_ê¸°ì¤€ = st.slider("ìž¬ê³  ë¶€ì¡± ê¸°ì¤€ (ê°œ)", min_value=0, max_value=1000, value=100, step=10)
            
            # ìµœê·¼ 10ê°œì›” ê±°ëž˜ í’ˆëª© ì¤‘ ìž¬ê³  ë¶€ì¡± í’ˆëª©
            ë¶€ì¡±_df = inventory_df[inventory_df['í˜„ìž¬ìž¬ê³ '] <= ë¶€ì¡±_ê¸°ì¤€].copy()
            
            # ìµœê·¼ ê±°ëž˜ëœ í’ˆëª©ë§Œ í•„í„°ë§
            ë¶€ì¡±_df['ìµœê·¼ê±°ëž˜'] = ë¶€ì¡±_df['í’ˆëª©ëª…'].apply(
                lambda x: any(str(x) in str(í’ˆëª©) for í’ˆëª© in ìµœê·¼ê±°ëž˜_í’ˆëª©)
            )
            ë¶€ì¡±_df = ë¶€ì¡±_df[ë¶€ì¡±_df['ìµœê·¼ê±°ëž˜'] == True]
            
            # ê±°ëž˜ íšŸìˆ˜ ì¶”ê°€ ë° ì •ë ¬
            ë¶€ì¡±_df['ê±°ëž˜íšŸìˆ˜'] = ë¶€ì¡±_df['í’ˆëª©ëª…'].apply(
                lambda x: sum(cnt for í’ˆëª©, cnt in í’ˆëª©ë³„_ê±°ëž˜ìˆ˜.items() if str(x) in str(í’ˆëª©))
            )
            ë¶€ì¡±_df = ë¶€ì¡±_df.sort_values('ê±°ëž˜íšŸìˆ˜', ascending=False)
            
            if len(ë¶€ì¡±_df) > 0:
                st.error(f"âš ï¸ ìž¬ê³  ë¶€ì¡± í’ˆëª©: **{len(ë¶€ì¡±_df)}ê°œ** (ìµœê·¼ 10ê°œì›” ê±°ëž˜ í’ˆëª© ì¤‘)")
                
                for _, row in ë¶€ì¡±_df.iterrows():
                    ìž¬ê³  = row['í˜„ìž¬ìž¬ê³ ']
                    í’ˆëª© = row['í’ˆëª©ëª…']
                    ê±°ëž˜ìˆ˜ = row['ê±°ëž˜íšŸìˆ˜']
                    
                    if ìž¬ê³  <= 0:
                        st.markdown(f"âŒ **{í’ˆëª©}** - ìž¬ê³  ì—†ìŒ! (ê±°ëž˜ {ê±°ëž˜ìˆ˜}íšŒ)")
                    elif ìž¬ê³  <= ë¶€ì¡±_ê¸°ì¤€ / 2:
                        st.markdown(f"ðŸ”´ **{í’ˆëª©}** - {ìž¬ê³ :,.0f}ê°œ (ê¸´ê¸‰, ê±°ëž˜ {ê±°ëž˜ìˆ˜}íšŒ)")
                    else:
                        st.markdown(f"ðŸŸ¡ **{í’ˆëª©}** - {ìž¬ê³ :,.0f}ê°œ (ê±°ëž˜ {ê±°ëž˜ìˆ˜}íšŒ)")
            else:
                st.success(f"âœ… ìž¬ê³  {ë¶€ì¡±_ê¸°ì¤€}ê°œ ì´í•˜ì¸ í’ˆëª©ì´ ì—†ìŠµë‹ˆë‹¤!")
        else:
            st.info("ìž¬ê³  ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
    
    # ===== íƒ­4: ìž¬ê³  ì„¤ì • =====
    with tab4:
        st.markdown("### ðŸ”§ ìž¬ê³  ì„¤ì •")
        
        st.markdown("#### ðŸ“¥ ê¸°ì´ˆ ìž¬ê³  ì¼ê´„ ë“±ë¡")
        st.info("CSV íŒŒì¼ì„ ì—…ë¡œë“œí•˜ì—¬ ê¸°ì´ˆ ìž¬ê³ ë¥¼ ë“±ë¡í•  ìˆ˜ ìžˆìŠµë‹ˆë‹¤.")
        
        uploaded_file = st.file_uploader("ìž¬ê³  CSV íŒŒì¼ ì—…ë¡œë“œ", type=['csv'])
        
        if uploaded_file:
            try:
                new_inventory = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                st.success(f"âœ… {len(new_inventory)}ê°œ í’ˆëª© ë¡œë“œ ì™„ë£Œ!")
                st.dataframe(new_inventory.head(10))
                
                if st.button("ðŸ“¥ ìž¬ê³  ë°ì´í„° ì ìš©", type="primary"):
                    # ì»¬ëŸ¼ëª… ë§žì¶”ê¸°
                    if 'ìž¬ê³ ìˆ˜ëŸ‰' in new_inventory.columns:
                        new_inventory = new_inventory.rename(columns={'ìž¬ê³ ìˆ˜ëŸ‰': 'í˜„ìž¬ìž¬ê³ '})
                    if 'í˜„ìž¬ìž¬ê³ ' not in new_inventory.columns and 'ê¸°ì´ˆìž¬ê³ ' in new_inventory.columns:
                        new_inventory['í˜„ìž¬ìž¬ê³ '] = new_inventory['ê¸°ì´ˆìž¬ê³ ']
                    
                    # í•„ìˆ˜ ì»¬ëŸ¼ í™•ì¸
                    if 'í’ˆëª©ëª…' in new_inventory.columns and 'í˜„ìž¬ìž¬ê³ ' in new_inventory.columns:
                        new_inventory['ê¸°ì´ˆìž¬ê³ '] = new_inventory['í˜„ìž¬ìž¬ê³ ']
                        new_inventory['ê¸°ì¤€ì¼ìž'] = '2025-12-20'
                        if 'ì•ˆì „ìž¬ê³ ' not in new_inventory.columns:
                            new_inventory['ì•ˆì „ìž¬ê³ '] = 100
                        if 'ë‹¨ìœ„' not in new_inventory.columns:
                            new_inventory['ë‹¨ìœ„'] = 'ê°œ'
                        
                        st.session_state.inventory_df = new_inventory[['í’ˆëª©ëª…', 'ê¸°ì´ˆìž¬ê³ ', 'í˜„ìž¬ìž¬ê³ ', 'ê¸°ì¤€ì¼ìž', 'ì•ˆì „ìž¬ê³ ', 'ë‹¨ìœ„']]
                        save_inventory()
                        st.success("âœ… ìž¬ê³  ë°ì´í„°ê°€ ì ìš©ë˜ì—ˆìŠµë‹ˆë‹¤!")
                        st.rerun()
                    else:
                        st.error("CSV íŒŒì¼ì— 'í’ˆëª©ëª…'ê³¼ 'í˜„ìž¬ìž¬ê³ (ë˜ëŠ” ìž¬ê³ ìˆ˜ëŸ‰)' ì»¬ëŸ¼ì´ í•„ìš”í•©ë‹ˆë‹¤.")
            except Exception as e:
                st.error(f"íŒŒì¼ ì½ê¸° ì˜¤ë¥˜: {e}")
        
        st.markdown("---")
        st.markdown("#### ðŸ“Š í˜„ìž¬ ìž¬ê³  í†µê³„")
        if len(inventory_df) > 0:
            st.write(f"- ì´ í’ˆëª© ìˆ˜: {len(inventory_df)}ê°œ")
            st.write(f"- ì´ ìž¬ê³  ìˆ˜ëŸ‰: {inventory_df['í˜„ìž¬ìž¬ê³ '].sum():,.0f}ê°œ")
            st.write(f"- ê¸°ì¤€ì¼ìž: {inventory_df['ê¸°ì¤€ì¼ìž'].iloc[0] if len(inventory_df) > 0 else 'N/A'}")

# ==================== ê±°ëž˜ì²˜ ê´€ë¦¬ ====================
elif menu == "ðŸ‘¥ ê±°ëž˜ì²˜ ê´€ë¦¬":
    st.title("ðŸ‘¥ ê±°ëž˜ì²˜ ê´€ë¦¬")
    
    ledger_df = st.session_state.ledger_df
    base_recv_df = st.session_state.base_receivables_df
    
    # ê±°ëž˜ì²˜ ëª©ë¡ ì¶”ì¶œ
    ê±°ëž˜ì²˜_list = sorted(ledger_df['ê±°ëž˜ì²˜'].dropna().unique().tolist()) if len(ledger_df) > 0 else []
    
    # ========== êµ¬ë§¤ ì£¼ê¸° ë¶„ì„ í•¨ìˆ˜ ==========
    def êµ¬ë§¤ì£¼ê¸°_ë¶„ì„(ê±°ëž˜ì²˜ëª…, ledger_df):
        """ê±°ëž˜ì²˜ì˜ í’ˆëª©ë³„ êµ¬ë§¤ ì£¼ê¸° ë¶„ì„ (ê³ ê°ì´ êµ¬ë§¤í•˜ëŠ” ì£¼ê¸°)"""
        ê±°ëž˜ì²˜_df = ledger_df[ledger_df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜ëª…]
        # ë‚´ê°€ íŒë§¤í•œ ê²ƒ = ê³µê¸‰ê°€ì•¡ > 0
        íŒë§¤_df = ê±°ëž˜ì²˜_df[ê±°ëž˜ì²˜_df['ê³µê¸‰ê°€ì•¡'] > 0]
        # ìž…ê¸ˆ/ì¶œê¸ˆ ì œì™¸
        íŒë§¤_df = íŒë§¤_df[~íŒë§¤_df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ|ì¶œê¸ˆ', na=False)]
        
        if len(íŒë§¤_df) < 2:
            return []
        
        ê²°ê³¼ = []
        í’ˆëª©_list = íŒë§¤_df['í’ˆëª©'].unique()
        
        for í’ˆëª© in í’ˆëª©_list:
            if pd.isna(í’ˆëª©):
                continue
            í’ˆëª©_df = íŒë§¤_df[íŒë§¤_df['í’ˆëª©'] == í’ˆëª©].sort_values('ë‚ ì§œ')
            
            if len(í’ˆëª©_df) >= 2:
                # êµ¬ë§¤ì¼ ê°„ê²© ê³„ì‚°
                ë‚ ì§œë“¤ = í’ˆëª©_df['ë‚ ì§œ'].tolist()
                ê°„ê²©ë“¤ = []
                for i in range(1, len(ë‚ ì§œë“¤)):
                    ê°„ê²© = (ë‚ ì§œë“¤[i] - ë‚ ì§œë“¤[i-1]).days
                    if ê°„ê²© > 0:
                        ê°„ê²©ë“¤.append(ê°„ê²©)
                
                if ê°„ê²©ë“¤:
                    í‰ê· _ì£¼ê¸° = sum(ê°„ê²©ë“¤) / len(ê°„ê²©ë“¤)
                    ë§ˆì§€ë§‰_êµ¬ë§¤ì¼ = ë‚ ì§œë“¤[-1]
                    ë‹¤ìŒ_ì˜ˆìƒì¼ = ë§ˆì§€ë§‰_êµ¬ë§¤ì¼ + timedelta(days=í‰ê· _ì£¼ê¸°)
                    ë‚¨ì€_ì¼ìˆ˜ = (ë‹¤ìŒ_ì˜ˆìƒì¼ - get_kst_now()).days
                    
                    ê²°ê³¼.append({
                        'í’ˆëª©': í’ˆëª©[:30] + '...' if len(í’ˆëª©) > 30 else í’ˆëª©,
                        'í‰ê· ì£¼ê¸°': int(í‰ê· _ì£¼ê¸°),
                        'ë§ˆì§€ë§‰êµ¬ë§¤': ë§ˆì§€ë§‰_êµ¬ë§¤ì¼,
                        'ë‹¤ìŒì˜ˆìƒ': ë‹¤ìŒ_ì˜ˆìƒì¼,
                        'ë‚¨ì€ì¼ìˆ˜': ë‚¨ì€_ì¼ìˆ˜,
                        'êµ¬ë§¤íšŸìˆ˜': len(í’ˆëª©_df)
                    })
        
        # ë‚¨ì€ ì¼ìˆ˜ ê¸°ì¤€ ì •ë ¬ (ìž„ë°•í•œ ê²ƒ ë¨¼ì €)
        ê²°ê³¼.sort(key=lambda x: x['ë‚¨ì€ì¼ìˆ˜'])
        return ê²°ê³¼
    
    def íŒë§¤ê¸°ëŒ€ì¹˜_ê³„ì‚°(ê±°ëž˜ì²˜ëª…, ledger_df):
        """ê±°ëž˜ì²˜ì˜ íŒë§¤ ê¸°ëŒ€ì¹˜ ì ìˆ˜ ê³„ì‚°"""
        ê±°ëž˜ì²˜_df = ledger_df[ledger_df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜ëª…]
        # ë‚´ê°€ íŒë§¤í•œ ê²ƒ = ê³µê¸‰ê°€ì•¡ > 0
        íŒë§¤_df = ê±°ëž˜ì²˜_df[ê±°ëž˜ì²˜_df['ê³µê¸‰ê°€ì•¡'] > 0]
        # ìž…ê¸ˆ/ì¶œê¸ˆ ì œì™¸
        íŒë§¤_df = íŒë§¤_df[~íŒë§¤_df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ|ì¶œê¸ˆ', na=False)]
        
        if len(íŒë§¤_df) == 0:
            return 0, {}
        
        # ìµœê·¼ 3ê°œì›” ë°ì´í„°ë§Œ
        ìµœê·¼3ê°œì›” = get_kst_now() - timedelta(days=90)
        ìµœê·¼_íŒë§¤ = íŒë§¤_df[íŒë§¤_df['ë‚ ì§œ'] >= ìµœê·¼3ê°œì›”]
        
        # ì›”í‰ê·  êµ¬ë§¤ê¸ˆì•¡
        ì›”í‰ê· _ê¸ˆì•¡ = (ìµœê·¼_íŒë§¤['ê³µê¸‰ê°€ì•¡'].sum() + ìµœê·¼_íŒë§¤['ë¶€ê°€ì„¸'].sum()) / 3 if len(ìµœê·¼_íŒë§¤) > 0 else 0
        
        # êµ¬ë§¤ ë¹ˆë„ (ì›”í‰ê· )
        ì›”í‰ê· _íšŸìˆ˜ = len(ìµœê·¼_íŒë§¤) / 3
        
        # êµ¬ë§¤ ì£¼ê¸° ìž„ë°• í’ˆëª© ìˆ˜ (3ê°œì›” = 90ì¼ ë‚´)
        ì£¼ê¸°_ë¶„ì„ = êµ¬ë§¤ì£¼ê¸°_ë¶„ì„(ê±°ëž˜ì²˜ëª…, ledger_df)
        ìž„ë°•_í’ˆëª© = len([x for x in ì£¼ê¸°_ë¶„ì„ if x['ë‚¨ì€ì¼ìˆ˜'] <= 90])
        
        # ê¸°ëŒ€ì¹˜ ì ìˆ˜ ê³„ì‚° (0~100)
        ì ìˆ˜ = 0
        ì ìˆ˜ += min(ìž„ë°•_í’ˆëª© * 20, 40)  # ìž„ë°• í’ˆëª© (ìµœëŒ€ 40ì )
        ì ìˆ˜ += min(ì›”í‰ê· _ê¸ˆì•¡ / 100000, 30)  # ê¸ˆì•¡ (ìµœëŒ€ 30ì )
        ì ìˆ˜ += min(ì›”í‰ê· _íšŸìˆ˜ * 5, 30)  # ë¹ˆë„ (ìµœëŒ€ 30ì )
        
        ìƒì„¸ = {
            'ì›”í‰ê· ê¸ˆì•¡': ì›”í‰ê· _ê¸ˆì•¡,
            'ì›”í‰ê· íšŸìˆ˜': ì›”í‰ê· _íšŸìˆ˜,
            'ìž„ë°•í’ˆëª©ìˆ˜': ìž„ë°•_í’ˆëª©,
            'ì£¼ê¸°ë¶„ì„': ì£¼ê¸°_ë¶„ì„[:3] if ì£¼ê¸°_ë¶„ì„ else []  # ìƒìœ„ 3ê°œë§Œ
        }
        
        return min(ì ìˆ˜, 100), ìƒì„¸
    
    # ========== ê±°ëž˜ì²˜ ë¶„ë¥˜ í•¨ìˆ˜ ==========
    def ê±°ëž˜ì²˜_ë¶„ë¥˜(ledger_df):
        """ê±°ëž˜ì²˜ë¥¼ ë§¤ìž…/ê³ ê°ìœ¼ë¡œ ë¶„ë¥˜í•˜ê³  ìµœê·¼ ê±°ëž˜ì¼ ê¸°ì¤€ ì •ë ¬
        
        ë¶„ë¥˜ ê¸°ì¤€ (ê³µê¸‰ê°€ì•¡ ë¶€í˜¸):
        - ê³µê¸‰ê°€ì•¡ < 0 (ë§ˆì´ë„ˆìŠ¤): ë§¤ìž…ì—…ì²´ (ë‚´ê°€ êµ¬ìž…)
        - ê³µê¸‰ê°€ì•¡ > 0 (í”ŒëŸ¬ìŠ¤): ê³ ê°ì—…ì²´ (ë‚´ê°€ íŒë§¤)
        """
        # ìµœê·¼ 6ê°œì›” ë°ì´í„°ë§Œ ì‚¬ìš©
        ê¸°ì¤€ì¼_6ê°œì›” = get_kst_now() - timedelta(days=180)
        ìµœê·¼_ledger = ledger_df[ledger_df['ë‚ ì§œ'] >= ê¸°ì¤€ì¼_6ê°œì›”]
        
        ë§¤ìž…ì—…ì²´ = {}  # ë‚´ê°€ ì‚¬ëŠ” ê³³ (ê³µê¸‰ê°€ì•¡ ë§ˆì´ë„ˆìŠ¤)
        ê³ ê°ì—…ì²´ = {}  # ë‚´ê°€ íŒŒëŠ” ê³³ (ê³µê¸‰ê°€ì•¡ í”ŒëŸ¬ìŠ¤)
        
        for _, row in ìµœê·¼_ledger.iterrows():
            ê±°ëž˜ì²˜ = row['ê±°ëž˜ì²˜']
            ë‚ ì§œ = row['ë‚ ì§œ']
            ì°¸ì¡° = row['ì°¸ì¡°'] if pd.notna(row['ì°¸ì¡°']) else ''
            ê³µê¸‰ê°€ì•¡ = row['ê³µê¸‰ê°€ì•¡'] if pd.notna(row['ê³µê¸‰ê°€ì•¡']) else 0
            
            # ìž…ê¸ˆ/ì¶œê¸ˆì€ ì œì™¸ (ê±°ëž˜ì²˜ ë¶„ë¥˜ì—ì„œ)
            if 'ìž…ê¸ˆ' in ì°¸ì¡° or 'ì¶œê¸ˆ' in ì°¸ì¡°:
                continue
            
            # ê³µê¸‰ê°€ì•¡ ë¶€í˜¸ë¡œ ë¶„ë¥˜
            if ê³µê¸‰ê°€ì•¡ < 0:  # ë§ˆì´ë„ˆìŠ¤ = ë§¤ìž… (ë‚´ê°€ êµ¬ìž…)
                if ê±°ëž˜ì²˜ not in ë§¤ìž…ì—…ì²´ or ë‚ ì§œ > ë§¤ìž…ì—…ì²´[ê±°ëž˜ì²˜]:
                    ë§¤ìž…ì—…ì²´[ê±°ëž˜ì²˜] = ë‚ ì§œ
            elif ê³µê¸‰ê°€ì•¡ > 0:  # í”ŒëŸ¬ìŠ¤ = íŒë§¤ (ë‚´ê°€ íŒë§¤)
                if ê±°ëž˜ì²˜ not in ê³ ê°ì—…ì²´ or ë‚ ì§œ > ê³ ê°ì—…ì²´[ê±°ëž˜ì²˜]:
                    ê³ ê°ì—…ì²´[ê±°ëž˜ì²˜] = ë‚ ì§œ
        
        # 3ê°œì›” ê¸°ì¤€ìœ¼ë¡œ í™œì„±/íœ´ë©´ ë¶„ë¥˜
        ê¸°ì¤€ì¼ = get_kst_now() - timedelta(days=90)
        
        ë§¤ìž…_í™œì„± = [(k, v) for k, v in ë§¤ìž…ì—…ì²´.items() if v >= ê¸°ì¤€ì¼]
        ë§¤ìž…_íœ´ë©´ = [(k, v) for k, v in ë§¤ìž…ì—…ì²´.items() if v < ê¸°ì¤€ì¼]
        ê³ ê°_í™œì„± = [(k, v) for k, v in ê³ ê°ì—…ì²´.items() if v >= ê¸°ì¤€ì¼]
        ê³ ê°_íœ´ë©´ = [(k, v) for k, v in ê³ ê°ì—…ì²´.items() if v < ê¸°ì¤€ì¼]
        
        # ìµœê·¼ ê±°ëž˜ì¼ ê¸°ì¤€ ì •ë ¬ (ìµœì‹ ìˆœ)
        ë§¤ìž…_í™œì„±.sort(key=lambda x: x[1], reverse=True)
        ë§¤ìž…_íœ´ë©´.sort(key=lambda x: x[1], reverse=True)
        ê³ ê°_í™œì„±.sort(key=lambda x: x[1], reverse=True)
        ê³ ê°_íœ´ë©´.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'ë§¤ìž…_í™œì„±': ë§¤ìž…_í™œì„±,
            'ë§¤ìž…_íœ´ë©´': ë§¤ìž…_íœ´ë©´,
            'ê³ ê°_í™œì„±': ê³ ê°_í™œì„±,
            'ê³ ê°_íœ´ë©´': ê³ ê°_íœ´ë©´
        }
    
    # ê±°ëž˜ì²˜ ë¶„ë¥˜ ì‹¤í–‰
    ë¶„ë¥˜ëœ_ê±°ëž˜ì²˜ = ê±°ëž˜ì²˜_ë¶„ë¥˜(ledger_df) if len(ledger_df) > 0 else {'ë§¤ìž…_í™œì„±': [], 'ë§¤ìž…_íœ´ë©´': [], 'ê³ ê°_í™œì„±': [], 'ê³ ê°_íœ´ë©´': []}
    
    # ========== íƒ­ êµ¬ì„± (4ê°œ íƒ­) ==========
    tab1, tab2, tab3, tab4 = st.tabs(["ðŸŽ¯ ì˜¤ëŠ˜ì˜ ì˜ì—…", "ðŸ“¤ ê³ ê°ì—…ì²´", "ðŸ“¥ ë§¤ìž…ì—…ì²´", "âž• ê±°ëž˜ì²˜ ì¶”ê°€"])
    
    # ===== íƒ­1: ì˜¤ëŠ˜ì˜ ì˜ì—… ëŒ€ì‹œë³´ë“œ =====
    with tab1:
        st.markdown("### ðŸŽ¯ ì˜¤ëŠ˜ì˜ ì˜ì—… ëŒ€ì‹œë³´ë“œ")
        st.markdown(f"**{get_kst_now().strftime('%Yë…„ %mì›” %dì¼ %A')}** ê¸°ì¤€")
        
        # ì œì™¸í•  ê±°ëž˜ì²˜ (ì˜ì—…ì§ì›, ìœ„íƒíŒë§¤ ë“±)
        ì œì™¸_ê±°ëž˜ì²˜ = ['ìœ ì˜ì°¬']
        
        # ìµœê·¼ 6ê°œì›” ë°ì´í„°
        ê¸°ì¤€ì¼_6ê°œì›” = get_kst_now() - timedelta(days=180)
        ìµœê·¼6ê°œì›”_df = ledger_df[ledger_df['ë‚ ì§œ'] >= ê¸°ì¤€ì¼_6ê°œì›”]
        
        # 6ê°œì›” ë‚´ 2íšŒ ì´ìƒ ê±°ëž˜ + ë§¤ì¶œ ê³„ì‚°
        ê³ ê°_ë§¤ì¶œ = []
        for ê±°ëž˜ì²˜ in ledger_df['ê±°ëž˜ì²˜'].dropna().unique():
            if ê±°ëž˜ì²˜ in ì œì™¸_ê±°ëž˜ì²˜:
                continue
            
            ê±°ëž˜ì²˜_df = ìµœê·¼6ê°œì›”_df[ìµœê·¼6ê°œì›”_df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜]
            # íŒë§¤ ê±°ëž˜ë§Œ (ê³µê¸‰ê°€ì•¡ > 0, ìž…ê¸ˆ/ì¶œê¸ˆ ì œì™¸)
            íŒë§¤_df = ê±°ëž˜ì²˜_df[(ê±°ëž˜ì²˜_df['ê³µê¸‰ê°€ì•¡'] > 0) & (~ê±°ëž˜ì²˜_df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ|ì¶œê¸ˆ', na=False))]
            
            ê±°ëž˜íšŸìˆ˜ = len(íŒë§¤_df)
            if ê±°ëž˜íšŸìˆ˜ >= 2:  # 2íšŒ ì´ìƒ ê±°ëž˜
                ì´ë§¤ì¶œ = íŒë§¤_df['ê³µê¸‰ê°€ì•¡'].sum() + íŒë§¤_df['ë¶€ê°€ì„¸'].sum()
                ê³ ê°_ë§¤ì¶œ.append({
                    'ê±°ëž˜ì²˜': ê±°ëž˜ì²˜,
                    'ê±°ëž˜íšŸìˆ˜': ê±°ëž˜íšŸìˆ˜,
                    'ì´ë§¤ì¶œ': ì´ë§¤ì¶œ
                })
        
        # ë§¤ì¶œ ë†’ì€ ìˆœ ì •ë ¬
        ê³ ê°_ë§¤ì¶œ.sort(key=lambda x: x['ì´ë§¤ì¶œ'], reverse=True)
        
        if len(ê³ ê°_ë§¤ì¶œ) > 0:
            st.markdown("---")
            st.markdown("### ðŸ“ž ì˜¤ëŠ˜ ì—°ë½ ì¶”ì²œ TOP 5")
            st.caption("ðŸ’¡ ìµœê·¼ 6ê°œì›” ë‚´ 2íšŒ ì´ìƒ ê±°ëž˜, ë§¤ì¶œ ë†’ì€ ìˆœ")
            
            for i, item in enumerate(ê³ ê°_ë§¤ì¶œ[:5]):
                ê±°ëž˜ì²˜ëª… = item['ê±°ëž˜ì²˜']
                ì´ë§¤ì¶œ = item['ì´ë§¤ì¶œ']
                ê±°ëž˜íšŸìˆ˜ = item['ê±°ëž˜íšŸìˆ˜']
                
                # ë¯¸ìˆ˜ê¸ˆì€ base_receivablesì—ì„œ ì§ì ‘ ê°€ì ¸ì˜´ (ì»´ìž¥ë¶€ GULREST)
                ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict = base_recv_df.set_index('ê±°ëž˜ì²˜')['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].to_dict() if len(base_recv_df) > 0 else {}
                ë¯¸ìˆ˜ê¸ˆ = ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict.get(ê±°ëž˜ì²˜ëª…, 0)
                
                # êµ¬ë§¤ ì£¼ê¸° ìž„ë°• í’ˆëª© (ìµœê·¼ 6ê°œì›” ê±°ëž˜ í’ˆëª© ì¤‘)
                ì£¼ê¸°_ë¶„ì„ = êµ¬ë§¤ì£¼ê¸°_ë¶„ì„(ê±°ëž˜ì²˜ëª…, ledger_df)
                # ìµœê·¼ 6ê°œì›” ë‚´ ê±°ëž˜ëœ í’ˆëª©ë§Œ í•„í„°ë§
                ìµœê·¼_í’ˆëª© = ìµœê·¼6ê°œì›”_df[ìµœê·¼6ê°œì›”_df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜ëª…]['í’ˆëª©'].dropna().unique()
                ì£¼ê¸°_ë¶„ì„ = [x for x in ì£¼ê¸°_ë¶„ì„ if any(str(x['í’ˆëª©']) in str(p) for p in ìµœê·¼_í’ˆëª©)]
                
                ìž„ë°•_í’ˆëª©_í…ìŠ¤íŠ¸ = ""
                if ì£¼ê¸°_ë¶„ì„:
                    ìž„ë°• = ì£¼ê¸°_ë¶„ì„[0]
                    if ìž„ë°•['ë‚¨ì€ì¼ìˆ˜'] <= 0:
                        ìž„ë°•_í’ˆëª©_í…ìŠ¤íŠ¸ = f"ðŸ“¦ {ìž„ë°•['í’ˆëª©']} - êµ¬ë§¤ ì˜ˆìƒì¼ ì§€ë‚¨!"
                    elif ìž„ë°•['ë‚¨ì€ì¼ìˆ˜'] <= 14:
                        ìž„ë°•_í’ˆëª©_í…ìŠ¤íŠ¸ = f"ðŸ“¦ {ìž„ë°•['í’ˆëª©']} - {ìž„ë°•['ë‚¨ì€ì¼ìˆ˜']}ì¼ í›„ ì˜ˆìƒ"
                
                # ìˆœìœ„ë³„ ì•„ì´ì½˜
                ìˆœìœ„_ì•„ì´ì½˜ = ["ðŸ¥‡", "ðŸ¥ˆ", "ðŸ¥‰", "4ï¸âƒ£", "5ï¸âƒ£"][i]
                
                # ê¹”ë”í•œ ì¹´ë“œ ìŠ¤íƒ€ì¼
                with st.container():
                    col1, col2 = st.columns([2, 3])
                    with col1:
                        st.markdown(f"**{ìˆœìœ„_ì•„ì´ì½˜} {ê±°ëž˜ì²˜ëª…}**")
                    with col2:
                        st.markdown(f"ðŸ’° 6ê°œì›” ë§¤ì¶œ: **{ì´ë§¤ì¶œ:,.0f}ì›** | ê±°ëž˜ {ê±°ëž˜íšŸìˆ˜}íšŒ | ë¯¸ìˆ˜ê¸ˆ: {ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›")
                    
                    if ìž„ë°•_í’ˆëª©_í…ìŠ¤íŠ¸:
                        st.caption(ìž„ë°•_í’ˆëª©_í…ìŠ¤íŠ¸)
                    st.markdown("---")
            
            # êµ¬ë§¤ ì£¼ê¸° ìž„ë°• í’ˆëª© - TOP 5 ë‹¤ìŒ ì—…ì²´ (6~15ìœ„)
            st.markdown("### â° êµ¬ë§¤ ì£¼ê¸° ìž„ë°• (TOP 6~15 ì—…ì²´)")
            st.caption("ðŸ’¡ TOP 5 ë‹¤ìŒ ìˆœìœ„ ì—…ì²´ ì¤‘ ìž¬êµ¬ë§¤ ì˜ˆìƒ í’ˆëª©")
            
            ë‹¤ìŒ_ì—…ì²´ = ê³ ê°_ë§¤ì¶œ[5:15] if len(ê³ ê°_ë§¤ì¶œ) > 5 else []
            
            ëª¨ë“ _ìž„ë°• = []
            for item in ë‹¤ìŒ_ì—…ì²´:
                ê±°ëž˜ì²˜ = item['ê±°ëž˜ì²˜']
                ì£¼ê¸°_ë¶„ì„ = êµ¬ë§¤ì£¼ê¸°_ë¶„ì„(ê±°ëž˜ì²˜, ledger_df)
                # ìµœê·¼ 6ê°œì›” ë‚´ ê±°ëž˜ëœ í’ˆëª©ë§Œ í•„í„°ë§
                ìµœê·¼_í’ˆëª© = ìµœê·¼6ê°œì›”_df[ìµœê·¼6ê°œì›”_df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜]['í’ˆëª©'].dropna().unique()
                ì£¼ê¸°_ë¶„ì„ = [x for x in ì£¼ê¸°_ë¶„ì„ if any(str(x['í’ˆëª©']) in str(p) for p in ìµœê·¼_í’ˆëª©)]
                
                for í’ˆëª© in ì£¼ê¸°_ë¶„ì„:
                    if í’ˆëª©['ë‚¨ì€ì¼ìˆ˜'] <= 14:  # 2ì£¼ ì´ë‚´
                        ëª¨ë“ _ìž„ë°•.append({
                            'ê±°ëž˜ì²˜': ê±°ëž˜ì²˜,
                            'ë§¤ì¶œ': item['ì´ë§¤ì¶œ'],
                            **í’ˆëª©
                        })
            
            ëª¨ë“ _ìž„ë°•.sort(key=lambda x: x['ë‚¨ì€ì¼ìˆ˜'])
            
            if ëª¨ë“ _ìž„ë°•:
                ìž„ë°•_df = pd.DataFrame(ëª¨ë“ _ìž„ë°•[:15])  # ìƒìœ„ 15ê°œ
                ìž„ë°•_df['ë‹¤ìŒì˜ˆìƒ'] = pd.to_datetime(ìž„ë°•_df['ë‹¤ìŒì˜ˆìƒ']).dt.strftime('%m/%d')
                ìž„ë°•_df['ë§ˆì§€ë§‰êµ¬ë§¤'] = pd.to_datetime(ìž„ë°•_df['ë§ˆì§€ë§‰êµ¬ë§¤']).dt.strftime('%m/%d')
                ìž„ë°•_df['ìƒíƒœ'] = ìž„ë°•_df['ë‚¨ì€ì¼ìˆ˜'].apply(
                    lambda x: 'ðŸ”´ ì§€ë‚¨' if x <= 0 else 'ðŸŸ  ìž„ë°•' if x <= 3 else 'ðŸŸ¡ ì´ë²ˆì£¼' if x <= 7 else 'ðŸŸ¢ ì—¬ìœ '
                )
                
                display_df = ìž„ë°•_df[['ìƒíƒœ', 'ê±°ëž˜ì²˜', 'í’ˆëª©', 'í‰ê· ì£¼ê¸°', 'ë§ˆì§€ë§‰êµ¬ë§¤', 'ë‹¤ìŒì˜ˆìƒ', 'ë‚¨ì€ì¼ìˆ˜']]
                display_df.columns = ['ìƒíƒœ', 'ê±°ëž˜ì²˜', 'í’ˆëª©', 'ì£¼ê¸°', 'ë§ˆì§€ë§‰', 'ì˜ˆìƒì¼', 'D-day']
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("2ì£¼ ì´ë‚´ êµ¬ë§¤ ì˜ˆìƒ í’ˆëª©ì´ ì—†ìŠµë‹ˆë‹¤.")
        else:
            st.info("ê±°ëž˜ì²˜ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤. ê±°ëž˜ë¥¼ ìž…ë ¥í•˜ë©´ ìžë™ìœ¼ë¡œ ë¶„ì„ë©ë‹ˆë‹¤.")
    
    # ===== íƒ­2: ê³ ê°ì—…ì²´ (ë‚´ê°€ íŒë§¤í•˜ëŠ” ê³³) =====
    with tab2:
        st.markdown("### ðŸ“¤ ê³ ê°ì—…ì²´")
        st.markdown("*ë‚´ê°€ ë¬¼ê±´ì„ íŒë§¤í•˜ëŠ” ì—…ì²´*")
        
        # ê³ ê°ì—…ì²´ = ê³µê¸‰ê°€ì•¡ì´ í”ŒëŸ¬ìŠ¤ì¸ ê±°ëž˜
        ê³ ê°_í™œì„± = ë¶„ë¥˜ëœ_ê±°ëž˜ì²˜['ê³ ê°_í™œì„±']
        ê³ ê°_íœ´ë©´ = ë¶„ë¥˜ëœ_ê±°ëž˜ì²˜['ê³ ê°_íœ´ë©´']
        
        # ì „ì²´ ê³ ê° ëª©ë¡ (í™œì„± + íœ´ë©´)
        ì „ì²´_ê³ ê° = []
        for x in ê³ ê°_í™œì„±:
            ì „ì²´_ê³ ê°.append((x[0], x[1], "ðŸŸ¢"))
        for x in ê³ ê°_íœ´ë©´:
            ì „ì²´_ê³ ê°.append((x[0], x[1], "âšª"))
        
        if len(ì „ì²´_ê³ ê°) > 0:
            # ê³ ê° ì„ íƒ ë“œë¡­ë‹¤ìš´
            ê³ ê°_ì˜µì…˜ = [f"{x[2]} {x[0]} ({x[1].strftime('%m/%d')})" for x in ì „ì²´_ê³ ê°]
            ì„ íƒ_idx = st.selectbox(
                f"ê³ ê° ì„ íƒ (ðŸŸ¢í™œì„± {len(ê³ ê°_í™œì„±)}ê°œ / âšªíœ´ë©´ {len(ê³ ê°_íœ´ë©´)}ê°œ)",
                range(len(ê³ ê°_ì˜µì…˜)),
                format_func=lambda i: ê³ ê°_ì˜µì…˜[i],
                key="ê³ ê°ì—…ì²´_ì„ íƒ"
            )
            
            ì„ íƒ_ê³ ê° = ì „ì²´_ê³ ê°[ì„ íƒ_idx][0]
            
            st.markdown("---")
            st.markdown(f"## ðŸ¢ {ì„ íƒ_ê³ ê°}")
            
            # ì´ ê³ ê°ì—ê²Œ íŒë§¤í•œ ê±°ëž˜ ë°ì´í„° (ê³µê¸‰ê°€ì•¡ > 0)
            ê³ ê°_df = ledger_df[(ledger_df['ê±°ëž˜ì²˜'] == ì„ íƒ_ê³ ê°) & (ledger_df['ê³µê¸‰ê°€ì•¡'] > 0) & (~ledger_df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ|ì¶œê¸ˆ', na=False))]
            
            # ===== ë¯¸ìˆ˜ê¸ˆ í˜„í™© (base_receivablesì—ì„œ ê°€ì ¸ì˜´) =====
            st.markdown("### ðŸ’° ë¯¸ìˆ˜ê¸ˆ í˜„í™©")
            
            # ë¯¸ìˆ˜ê¸ˆì€ base_receivablesì—ì„œ ì§ì ‘ ê°€ì ¸ì˜´ (ì»´ìž¥ë¶€ GULREST)
            ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict = base_recv_df.set_index('ê±°ëž˜ì²˜')['ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ'].to_dict() if len(base_recv_df) > 0 else {}
            ë¯¸ìˆ˜ê¸ˆ = ê¸°ì´ˆë¯¸ìˆ˜ê¸ˆ_dict.get(ì„ íƒ_ê³ ê°, 0)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("ì´ ê±°ëž˜ íšŸìˆ˜", f"{len(ê³ ê°_df)}ê±´")
            with col_b:
                ì´_íŒë§¤ê¸ˆì•¡ = ê³ ê°_df['ê³µê¸‰ê°€ì•¡'].sum() + ê³ ê°_df['ë¶€ê°€ì„¸'].sum()
                st.metric("ì´ íŒë§¤ê¸ˆì•¡", f"{ì´_íŒë§¤ê¸ˆì•¡:,.0f}ì›")
            with col_c:
                delta_color = "inverse" if ë¯¸ìˆ˜ê¸ˆ > 0 else "normal"
                st.metric("í˜„ìž¬ ë¯¸ìˆ˜ê¸ˆ", f"{ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›", delta="ë¯¸ìˆ˜" if ë¯¸ìˆ˜ê¸ˆ > 0 else "ì™„ë‚©", delta_color=delta_color)
            
            st.markdown("---")
            
            # ===== ì—°ë„ë³„ ë§¤ì¶œ í˜„í™© =====
            st.markdown("### ðŸ“… ì—°ë„ë³„ ë§¤ì¶œ í˜„í™©")
            
            ì „ì²´_ê±°ëž˜ì²˜_df = ledger_df[ledger_df['ê±°ëž˜ì²˜'] == ì„ íƒ_ê³ ê°].copy()
            
            if len(ì „ì²´_ê±°ëž˜ì²˜_df) > 0:
                # ì—°ë„ ì¶”ì¶œ
                ì „ì²´_ê±°ëž˜ì²˜_df['ì—°ë„'] = ì „ì²´_ê±°ëž˜ì²˜_df['ë‚ ì§œ'].dt.year
                
                # ë‹¹í•´ë…„ë„, ì „ë…„ë„
                ë‹¹í•´ì—°ë„ = get_kst_now().year
                ì „ë…„ë„ = ë‹¹í•´ì—°ë„ - 1
                
                ì—°ë„ë³„_ë°ì´í„° = []
                for ì—°ë„ in [ë‹¹í•´ì—°ë„, ì „ë…„ë„]:
                    ì—°ë„_df = ì „ì²´_ê±°ëž˜ì²˜_df[ì „ì²´_ê±°ëž˜ì²˜_df['ì—°ë„'] == ì—°ë„]
                    
                    # íŒë§¤ (ìž…ê¸ˆ/ì¶œê¸ˆ ì œì™¸, ê³µê¸‰ê°€ì•¡ > 0)
                    íŒë§¤_df = ì—°ë„_df[(ì—°ë„_df['ê³µê¸‰ê°€ì•¡'] > 0) & (~ì—°ë„_df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ|ì¶œê¸ˆ', na=False))]
                    ë§¤ì¶œì•¡ = íŒë§¤_df['ê³µê¸‰ê°€ì•¡'].sum()
                    ë¶€ê°€ì„¸ = íŒë§¤_df['ë¶€ê°€ì„¸'].sum()
                    í•©ê³„ = ë§¤ì¶œì•¡ + ë¶€ê°€ì„¸
                    
                    # ìž…ê¸ˆ
                    ìž…ê¸ˆ_df = ì—°ë„_df[ì—°ë„_df['ì°¸ì¡°'].str.contains('ìž…ê¸ˆ', na=False)]
                    ìž…ê¸ˆì•¡ = abs(ìž…ê¸ˆ_df['ê³µê¸‰ê°€ì•¡'].sum())
                    
                    ì—°ë„ë³„_ë°ì´í„°.append({
                        'ì—°ë„': f"{ì—°ë„}ë…„",
                        'ë§¤ì¶œì•¡': ë§¤ì¶œì•¡,
                        'ë¶€ê°€ì„¸': ë¶€ê°€ì„¸,
                        'í•©ê³„': í•©ê³„,
                        'ìž…ê¸ˆì•¡': ìž…ê¸ˆì•¡
                    })
                
                # í…Œì´ë¸” í˜•ì‹ìœ¼ë¡œ í‘œì‹œ
                col1, col2 = st.columns(2)
                
                for i, data in enumerate(ì—°ë„ë³„_ë°ì´í„°):
                    with col1 if i == 0 else col2:
                        st.markdown(f"#### {data['ì—°ë„']} {'(ë‹¹í•´)' if i == 0 else '(ì „ë…„)'}")
                        st.markdown(f"""
                        | í•­ëª© | ê¸ˆì•¡ |
                        |------|------|
                        | ë§¤ì¶œì•¡ | {data['ë§¤ì¶œì•¡']:,.0f}ì› |
                        | ë¶€ê°€ì„¸ | {data['ë¶€ê°€ì„¸']:,.0f}ì› |
                        | **í•©ê³„** | **{data['í•©ê³„']:,.0f}ì›** |
                        | ìž…ê¸ˆì•¡ | {data['ìž…ê¸ˆì•¡']:,.0f}ì› |
                        """)
            
            st.markdown("---")
            
            # ===== ìµœê·¼ 60ì¼ íŒë§¤ ë‚´ì—­ =====
            st.markdown("### ðŸ“¦ ìµœê·¼ 60ì¼ íŒë§¤ ë‚´ì—­")
            
            if len(ê³ ê°_df) > 0:
                # 60ì¼ ì´ë‚´ ê±°ëž˜ë§Œ
                ê¸°ì¤€ì¼_60 = get_kst_now() - timedelta(days=60)
                ìµœê·¼60ì¼_df = ê³ ê°_df[ê³ ê°_df['ë‚ ì§œ'] >= ê¸°ì¤€ì¼_60].sort_values('ë‚ ì§œ', ascending=False)
                
                if len(ìµœê·¼60ì¼_df) > 0:
                    st.success(f"ðŸ” ìµœê·¼ 60ì¼ ë‚´ {len(ìµœê·¼60ì¼_df)}ê±´ íŒë§¤")
                    
                    # í…Œì´ë¸”ë¡œ í‘œì‹œ
                    for _, row in ìµœê·¼60ì¼_df.iterrows():
                        í’ˆëª©ëª… = row['í’ˆëª©'] if pd.notna(row['í’ˆëª©']) else ''
                        ìˆ˜ëŸ‰ = abs(row['ìˆ˜ëŸ‰']) if pd.notna(row['ìˆ˜ëŸ‰']) else 0
                        ë‹¨ê°€ = row['ë‹¨ê°€'] if pd.notna(row['ë‹¨ê°€']) else 0
                        ê³µê¸‰ê°€ì•¡ = row['ê³µê¸‰ê°€ì•¡'] if pd.notna(row['ê³µê¸‰ê°€ì•¡']) else 0
                        ë‚ ì§œ = row['ë‚ ì§œ'].strftime('%m/%d')
                        
                        st.markdown(f"**{ë‚ ì§œ}** | {í’ˆëª©ëª…} | {ìˆ˜ëŸ‰:,.0f}ê°œ Ã— {ë‹¨ê°€:,.0f}ì› = **{ê³µê¸‰ê°€ì•¡:,.0f}ì›**")
                else:
                    st.info("ìµœê·¼ 60ì¼ ë‚´ íŒë§¤ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
            else:
                st.info("íŒë§¤ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
            
            st.markdown("---")
            
            # ===== êµ¬ë§¤ íŒ¨í„´ ë¶„ì„ =====
            st.markdown("### ðŸ“Š êµ¬ë§¤ íŒ¨í„´ ë¶„ì„")
            
            ì£¼ê¸°_ë¶„ì„ = êµ¬ë§¤ì£¼ê¸°_ë¶„ì„(ì„ íƒ_ê³ ê°, ledger_df)
            
            if ì£¼ê¸°_ë¶„ì„:
                for item in ì£¼ê¸°_ë¶„ì„[:5]:
                    ë‚¨ì€ì¼ = item['ë‚¨ì€ì¼ìˆ˜']
                    if ë‚¨ì€ì¼ <= 0:
                        ìƒíƒœ = "ðŸ”´ êµ¬ë§¤ì¼ ì§€ë‚¨!"
                    elif ë‚¨ì€ì¼ <= 7:
                        ìƒíƒœ = f"ðŸŸ  {ë‚¨ì€ì¼}ì¼ í›„"
                    elif ë‚¨ì€ì¼ <= 14:
                        ìƒíƒœ = f"ðŸŸ¡ {ë‚¨ì€ì¼}ì¼ í›„"
                    else:
                        ìƒíƒœ = f"ðŸŸ¢ {ë‚¨ì€ì¼}ì¼ í›„"
                    
                    st.markdown(f"**{item['í’ˆëª©']}** - ì£¼ê¸°: {item['í‰ê· ì£¼ê¸°']}ì¼ | ë§ˆì§€ë§‰: {item['ë§ˆì§€ë§‰êµ¬ë§¤'].strftime('%m/%d')} | {ìƒíƒœ}")
            else:
                st.info("êµ¬ë§¤ íŒ¨í„´ì„ ë¶„ì„í•˜ë ¤ë©´ ë™ì¼ í’ˆëª© 2íšŒ ì´ìƒ ê±°ëž˜ê°€ í•„ìš”í•©ë‹ˆë‹¤.")
        else:
            st.info("ê³ ê°ì—…ì²´ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
    
    # ===== íƒ­3: ë§¤ìž…ì—…ì²´ (ë‚´ê°€ ë¬¼ê±´ ì‚¬ì˜¤ëŠ” ê³³) =====
    with tab3:
        st.markdown("### ðŸ“¥ ë§¤ìž…ì—…ì²´")
        st.markdown("*ë‚´ê°€ ë¬¼ê±´ì„ êµ¬ìž…í•˜ëŠ” ì—…ì²´*")
        
        ë§¤ìž…_í™œì„± = ë¶„ë¥˜ëœ_ê±°ëž˜ì²˜['ë§¤ìž…_í™œì„±']
        ë§¤ìž…_íœ´ë©´ = ë¶„ë¥˜ëœ_ê±°ëž˜ì²˜['ë§¤ìž…_íœ´ë©´']
        
        # ì „ì²´ ë§¤ìž…ì—…ì²´ ëª©ë¡ (í™œì„± + íœ´ë©´)
        ì „ì²´_ë§¤ìž… = []
        for x in ë§¤ìž…_í™œì„±:
            ì „ì²´_ë§¤ìž….append((x[0], x[1], "ðŸŸ¢"))
        for x in ë§¤ìž…_íœ´ë©´:
            ì „ì²´_ë§¤ìž….append((x[0], x[1], "âšª"))
        
        if len(ì „ì²´_ë§¤ìž…) > 0:
            # ë§¤ìž…ì—…ì²´ ì„ íƒ ë“œë¡­ë‹¤ìš´
            ë§¤ìž…_ì˜µì…˜ = [f"{x[2]} {x[0]} ({x[1].strftime('%m/%d')})" for x in ì „ì²´_ë§¤ìž…]
            ì„ íƒ_idx = st.selectbox(
                f"ë§¤ìž…ì—…ì²´ ì„ íƒ (ðŸŸ¢í™œì„± {len(ë§¤ìž…_í™œì„±)}ê°œ / âšªíœ´ë©´ {len(ë§¤ìž…_íœ´ë©´)}ê°œ)",
                range(len(ë§¤ìž…_ì˜µì…˜)),
                format_func=lambda i: ë§¤ìž…_ì˜µì…˜[i],
                key="ë§¤ìž…ì—…ì²´_ì„ íƒ"
            )
            
            ì„ íƒ_ë§¤ìž…ì—…ì²´ = ì „ì²´_ë§¤ìž…[ì„ íƒ_idx][0]
            
            st.markdown("---")
            st.markdown(f"## ðŸ­ {ì„ íƒ_ë§¤ìž…ì—…ì²´}")
            
            # ì´ ì—…ì²´ì—ì„œ ë§¤ìž…í•œ ê±°ëž˜ ë°ì´í„° (ê³µê¸‰ê°€ì•¡ < 0)
            ë§¤ìž…_df = ledger_df[(ledger_df['ê±°ëž˜ì²˜'] == ì„ íƒ_ë§¤ìž…ì—…ì²´) & (ledger_df['ê³µê¸‰ê°€ì•¡'] < 0)]
            
            # ===== ë§¤ìž… í˜„í™© =====
            st.markdown("### ðŸ’° ë§¤ìž… í˜„í™©")
            
            if len(ë§¤ìž…_df) > 0:
                # ë‹¹ì›” ë§¤ìž…
                í˜„ìž¬ì›” = get_kst_now().month
                ë‹¹ì›”_df = ë§¤ìž…_df[ë§¤ìž…_df['ë‚ ì§œ'].dt.month == í˜„ìž¬ì›”]
                ë‹¹ì›”_ê¸ˆì•¡ = abs(ë‹¹ì›”_df['ê³µê¸‰ê°€ì•¡'].sum() + ë‹¹ì›”_df['ë¶€ê°€ì„¸'].sum())
                
                # ì´ ë§¤ìž… (ì ˆëŒ€ê°’)
                ì´_ê¸ˆì•¡ = abs(ë§¤ìž…_df['ê³µê¸‰ê°€ì•¡'].sum() + ë§¤ìž…_df['ë¶€ê°€ì„¸'].sum())
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("ì´ ë§¤ìž… íšŸìˆ˜", f"{len(ë§¤ìž…_df)}ê±´")
                with col_b:
                    st.metric("ë‹¹ì›” ë§¤ìž…", f"{len(ë‹¹ì›”_df)}ê±´ / {ë‹¹ì›”_ê¸ˆì•¡:,.0f}ì›")
                with col_c:
                    st.metric("ì´ ë§¤ìž…ê¸ˆì•¡", f"{ì´_ê¸ˆì•¡:,.0f}ì›")
                
                st.markdown("---")
                
                # ===== ìµœê·¼ 60ì¼ ë§¤ìž… ë‚´ì—­ =====
                st.markdown("### ðŸ“¦ ìµœê·¼ 60ì¼ ë§¤ìž… ë‚´ì—­")
                
                ê¸°ì¤€ì¼_60 = get_kst_now() - timedelta(days=60)
                ìµœê·¼60ì¼_df = ë§¤ìž…_df[ë§¤ìž…_df['ë‚ ì§œ'] >= ê¸°ì¤€ì¼_60].sort_values('ë‚ ì§œ', ascending=False)
                
                if len(ìµœê·¼60ì¼_df) > 0:
                    st.success(f"ðŸ” ìµœê·¼ 60ì¼ ë‚´ {len(ìµœê·¼60ì¼_df)}ê±´ ë§¤ìž…")
                    
                    for _, row in ìµœê·¼60ì¼_df.iterrows():
                        í’ˆëª©ëª… = row['í’ˆëª©'] if pd.notna(row['í’ˆëª©']) else ''
                        ìˆ˜ëŸ‰ = abs(row['ìˆ˜ëŸ‰']) if pd.notna(row['ìˆ˜ëŸ‰']) else 0
                        ë‹¨ê°€ = row['ë‹¨ê°€'] if pd.notna(row['ë‹¨ê°€']) else 0
                        ê³µê¸‰ê°€ì•¡ = abs(row['ê³µê¸‰ê°€ì•¡']) if pd.notna(row['ê³µê¸‰ê°€ì•¡']) else 0
                        ë‚ ì§œ = row['ë‚ ì§œ'].strftime('%m/%d')
                        
                        st.markdown(f"**{ë‚ ì§œ}** | {í’ˆëª©ëª…} | {ìˆ˜ëŸ‰:,.0f}ê°œ Ã— {ë‹¨ê°€:,.0f}ì› = **{ê³µê¸‰ê°€ì•¡:,.0f}ì›**")
                else:
                    st.info("ìµœê·¼ 60ì¼ ë‚´ ë§¤ìž… ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
                
                st.markdown("---")
                
                # ===== ì£¼ìš” ë§¤ìž… í’ˆëª© =====
                st.markdown("### ðŸ“Š ì£¼ìš” ë§¤ìž… í’ˆëª©")
                
                í’ˆëª©ë³„_ë§¤ìž… = ë§¤ìž…_df.groupby('í’ˆëª©').agg({
                    'ìˆ˜ëŸ‰': 'sum',
                    'ê³µê¸‰ê°€ì•¡': 'sum',
                    'ë‹¨ê°€': 'mean'
                }).reset_index()
                í’ˆëª©ë³„_ë§¤ìž…['ê³µê¸‰ê°€ì•¡'] = í’ˆëª©ë³„_ë§¤ìž…['ê³µê¸‰ê°€ì•¡'].abs()
                í’ˆëª©ë³„_ë§¤ìž… = í’ˆëª©ë³„_ë§¤ìž….sort_values('ê³µê¸‰ê°€ì•¡', ascending=False).head(10)
                
                for _, row in í’ˆëª©ë³„_ë§¤ìž….iterrows():
                    í’ˆëª©ëª… = str(row['í’ˆëª©'])[:40] + '...' if len(str(row['í’ˆëª©'])) > 40 else row['í’ˆëª©']
                    st.markdown(f"**{í’ˆëª©ëª…}** - {abs(row['ìˆ˜ëŸ‰']):,.0f}ê°œ / í‰ê·  {row['ë‹¨ê°€']:,.0f}ì›")
            else:
                st.info("ë§¤ìž… ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤.")
        else:
            st.info("ë§¤ìž…ì—…ì²´ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
    
    # ===== íƒ­4: ê±°ëž˜ì²˜ ì¶”ê°€ (ë¯¸ëž˜ ê¸°ëŠ¥) =====
    with tab4:
        st.markdown("### âž• ê±°ëž˜ì²˜ ì •ë³´ ê´€ë¦¬")
        
        # ê±°ëž˜ì²˜ ì •ë³´ íŒŒì¼ ê²½ë¡œ
        from pathlib import Path
        data_dir = Path("data")
        customers_file = data_dir / "customers.csv"
        
        # ê±°ëž˜ì²˜ ì •ë³´ ë¡œë“œ
        if customers_file.exists():
            customers_df = pd.read_csv(customers_file)
            # ê¸°ì¡´ ë°ì´í„°ì— ì§€ì—­ ì»¬ëŸ¼ì´ ì—†ìœ¼ë©´ ì¶”ê°€
            if 'ì§€ì—­' not in customers_df.columns:
                customers_df['ì§€ì—­'] = ''
        else:
            customers_df = pd.DataFrame(columns=[
                'ê±°ëž˜ì²˜ëª…', 'êµ¬ë¶„', 'ì§€ì—­', 'ì‚¬ì—…ìžë²ˆí˜¸', 'ëŒ€í‘œìžëª…', 'ì—…íƒœ', 'ì¢…ëª©',
                'ì£¼ì†Œ', 'ì „í™”ë²ˆí˜¸', 'íŒ©ìŠ¤ë²ˆí˜¸', 'íœ´ëŒ€í°', 'ì´ë©”ì¼',
                'ëŒ€ì‹ í™”ë¬¼_ì§€ì ', 'ê²½ë™í™”ë¬¼_ì§€ì ', 'ë‹´ë‹¹ìžëª…', 'ë‹´ë‹¹ìžì—°ë½ì²˜', 'ë©”ëª¨'
            ])
        
        # ì„œë¸Œíƒ­
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["ðŸ“ ê±°ëž˜ì²˜ ë“±ë¡/ìˆ˜ì •", "ðŸ“‹ ê±°ëž˜ì²˜ ëª©ë¡", "ðŸ“¤ ì§€ì—­ ì¼ê´„ ì—…ë¡œë“œ"])
        
        # ===== ì„œë¸Œíƒ­1: ê±°ëž˜ì²˜ ë“±ë¡/ìˆ˜ì • =====
        with sub_tab1:
            st.markdown("#### ê±°ëž˜ì²˜ ì •ë³´ ìž…ë ¥")
            
            # ê¸°ì¡´ ê±°ëž˜ì²˜ ì„ íƒ ë˜ëŠ” ì‹ ê·œ ìž…ë ¥
            try:
                ledger_data = st.session_state.get('ledger_df', None)
                if ledger_data is not None and isinstance(ledger_data, pd.DataFrame) and len(ledger_data) > 0 and 'ê±°ëž˜ì²˜' in ledger_data.columns:
                    ê¸°ì¡´_ê±°ëž˜ì²˜_list = sorted(ledger_data['ê±°ëž˜ì²˜'].dropna().unique().tolist())
                else:
                    ê¸°ì¡´_ê±°ëž˜ì²˜_list = []
            except:
                ê¸°ì¡´_ê±°ëž˜ì²˜_list = []
            
            ë“±ë¡ëœ_ê±°ëž˜ì²˜_list = customers_df['ê±°ëž˜ì²˜ëª…'].tolist() if len(customers_df) > 0 else []
            
            ìž…ë ¥_ë°©ì‹ = st.radio("ìž…ë ¥ ë°©ì‹", ["ê¸°ì¡´ ê±°ëž˜ì²˜ ì„ íƒ", "ì‹ ê·œ ê±°ëž˜ì²˜ ìž…ë ¥"], horizontal=True, label_visibility="collapsed")
            
            if ìž…ë ¥_ë°©ì‹ == "ê¸°ì¡´ ê±°ëž˜ì²˜ ì„ íƒ":
                if ê¸°ì¡´_ê±°ëž˜ì²˜_list:
                    ì„ íƒ_ê±°ëž˜ì²˜ = st.selectbox("ê±°ëž˜ì²˜ ì„ íƒ", ê¸°ì¡´_ê±°ëž˜ì²˜_list, key="customer_select")
                    # ì´ë¯¸ ë“±ë¡ëœ ê±°ëž˜ì²˜ë©´ ê¸°ì¡´ ì •ë³´ ë¶ˆëŸ¬ì˜¤ê¸°
                    if ì„ íƒ_ê±°ëž˜ì²˜ in ë“±ë¡ëœ_ê±°ëž˜ì²˜_list:
                        ê¸°ì¡´_ì •ë³´ = customers_df[customers_df['ê±°ëž˜ì²˜ëª…'] == ì„ íƒ_ê±°ëž˜ì²˜].iloc[0].to_dict()
                        st.info(f"âœ… '{ì„ íƒ_ê±°ëž˜ì²˜}'ì˜ ê¸°ì¡´ ì •ë³´ë¥¼ ë¶ˆëŸ¬ì™”ìŠµë‹ˆë‹¤. ìˆ˜ì • í›„ ì €ìž¥í•˜ì„¸ìš”.")
                    else:
                        ê¸°ì¡´_ì •ë³´ = {}
                else:
                    st.warning("ê±°ëž˜ ë‚´ì—­ì´ ì—†ìŠµë‹ˆë‹¤. ë¨¼ì € ê±°ëž˜ë¥¼ ìž…ë ¥í•˜ì„¸ìš”.")
                    ì„ íƒ_ê±°ëž˜ì²˜ = ""
                    ê¸°ì¡´_ì •ë³´ = {}
            else:
                ì„ íƒ_ê±°ëž˜ì²˜ = st.text_input("ê±°ëž˜ì²˜ëª… ìž…ë ¥", key="new_customer_name")
                ê¸°ì¡´_ì •ë³´ = {}
            
            if ì„ íƒ_ê±°ëž˜ì²˜:
                st.markdown("---")
                
                # êµ¬ë¶„
                êµ¬ë¶„_ì˜µì…˜ = ["ê³ ê°ì—…ì²´ (íŒë§¤)", "ë§¤ìž…ì—…ì²´ (êµ¬ë§¤)", "í˜¼í•© (íŒë§¤+êµ¬ë§¤)"]
                êµ¬ë¶„_ê¸°ë³¸ê°’ = êµ¬ë¶„_ì˜µì…˜.index(ê¸°ì¡´_ì •ë³´.get('êµ¬ë¶„', 'ê³ ê°ì—…ì²´ (íŒë§¤)')) if ê¸°ì¡´_ì •ë³´.get('êµ¬ë¶„') in êµ¬ë¶„_ì˜µì…˜ else 0
                êµ¬ë¶„ = st.selectbox("êµ¬ë¶„", êµ¬ë¶„_ì˜µì…˜, index=êµ¬ë¶„_ê¸°ë³¸ê°’)
                
                # ì§€ì—­ ì„ íƒ (ë°©ë¬¸ ì¼ì •ìš©)
                ì§€ì—­_ì˜µì…˜ = ["", "ì²­ì£¼ì‹œ ìƒë‹¹êµ¬", "ì²­ì£¼ì‹œ ì„œì›êµ¬", "ì²­ì£¼ì‹œ í¥ë•êµ¬", "ì²­ì£¼ì‹œ ì²­ì›êµ¬", 
                          "ì„¸ì¢…ì‹œ", "ëŒ€ì „ì‹œ", "ì²œì•ˆì‹œ", "ì•„ì‚°ì‹œ", "ìŒì„±êµ°", "ì§„ì²œêµ°", "ì¦í‰êµ°", 
                          "ê´´ì‚°êµ°", "ë³´ì€êµ°", "ì˜¥ì²œêµ°", "ì˜ë™êµ°", "ì¶©ì£¼ì‹œ", "ì œì²œì‹œ", "ë‹¨ì–‘êµ°",
                          "ê³µì£¼ì‹œ", "ë…¼ì‚°ì‹œ", "ê³„ë£¡ì‹œ", "ê¸ˆì‚°êµ°", "ë¶€ì—¬êµ°", "ì„œì²œêµ°", "ì²­ì–‘êµ°", "í™ì„±êµ°", "ì˜ˆì‚°êµ°", "íƒœì•ˆêµ°", "ë‹¹ì§„ì‹œ",
                          "ê¸°íƒ€ì§€ì—­"]
                ì§€ì—­_ê¸°ë³¸ê°’ = ì§€ì—­_ì˜µì…˜.index(ê¸°ì¡´_ì •ë³´.get('ì§€ì—­', '')) if ê¸°ì¡´_ì •ë³´.get('ì§€ì—­', '') in ì§€ì—­_ì˜µì…˜ else 0
                ì§€ì—­ = st.selectbox("ðŸ“ ì§€ì—­ (ë°©ë¬¸ ì¼ì •ìš©)", ì§€ì—­_ì˜µì…˜, index=ì§€ì—­_ê¸°ë³¸ê°’, help="ì˜ì—… ë°©ë¬¸ ì¼ì •í‘œ ìž‘ì„±ì— ì‚¬ìš©ë©ë‹ˆë‹¤")
                
                st.markdown("##### ðŸ“‹ ì‚¬ì—…ìž ì •ë³´")
                col1, col2 = st.columns(2)
                with col1:
                    ì‚¬ì—…ìžë²ˆí˜¸ = st.text_input("ì‚¬ì—…ìžë“±ë¡ë²ˆí˜¸", value=ê¸°ì¡´_ì •ë³´.get('ì‚¬ì—…ìžë²ˆí˜¸', ''), placeholder="000-00-00000")
                    ëŒ€í‘œìžëª… = st.text_input("ëŒ€í‘œìžëª…", value=ê¸°ì¡´_ì •ë³´.get('ëŒ€í‘œìžëª…', ''))
                with col2:
                    ì—…íƒœ = st.text_input("ì—…íƒœ", value=ê¸°ì¡´_ì •ë³´.get('ì—…íƒœ', ''), placeholder="ë„ì†Œë§¤")
                    ì¢…ëª© = st.text_input("ì¢…ëª©", value=ê¸°ì¡´_ì •ë³´.get('ì¢…ëª©', ''), placeholder="ê³µêµ¬, ì² ë¬¼")
                
                ì£¼ì†Œ = st.text_input("ì‚¬ì—…ìž¥ ì£¼ì†Œ", value=ê¸°ì¡´_ì •ë³´.get('ì£¼ì†Œ', ''), placeholder="ì‹œ/ë„ êµ¬/êµ° ìƒì„¸ì£¼ì†Œ")
                
                st.markdown("##### ðŸ“ž ì—°ë½ì²˜ ì •ë³´")
                col1, col2, col3 = st.columns(3)
                with col1:
                    ì „í™”ë²ˆí˜¸ = st.text_input("ì „í™”ë²ˆí˜¸", value=ê¸°ì¡´_ì •ë³´.get('ì „í™”ë²ˆí˜¸', ''), placeholder="043-000-0000")
                with col2:
                    íŒ©ìŠ¤ë²ˆí˜¸ = st.text_input("íŒ©ìŠ¤ë²ˆí˜¸", value=ê¸°ì¡´_ì •ë³´.get('íŒ©ìŠ¤ë²ˆí˜¸', ''), placeholder="043-000-0001")
                with col3:
                    íœ´ëŒ€í° = st.text_input("íœ´ëŒ€í°", value=ê¸°ì¡´_ì •ë³´.get('íœ´ëŒ€í°', ''), placeholder="010-0000-0000")
                
                ì´ë©”ì¼ = st.text_input("ì´ë©”ì¼ (í™ˆíƒìŠ¤ìš©)", value=ê¸°ì¡´_ì •ë³´.get('ì´ë©”ì¼', ''), placeholder="example@email.com")
                
                st.markdown("##### ðŸšš í™”ë¬¼/ë°°ì†¡ ì •ë³´")
                col1, col2 = st.columns(2)
                with col1:
                    ëŒ€ì‹ í™”ë¬¼_ì§€ì  = st.text_input("ëŒ€ì‹ í™”ë¬¼ ì§€ì ", value=ê¸°ì¡´_ì •ë³´.get('ëŒ€ì‹ í™”ë¬¼_ì§€ì ', ''), placeholder="ì²­ì£¼ ì§€ì ëª…")
                with col2:
                    ê²½ë™í™”ë¬¼_ì§€ì  = st.text_input("ê²½ë™í™”ë¬¼ ì§€ì ", value=ê¸°ì¡´_ì •ë³´.get('ê²½ë™í™”ë¬¼_ì§€ì ', ''), placeholder="ì²­ì£¼ ì§€ì ëª…")
                
                st.markdown("##### ðŸ‘¤ ë‹´ë‹¹ìž ì •ë³´")
                col1, col2 = st.columns(2)
                with col1:
                    ë‹´ë‹¹ìžëª… = st.text_input("ë‹´ë‹¹ìžëª…", value=ê¸°ì¡´_ì •ë³´.get('ë‹´ë‹¹ìžëª…', ''))
                with col2:
                    ë‹´ë‹¹ìžì—°ë½ì²˜ = st.text_input("ë‹´ë‹¹ìž ì—°ë½ì²˜", value=ê¸°ì¡´_ì •ë³´.get('ë‹´ë‹¹ìžì—°ë½ì²˜', ''), placeholder="010-0000-0000")
                
                ë©”ëª¨ = st.text_area("ë©”ëª¨", value=ê¸°ì¡´_ì •ë³´.get('ë©”ëª¨', ''), placeholder="íŠ¹ì´ì‚¬í•­, ë°°ì†¡ ìš”ì²­ì‚¬í•­ ë“±", height=80)
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("ðŸ’¾ ì €ìž¥", type="primary", use_container_width=True):
                        # ìƒˆ ë°ì´í„° ìƒì„±
                        new_data = {
                            'ê±°ëž˜ì²˜ëª…': ì„ íƒ_ê±°ëž˜ì²˜,
                            'êµ¬ë¶„': êµ¬ë¶„,
                            'ì§€ì—­': ì§€ì—­,
                            'ì‚¬ì—…ìžë²ˆí˜¸': ì‚¬ì—…ìžë²ˆí˜¸,
                            'ëŒ€í‘œìžëª…': ëŒ€í‘œìžëª…,
                            'ì—…íƒœ': ì—…íƒœ,
                            'ì¢…ëª©': ì¢…ëª©,
                            'ì£¼ì†Œ': ì£¼ì†Œ,
                            'ì „í™”ë²ˆí˜¸': ì „í™”ë²ˆí˜¸,
                            'íŒ©ìŠ¤ë²ˆí˜¸': íŒ©ìŠ¤ë²ˆí˜¸,
                            'íœ´ëŒ€í°': íœ´ëŒ€í°,
                            'ì´ë©”ì¼': ì´ë©”ì¼,
                            'ëŒ€ì‹ í™”ë¬¼_ì§€ì ': ëŒ€ì‹ í™”ë¬¼_ì§€ì ,
                            'ê²½ë™í™”ë¬¼_ì§€ì ': ê²½ë™í™”ë¬¼_ì§€ì ,
                            'ë‹´ë‹¹ìžëª…': ë‹´ë‹¹ìžì—°ë½ì²˜,
                            'ë‹´ë‹¹ìžì—°ë½ì²˜': ë‹´ë‹¹ìžì—°ë½ì²˜,
                            'ë©”ëª¨': ë©”ëª¨
                        }
                        
                        # ê¸°ì¡´ ê±°ëž˜ì²˜ë©´ ì—…ë°ì´íŠ¸, ì‹ ê·œë©´ ì¶”ê°€
                        if ì„ íƒ_ê±°ëž˜ì²˜ in ë“±ë¡ëœ_ê±°ëž˜ì²˜_list:
                            customers_df.loc[customers_df['ê±°ëž˜ì²˜ëª…'] == ì„ íƒ_ê±°ëž˜ì²˜] = pd.DataFrame([new_data]).values[0]
                            st.success(f"âœ… '{ì„ íƒ_ê±°ëž˜ì²˜}' ì •ë³´ê°€ ìˆ˜ì •ë˜ì—ˆìŠµë‹ˆë‹¤!")
                        else:
                            customers_df = pd.concat([customers_df, pd.DataFrame([new_data])], ignore_index=True)
                            st.success(f"âœ… '{ì„ íƒ_ê±°ëž˜ì²˜}' ì •ë³´ê°€ ë“±ë¡ë˜ì—ˆìŠµë‹ˆë‹¤!")
                        
                        # ì €ìž¥
                        customers_df.to_csv(customers_file, index=False, encoding='utf-8-sig')
                        st.rerun()
                
                with col2:
                    if ì„ íƒ_ê±°ëž˜ì²˜ in ë“±ë¡ëœ_ê±°ëž˜ì²˜_list:
                        if st.button("ðŸ—‘ï¸ ì‚­ì œ", type="secondary", use_container_width=True):
                            customers_df = customers_df[customers_df['ê±°ëž˜ì²˜ëª…'] != ì„ íƒ_ê±°ëž˜ì²˜]
                            customers_df.to_csv(customers_file, index=False, encoding='utf-8-sig')
                            st.success(f"'{ì„ íƒ_ê±°ëž˜ì²˜}' ì •ë³´ê°€ ì‚­ì œë˜ì—ˆìŠµë‹ˆë‹¤.")
                            st.rerun()
        
        # ===== ì„œë¸Œíƒ­2: ê±°ëž˜ì²˜ ëª©ë¡ =====
        with sub_tab2:
            st.markdown("#### ë“±ë¡ëœ ê±°ëž˜ì²˜ ëª©ë¡")
            
            if len(customers_df) > 0:
                # ê²€ìƒ‰
                ê²€ìƒ‰ì–´ = st.text_input("ðŸ” ê±°ëž˜ì²˜ ê²€ìƒ‰", placeholder="ê±°ëž˜ì²˜ëª…, ì‚¬ì—…ìžë²ˆí˜¸, ë‹´ë‹¹ìžëª…ìœ¼ë¡œ ê²€ìƒ‰")
                
                í‘œì‹œ_df = customers_df.copy()
                if ê²€ìƒ‰ì–´:
                    í‘œì‹œ_df = í‘œì‹œ_df[
                        í‘œì‹œ_df['ê±°ëž˜ì²˜ëª…'].str.contains(ê²€ìƒ‰ì–´, na=False) |
                        í‘œì‹œ_df['ì‚¬ì—…ìžë²ˆí˜¸'].str.contains(ê²€ìƒ‰ì–´, na=False) |
                        í‘œì‹œ_df['ë‹´ë‹¹ìžëª…'].str.contains(ê²€ìƒ‰ì–´, na=False)
                    ]
                
                st.markdown(f"**ì´ {len(í‘œì‹œ_df)}ê°œ ê±°ëž˜ì²˜**")
                
                # ì£¼ìš” ì •ë³´ë§Œ í‘œì‹œ (ì§€ì—­ ì¶”ê°€)
                í‘œì‹œ_ì»¬ëŸ¼ = ['ê±°ëž˜ì²˜ëª…', 'êµ¬ë¶„', 'ì§€ì—­', 'ì‚¬ì—…ìžë²ˆí˜¸', 'ì „í™”ë²ˆí˜¸', 'íŒ©ìŠ¤ë²ˆí˜¸', 'ëŒ€ì‹ í™”ë¬¼_ì§€ì ', 'ê²½ë™í™”ë¬¼_ì§€ì ', 'ë‹´ë‹¹ìžëª…']
                # ì§€ì—­ ì»¬ëŸ¼ì´ ì—†ëŠ” ê²½ìš° ì²˜ë¦¬
                í‘œì‹œ_ì»¬ëŸ¼ = [col for col in í‘œì‹œ_ì»¬ëŸ¼ if col in í‘œì‹œ_df.columns]
                í‘œì‹œ_df_short = í‘œì‹œ_df[í‘œì‹œ_ì»¬ëŸ¼].fillna('')
                
                st.dataframe(í‘œì‹œ_df_short, use_container_width=True, hide_index=True)
                
                # CSV ë‹¤ìš´ë¡œë“œ
                csv_data = customers_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="ðŸ“¥ ê±°ëž˜ì²˜ ëª©ë¡ ë‹¤ìš´ë¡œë“œ (CSV)",
                    data=csv_data,
                    file_name=f"ê±°ëž˜ì²˜ëª©ë¡_{get_kst_now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("ë“±ë¡ëœ ê±°ëž˜ì²˜ê°€ ì—†ìŠµë‹ˆë‹¤. 'ê±°ëž˜ì²˜ ë“±ë¡/ìˆ˜ì •' íƒ­ì—ì„œ ê±°ëž˜ì²˜ë¥¼ ë“±ë¡í•˜ì„¸ìš”.")
        
        # ===== ì„œë¸Œíƒ­3: ì§€ì—­ ì¼ê´„ ì—…ë¡œë“œ =====
        with sub_tab3:
            st.markdown("### ðŸ“¤ ì§€ì—­ ì¼ê´„ ì—…ë¡œë“œ")
            st.info("""
            **ì‚¬ìš© ë°©ë²•:**
            1. ðŸ“… ë°©ë¬¸ ì¼ì • â†’ ðŸ—ºï¸ ì§€ì—­ë³„ í˜„í™©ì—ì„œ **ì§€ì—­ ë¯¸ì§€ì • ê±°ëž˜ì²˜ ì—‘ì…€** ë‹¤ìš´ë¡œë“œ
            2. ì—‘ì…€ íŒŒì¼ì˜ **Eì—´(ì§€ì—­)**ì— ì§€ì—­ëª… ìž…ë ¥
            3. ì•„ëž˜ì— ì—‘ì…€ íŒŒì¼ ì—…ë¡œë“œ
            4. **ì ìš©í•˜ê¸°** ë²„íŠ¼ í´ë¦­
            """)
            
            st.markdown("---")
            
            ì—…ë¡œë“œ_íŒŒì¼ = st.file_uploader("ðŸ“ ì§€ì—­ ì •ë³´ ì—‘ì…€ íŒŒì¼ ì—…ë¡œë“œ", type=['xlsx', 'xls'])
            
            if ì—…ë¡œë“œ_íŒŒì¼ is not None:
                try:
                    ì—…ë¡œë“œ_df = pd.read_excel(ì—…ë¡œë“œ_íŒŒì¼)
                    
                    # í•„ìˆ˜ ì»¬ëŸ¼ í™•ì¸
                    if 'ê±°ëž˜ì²˜ëª…' in ì—…ë¡œë“œ_df.columns and 'ì§€ì—­' in ì—…ë¡œë“œ_df.columns:
                        st.success(f"âœ… {len(ì—…ë¡œë“œ_df)}ê°œ ê±°ëž˜ì²˜ ë°ì´í„° í™•ì¸!")
                        
                        # ë¯¸ë¦¬ë³´ê¸°
                        st.markdown("#### ðŸ“‹ ì—…ë¡œë“œ ë°ì´í„° ë¯¸ë¦¬ë³´ê¸°")
                        st.dataframe(ì—…ë¡œë“œ_df[['ê±°ëž˜ì²˜ëª…', 'ì§€ì—­']].head(20), use_container_width=True, hide_index=True)
                        
                        # ì§€ì—­ë³„ í†µê³„
                        ì§€ì—­_í†µê³„ = ì—…ë¡œë“œ_df['ì§€ì—­'].value_counts()
                        st.markdown(f"**ì§€ì—­ ì¢…ë¥˜:** {len(ì§€ì—­_í†µê³„)}ê°œ")
                        
                        if st.button("âœ… ì§€ì—­ ì •ë³´ ì ìš©í•˜ê¸°", type="primary", use_container_width=True):
                            # ê¸°ì¡´ ë°ì´í„°ì— ì§€ì—­ ì—…ë°ì´íŠ¸
                            ì—…ë°ì´íŠ¸_ìˆ˜ = 0
                            ì¶”ê°€_ìˆ˜ = 0
                            
                            for _, row in ì—…ë¡œë“œ_df.iterrows():
                                ê±°ëž˜ì²˜ëª… = row['ê±°ëž˜ì²˜ëª…']
                                ì§€ì—­ = row['ì§€ì—­'] if pd.notna(row['ì§€ì—­']) else ''
                                
                                if ê±°ëž˜ì²˜ëª… in customers_df['ê±°ëž˜ì²˜ëª…'].values:
                                    # ê¸°ì¡´ ê±°ëž˜ì²˜ ì—…ë°ì´íŠ¸
                                    customers_df.loc[customers_df['ê±°ëž˜ì²˜ëª…'] == ê±°ëž˜ì²˜ëª…, 'ì§€ì—­'] = ì§€ì—­
                                    ì—…ë°ì´íŠ¸_ìˆ˜ += 1
                                else:
                                    # ì‹ ê·œ ê±°ëž˜ì²˜ ì¶”ê°€
                                    new_row = pd.DataFrame([{
                                        'ê±°ëž˜ì²˜ëª…': ê±°ëž˜ì²˜ëª…,
                                        'êµ¬ë¶„': '',
                                        'ì§€ì—­': ì§€ì—­,
                                        'ì‚¬ì—…ìžë²ˆí˜¸': '',
                                        'ëŒ€í‘œìžëª…': '',
                                        'ì—…íƒœ': '',
                                        'ì¢…ëª©': '',
                                        'ì£¼ì†Œ': '',
                                        'ì „í™”ë²ˆí˜¸': '',
                                        'íŒ©ìŠ¤ë²ˆí˜¸': '',
                                        'íœ´ëŒ€í°': '',
                                        'ì´ë©”ì¼': '',
                                        'ëŒ€ì‹ í™”ë¬¼_ì§€ì ': '',
                                        'ê²½ë™í™”ë¬¼_ì§€ì ': '',
                                        'ë‹´ë‹¹ìžëª…': '',
                                        'ë‹´ë‹¹ìžì—°ë½ì²˜': '',
                                        'ë©”ëª¨': ''
                                    }])
                                    customers_df = pd.concat([customers_df, new_row], ignore_index=True)
                                    ì¶”ê°€_ìˆ˜ += 1
                            
                            # ì €ìž¥
                            customers_df.to_csv(customers_file, index=False, encoding='utf-8-sig')
                            
                            st.success(f"""
                            âœ… **ì ìš© ì™„ë£Œ!**
                            - ì—…ë°ì´íŠ¸: {ì—…ë°ì´íŠ¸_ìˆ˜}ê°œ ê±°ëž˜ì²˜
                            - ì‹ ê·œ ì¶”ê°€: {ì¶”ê°€_ìˆ˜}ê°œ ê±°ëž˜ì²˜
                            """)
                            st.balloons()
                            st.rerun()
                    else:
                        st.error("âŒ 'ê±°ëž˜ì²˜ëª…'ê³¼ 'ì§€ì—­' ì»¬ëŸ¼ì´ í•„ìš”í•©ë‹ˆë‹¤. ì˜¬ë°”ë¥¸ í˜•ì‹ì˜ íŒŒì¼ì„ ì—…ë¡œë“œí•´ì£¼ì„¸ìš”.")
                
                except Exception as e:
                    st.error(f"íŒŒì¼ ì½ê¸° ì˜¤ë¥˜: {str(e)}")
            
            st.markdown("---")
            st.markdown("#### ðŸ“ ì§€ì—­ ëª©ë¡ ì°¸ê³ ")
            st.markdown("""
            ì¶©ë¶: ì²­ì£¼ì‹œ, ì¶©ì£¼ì‹œ, ì œì²œì‹œ, ìŒì„±êµ°, ì§„ì²œêµ°, ì¦í‰êµ°, ê´´ì‚°êµ°, ë³´ì€êµ°, ì˜¥ì²œêµ°, ì˜ë™êµ°  
            ì¶©ë‚¨: ì²œì•ˆì‹œ, ì•„ì‚°ì‹œ, ë…¼ì‚°ì‹œ, ê³„ë£¡ì‹œ, ê³µì£¼ì‹œ, ê¸ˆì‚°êµ°, ë¶€ì—¬êµ°, ì„œì²œêµ°, ì²­ì–‘êµ°, í™ì„±êµ°, ì˜ˆì‚°êµ°, ë‹¹ì§„ì‹œ, ì„œì‚°ì‹œ, íƒœì•ˆêµ°, ë³´ë ¹ì‹œ  
            ì„¸ì¢…: ì„¸ì¢…ì‹œ  
            ëŒ€ì „: ëŒ€ì „ì‹œ  
            ê¸°íƒ€: ì§ì›ëª…(ë‹´ë‹¹êµ¬ì—­) ë˜ëŠ” ê¸°íƒ€ì§€ì—­
            """)

# ==================== ë°©ë¬¸ ì¼ì • ====================
elif menu == "ðŸ“… ë°©ë¬¸ ì¼ì •":
    st.title("ðŸ“… ì˜ì—… ë°©ë¬¸ ì¼ì •í‘œ")
    
    try:
        from pathlib import Path
        data_dir = Path("data")
        
        df = st.session_state.ledger_df.copy()
        
        # ê±°ëž˜ì²˜ ì •ë³´ ë¡œë“œ
        customers_file = data_dir / "customers.csv"
        if customers_file.exists():
            customers_df = pd.read_csv(customers_file)
            if 'ì§€ì—­' not in customers_df.columns:
                customers_df['ì§€ì—­'] = ''
            # ê±°ëž˜ì²˜ëª… ê³µë°± ì œê±°
            customers_df['ê±°ëž˜ì²˜ëª…'] = customers_df['ê±°ëž˜ì²˜ëª…'].astype(str).str.strip()
            st.caption(f"âœ… ê±°ëž˜ì²˜ ì •ë³´ ë¡œë“œ: {len(customers_df)}ê±´")
        else:
            customers_df = pd.DataFrame(columns=['ê±°ëž˜ì²˜ëª…', 'ì§€ì—­'])
            st.warning("âš ï¸ ê±°ëž˜ì²˜ ì •ë³´ íŒŒì¼(data/customers.csv)ì´ ì—†ìŠµë‹ˆë‹¤. GitHubì— ì—…ë¡œë“œí•´ì£¼ì„¸ìš”.")
        
        if len(df) == 0:
            st.warning("ê±°ëž˜ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤. ë¨¼ì € ê±°ëž˜ë¥¼ ìž…ë ¥í•´ì£¼ì„¸ìš”.")
        else:
            # ë‚ ì§œ ë³€í™˜
            df['ë‚ ì§œ'] = pd.to_datetime(df['ë‚ ì§œ'])
            
            # í˜„ìž¬ ì‹œê°„ (timezone-naive)
            í˜„ìž¬ì‹œê°„ = get_kst_now().replace(tzinfo=None)
            
            # ìµœê·¼ 1ë…„ ë°ì´í„°ë§Œ
            ê¸°ì¤€ì¼_1ë…„ = í˜„ìž¬ì‹œê°„ - timedelta(days=365)
            ìµœê·¼1ë…„_df = df[df['ë‚ ì§œ'] >= ê¸°ì¤€ì¼_1ë…„]
            
            # íŒë§¤ ê±°ëž˜ë§Œ (ì™¸ì¶œ)
            íŒë§¤_df = ìµœê·¼1ë…„_df[ìµœê·¼1ë…„_df['ì°¸ì¡°'].str.contains('ì™¸ì¶œ', na=False)]
            
            if len(íŒë§¤_df) == 0:
                st.info("ðŸ“Š ìµœê·¼ 1ë…„ê°„ íŒë§¤(ì™¸ì¶œ) ê±°ëž˜ ë°ì´í„°ê°€ í•„ìš”í•©ë‹ˆë‹¤.")
                st.markdown("""
                **ë°©ë¬¸ ì¼ì •í‘œ ì‚¬ìš© ë°©ë²•:**
                1. **ê±°ëž˜ ìž…ë ¥**ì—ì„œ íŒë§¤ ê±°ëž˜(ì™¸ì¶œ)ë¥¼ ìž…ë ¥í•˜ì„¸ìš”
                2. **ê±°ëž˜ì²˜ ê´€ë¦¬**ì—ì„œ ê° ê±°ëž˜ì²˜ì˜ **ì§€ì—­**ì„ ì„¤ì •í•˜ì„¸ìš”
                3. 2íšŒ ì´ìƒ ë°˜ë³µ ê±°ëž˜ê°€ ìžˆìœ¼ë©´ ìžë™ìœ¼ë¡œ ë°©ë¬¸ ì£¼ê¸°ê°€ ê³„ì‚°ë©ë‹ˆë‹¤
                """)
            else:
                # íƒ­ êµ¬ì„±
                tab1, tab2, tab3 = st.tabs(["ðŸ“… ì›”ê°„ ë°©ë¬¸ ì¼ì •", "ðŸ“Š ê±°ëž˜ì²˜ë³„ ë°©ë¬¸ ì£¼ê¸°", "ðŸ—ºï¸ ì§€ì—­ë³„ í˜„í™©"])
                
                # ===== íƒ­1: ì›”ê°„ ë°©ë¬¸ ì¼ì • =====
                with tab1:
                    st.markdown("### ðŸ“… ì›”ê°„ ë°©ë¬¸ ì¼ì •í‘œ")
                    
                    # ì›” ì„ íƒ
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        í˜„ìž¬ì—°ë„ = get_kst_now().year
                        ì„ íƒ_ì—°ë„ = st.selectbox("ì—°ë„", [í˜„ìž¬ì—°ë„, í˜„ìž¬ì—°ë„ + 1], index=0, key="visit_year")
                        ì„ íƒ_ì›” = st.selectbox("ì›”", list(range(1, 13)), index=get_kst_now().month - 1, key="visit_month")
                    
                    # ê±°ëž˜ì²˜ë³„ ë°©ë¬¸ ì£¼ê¸° ê³„ì‚°
                    def ë°©ë¬¸ì£¼ê¸°_ê³„ì‚°(ê±°ëž˜ì²˜ëª…):
                        try:
                            ê±°ëž˜ì²˜_df = íŒë§¤_df[íŒë§¤_df['ê±°ëž˜ì²˜'] == ê±°ëž˜ì²˜ëª…].sort_values('ë‚ ì§œ')
                            if len(ê±°ëž˜ì²˜_df) < 2:
                                return None
                            
                            ë‚ ì§œë“¤ = ê±°ëž˜ì²˜_df['ë‚ ì§œ'].tolist()
                            ê°„ê²©ë“¤ = []
                            for i in range(1, len(ë‚ ì§œë“¤)):
                                ê°„ê²© = (ë‚ ì§œë“¤[i] - ë‚ ì§œë“¤[i-1]).days
                                if ê°„ê²© > 0:
                                    ê°„ê²©ë“¤.append(ê°„ê²©)
                            
                            if not ê°„ê²©ë“¤:
                                return None
                            
                            í‰ê· _ì£¼ê¸° = sum(ê°„ê²©ë“¤) / len(ê°„ê²©ë“¤)
                            ë§ˆì§€ë§‰_ê±°ëž˜ì¼ = ë‚ ì§œë“¤[-1]
                            ë‹¤ìŒ_ì˜ˆìƒì¼ = ë§ˆì§€ë§‰_ê±°ëž˜ì¼ + timedelta(days=í‰ê· _ì£¼ê¸°)
                            
                            return {
                                'ê±°ëž˜ì²˜': ê±°ëž˜ì²˜ëª…,
                                'ê±°ëž˜íšŸìˆ˜': len(ê±°ëž˜ì²˜_df),
                                'í‰ê· ì£¼ê¸°': int(í‰ê· _ì£¼ê¸°),
                                'ë§ˆì§€ë§‰ê±°ëž˜': ë§ˆì§€ë§‰_ê±°ëž˜ì¼,
                                'ë‹¤ìŒì˜ˆìƒ': ë‹¤ìŒ_ì˜ˆìƒì¼
                            }
                        except:
                            return None
                    
                    # 2íšŒ ì´ìƒ ë°˜ë³µ ê±°ëž˜ì²˜ë§Œ
                    ê±°ëž˜ì²˜_ëª©ë¡ = íŒë§¤_df['ê±°ëž˜ì²˜'].value_counts()
                    ë°˜ë³µ_ê±°ëž˜ì²˜ = ê±°ëž˜ì²˜_ëª©ë¡[ê±°ëž˜ì²˜_ëª©ë¡ >= 2].index.tolist()
                    
                    if len(ë°˜ë³µ_ê±°ëž˜ì²˜) == 0:
                        st.info("2íšŒ ì´ìƒ ë°˜ë³µ ê±°ëž˜í•œ ê±°ëž˜ì²˜ê°€ ì—†ìŠµë‹ˆë‹¤. ê±°ëž˜ ë°ì´í„°ê°€ ìŒ“ì´ë©´ ìžë™ìœ¼ë¡œ í‘œì‹œë©ë‹ˆë‹¤.")
                    else:
                        ë°©ë¬¸_ì¼ì • = []
                        for ê±°ëž˜ì²˜ in ë°˜ë³µ_ê±°ëž˜ì²˜:
                            ê²°ê³¼ = ë°©ë¬¸ì£¼ê¸°_ê³„ì‚°(ê±°ëž˜ì²˜)
                            if ê²°ê³¼:
                                # ì§€ì—­ ì •ë³´ ì¶”ê°€ (ê³µë°± ì œê±° í›„ ë§¤ì¹­)
                                ê±°ëž˜ì²˜_ì •ë¦¬ = str(ê±°ëž˜ì²˜).strip()
                                ì§€ì—­_info = customers_df[customers_df['ê±°ëž˜ì²˜ëª…'] == ê±°ëž˜ì²˜_ì •ë¦¬]
                                
                                # ì •í™•ížˆ ì¼ì¹˜í•˜ì§€ ì•Šìœ¼ë©´ ë¶€ë¶„ ë§¤ì¹­ ì‹œë„
                                if len(ì§€ì—­_info) == 0:
                                    ì§€ì—­_info = customers_df[customers_df['ê±°ëž˜ì²˜ëª…'].str.contains(ê±°ëž˜ì²˜_ì •ë¦¬, na=False, regex=False)]
                                
                                if len(ì§€ì—­_info) > 0:
                                    ì§€ì—­ê°’ = ì§€ì—­_info['ì§€ì—­'].values[0]
                                    if pd.notna(ì§€ì—­ê°’) and str(ì§€ì—­ê°’).strip() != '':
                                        ê²°ê³¼['ì§€ì—­'] = str(ì§€ì—­ê°’).strip()
                                    else:
                                        ê²°ê³¼['ì§€ì—­'] = 'ë¯¸ì§€ì •'
                                else:
                                    ê²°ê³¼['ì§€ì—­'] = 'ë¯¸ì§€ì •'
                                ë°©ë¬¸_ì¼ì •.append(ê²°ê³¼)
                        
                        if ë°©ë¬¸_ì¼ì •:
                            ì¼ì •_df = pd.DataFrame(ë°©ë¬¸_ì¼ì •)
                            
                            # ì„ íƒí•œ ì›”ì— í•´ë‹¹í•˜ëŠ” ë°©ë¬¸ ì˜ˆìƒ ê±°ëž˜ì²˜
                            ì›”_ì‹œìž‘ = pd.Timestamp(f"{ì„ íƒ_ì—°ë„}-{ì„ íƒ_ì›”:02d}-01")
                            ì›”_ë = ì›”_ì‹œìž‘ + pd.offsets.MonthEnd(1)
                            
                            # í•´ë‹¹ ì›” ë°©ë¬¸ ì˜ˆìƒ
                            ì›”ê°„_ì¼ì • = ì¼ì •_df[
                                (ì¼ì •_df['ë‹¤ìŒì˜ˆìƒ'] <= ì›”_ë) | 
                                (ì¼ì •_df['ë‹¤ìŒì˜ˆìƒ'] < pd.Timestamp(í˜„ìž¬ì‹œê°„))
                            ].copy()
                            
                            if len(ì›”ê°„_ì¼ì •) > 0:
                                ì›”ê°„_ì¼ì •['ì£¼ì°¨'] = ì›”ê°„_ì¼ì •['ë‹¤ìŒì˜ˆìƒ'].apply(
                                    lambda x: min(4, max(1, (x.day - 1) // 7 + 1)) if pd.notna(x) else 1
                                )
                                ì›”ê°„_ì¼ì • = ì›”ê°„_ì¼ì •.sort_values(['ì§€ì—­', 'ì£¼ì°¨', 'ë‹¤ìŒì˜ˆìƒ'])
                                
                                st.success(f"ðŸ“… {ì„ íƒ_ì—°ë„}ë…„ {ì„ íƒ_ì›”}ì›” ë°©ë¬¸ ì˜ˆì •: **{len(ì›”ê°„_ì¼ì •)}ê°œ ê±°ëž˜ì²˜**")
                                
                                # ì§€ì—­ë³„ë¡œ ê·¸ë£¹í™”í•´ì„œ í‘œì‹œ
                                ì§€ì—­_ëª©ë¡ = ì›”ê°„_ì¼ì •['ì§€ì—­'].unique()
                                
                                for ì§€ì—­ in sorted(ì§€ì—­_ëª©ë¡):
                                    ì§€ì—­_df = ì›”ê°„_ì¼ì •[ì›”ê°„_ì¼ì •['ì§€ì—­'] == ì§€ì—­]
                                    
                                    with st.expander(f"ðŸ“ {ì§€ì—­} ({len(ì§€ì—­_df)}ê°œ ì—…ì²´)", expanded=True):
                                        for ì£¼ì°¨ in sorted(ì§€ì—­_df['ì£¼ì°¨'].unique()):
                                            ì£¼ì°¨_df = ì§€ì—­_df[ì§€ì—­_df['ì£¼ì°¨'] == ì£¼ì°¨]
                                            st.markdown(f"**{ì£¼ì°¨}ì£¼ì°¨**")
                                            
                                            for _, row in ì£¼ì°¨_df.iterrows():
                                                ì˜ˆìƒì¼ = row['ë‹¤ìŒì˜ˆìƒ'].strftime('%m/%d')
                                                ìƒíƒœ = "ðŸ”´ ì§€ë‚¨" if row['ë‹¤ìŒì˜ˆìƒ'] < pd.Timestamp(í˜„ìž¬ì‹œê°„) else "ðŸŸ¢ ì˜ˆì •"
                                                st.markdown(f"- {ìƒíƒœ} **{row['ê±°ëž˜ì²˜']}** - {ì˜ˆìƒì¼} (ì£¼ê¸°: {row['í‰ê· ì£¼ê¸°']}ì¼, ê±°ëž˜: {row['ê±°ëž˜íšŸìˆ˜']}íšŒ)")
                                            
                                            st.markdown("")
                            else:
                                st.info(f"{ì„ íƒ_ì›”}ì›”ì— ë°©ë¬¸ ì˜ˆì •ì¸ ê±°ëž˜ì²˜ê°€ ì—†ìŠµë‹ˆë‹¤.")
                            
                            # ì§€ì—­ ë¯¸ì§€ì • ê±°ëž˜ì²˜ ì•ˆë‚´
                            ë¯¸ì§€ì •_ìˆ˜ = len(ì¼ì •_df[ì¼ì •_df['ì§€ì—­'] == 'ë¯¸ì§€ì •'])
                            if ë¯¸ì§€ì •_ìˆ˜ > 0:
                                st.warning(f"âš ï¸ ì§€ì—­ ë¯¸ì§€ì • ê±°ëž˜ì²˜: {ë¯¸ì§€ì •_ìˆ˜}ê°œ\n\nðŸ‘¥ ê±°ëž˜ì²˜ ê´€ë¦¬ì—ì„œ ì§€ì—­ì„ ì„¤ì •í•´ì£¼ì„¸ìš”.")
                        else:
                            st.info("ë°©ë¬¸ ì£¼ê¸°ë¥¼ ê³„ì‚°í•  ìˆ˜ ìžˆëŠ” ê±°ëž˜ì²˜ê°€ ì—†ìŠµë‹ˆë‹¤.")
                
                # ===== íƒ­2: ê±°ëž˜ì²˜ë³„ ë°©ë¬¸ ì£¼ê¸° =====
                with tab2:
                    st.markdown("### ðŸ“Š ê±°ëž˜ì²˜ë³„ ë°©ë¬¸ ì£¼ê¸° ë¶„ì„")
                    
                    if len(ë°˜ë³µ_ê±°ëž˜ì²˜) > 0 and ë°©ë¬¸_ì¼ì •:
                        ì¼ì •_df = pd.DataFrame(ë°©ë¬¸_ì¼ì •)
                        ì¼ì •_df = ì¼ì •_df.sort_values('ë‹¤ìŒì˜ˆìƒ')
                        
                        # ìƒíƒœ í‘œì‹œ
                        ì¼ì •_df['ìƒíƒœ'] = ì¼ì •_df['ë‹¤ìŒì˜ˆìƒ'].apply(
                            lambda x: 'ðŸ”´ ë°©ë¬¸í•„ìš”' if x < pd.Timestamp(í˜„ìž¬ì‹œê°„) else 'ðŸŸ¢ ì˜ˆì •'
                        )
                        ì¼ì •_df['ë‹¤ìŒì˜ˆìƒ_í‘œì‹œ'] = ì¼ì •_df['ë‹¤ìŒì˜ˆìƒ'].dt.strftime('%Y-%m-%d')
                        ì¼ì •_df['ë§ˆì§€ë§‰ê±°ëž˜_í‘œì‹œ'] = ì¼ì •_df['ë§ˆì§€ë§‰ê±°ëž˜'].dt.strftime('%Y-%m-%d')
                        
                        # í•„í„°
                        ì§€ì—­_í•„í„° = st.multiselect(
                            "ì§€ì—­ í•„í„°", 
                            ['ì „ì²´'] + sorted(ì¼ì •_df['ì§€ì—­'].unique().tolist()),
                            default=['ì „ì²´']
                        )
                        
                        í‘œì‹œ_df = ì¼ì •_df.copy()
                        if 'ì „ì²´' not in ì§€ì—­_í•„í„°:
                            í‘œì‹œ_df = í‘œì‹œ_df[í‘œì‹œ_df['ì§€ì—­'].isin(ì§€ì—­_í•„í„°)]
                        
                        st.dataframe(
                            í‘œì‹œ_df[['ìƒíƒœ', 'ì§€ì—­', 'ê±°ëž˜ì²˜', 'ê±°ëž˜íšŸìˆ˜', 'í‰ê· ì£¼ê¸°', 'ë§ˆì§€ë§‰ê±°ëž˜_í‘œì‹œ', 'ë‹¤ìŒì˜ˆìƒ_í‘œì‹œ']].rename(columns={
                                'ë§ˆì§€ë§‰ê±°ëž˜_í‘œì‹œ': 'ë§ˆì§€ë§‰ê±°ëž˜',
                                'ë‹¤ìŒì˜ˆìƒ_í‘œì‹œ': 'ë‹¤ìŒì˜ˆìƒ'
                            }),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # í†µê³„
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("ì´ ë°˜ë³µ ê±°ëž˜ì²˜", f"{len(ì¼ì •_df)}ê°œ")
                        with col2:
                            ë°©ë¬¸í•„ìš” = len(ì¼ì •_df[ì¼ì •_df['ë‹¤ìŒì˜ˆìƒ'] < pd.Timestamp(í˜„ìž¬ì‹œê°„)])
                            st.metric("ë°©ë¬¸ í•„ìš” (ì§€ë‚¨)", f"{ë°©ë¬¸í•„ìš”}ê°œ", delta=f"-{ë°©ë¬¸í•„ìš”}" if ë°©ë¬¸í•„ìš” > 0 else None, delta_color="inverse")
                        with col3:
                            í‰ê· ì£¼ê¸°_ì „ì²´ = ì¼ì •_df['í‰ê· ì£¼ê¸°'].mean()
                            st.metric("í‰ê·  ë°©ë¬¸ ì£¼ê¸°", f"{í‰ê· ì£¼ê¸°_ì „ì²´:.0f}ì¼")
                    else:
                        st.info("2íšŒ ì´ìƒ ë°˜ë³µ ê±°ëž˜í•œ ê±°ëž˜ì²˜ ë°ì´í„°ê°€ í•„ìš”í•©ë‹ˆë‹¤.")
                
                # ===== íƒ­3: ì§€ì—­ë³„ í˜„í™© =====
                with tab3:
                    st.markdown("### ðŸ—ºï¸ ì§€ì—­ë³„ ê±°ëž˜ì²˜ í˜„í™©")
                    
                    # ========== ì§€ì—­ ê²€ìƒ‰ ê¸°ëŠ¥ ==========
                    st.markdown("#### ðŸ” ì§€ì—­ ê²€ìƒ‰")
                    ì§€ì—­_ê²€ìƒ‰ì–´ = st.text_input("ì§€ì—­ëª… ê²€ìƒ‰ (ì˜ˆ: ì²­ì£¼, ëŒ€ì „, ë…¼ì‚°)", placeholder="ì§€ì—­ëª…ì„ ìž…ë ¥í•˜ì„¸ìš”", key="region_search")
                    
                    if len(customers_df) > 0:
                        if ì§€ì—­_ê²€ìƒ‰ì–´:
                            # ì§€ì—­ ë˜ëŠ” ì£¼ì†Œì—ì„œ ê²€ìƒ‰
                            ê²€ìƒ‰_ê²°ê³¼ = customers_df[
                                (customers_df['ì§€ì—­'].str.contains(ì§€ì—­_ê²€ìƒ‰ì–´, case=False, na=False)) |
                                (customers_df['ì£¼ì†Œ'].str.contains(ì§€ì—­_ê²€ìƒ‰ì–´, case=False, na=False))
                            ]
                            
                            if len(ê²€ìƒ‰_ê²°ê³¼) > 0:
                                st.success(f"ðŸ” '{ì§€ì—­_ê²€ìƒ‰ì–´}' ê²€ìƒ‰ ê²°ê³¼: **{len(ê²€ìƒ‰_ê²°ê³¼)}ê°œ** ê±°ëž˜ì²˜")
                                
                                # ê²€ìƒ‰ ê²°ê³¼ í‘œì‹œ
                                í‘œì‹œ_ì»¬ëŸ¼ = ['ê±°ëž˜ì²˜ëª…', 'ì§€ì—­', 'ì£¼ì†Œ', 'ì „í™”ë²ˆí˜¸', 'íœ´ëŒ€í°']
                                í‘œì‹œ_ì»¬ëŸ¼ = [c for c in í‘œì‹œ_ì»¬ëŸ¼ if c in ê²€ìƒ‰_ê²°ê³¼.columns]
                                st.dataframe(ê²€ìƒ‰_ê²°ê³¼[í‘œì‹œ_ì»¬ëŸ¼], use_container_width=True, hide_index=True)
                                
                                # ê±°ëž˜ì²˜ ëª©ë¡ (í´ë¦­ ìš©ì´í•˜ê²Œ)
                                st.markdown("##### ðŸ“‹ ê±°ëž˜ì²˜ ëª©ë¡")
                                for idx, row in ê²€ìƒ‰_ê²°ê³¼.iterrows():
                                    ê±°ëž˜ì²˜ëª… = row['ê±°ëž˜ì²˜ëª…']
                                    ì§€ì—­ = row.get('ì§€ì—­', '')
                                    ì „í™” = row.get('ì „í™”ë²ˆí˜¸', '') or row.get('íœ´ëŒ€í°', '')
                                    st.markdown(f"- **{ê±°ëž˜ì²˜ëª…}** | {ì§€ì—­} | ðŸ“ž {ì „í™”}")
                            else:
                                st.warning(f"'{ì§€ì—­_ê²€ìƒ‰ì–´}'ì— í•´ë‹¹í•˜ëŠ” ê±°ëž˜ì²˜ê°€ ì—†ìŠµë‹ˆë‹¤.")
                        else:
                            # ì§€ì—­ë³„ í†µê³„ í‘œì‹œ
                            ì§€ì—­_í†µê³„ = customers_df['ì§€ì—­'].value_counts().reset_index()
                            ì§€ì—­_í†µê³„.columns = ['ì§€ì—­', 'ê±°ëž˜ì²˜ìˆ˜']
                            ì§€ì—­_í†µê³„ = ì§€ì—­_í†µê³„[ì§€ì—­_í†µê³„['ì§€ì—­'] != '']
                            
                            st.markdown("##### ðŸ“Š ì§€ì—­ë³„ ê±°ëž˜ì²˜ ìˆ˜")
                            st.dataframe(ì§€ì—­_í†µê³„.head(20), use_container_width=True, hide_index=True)
                    else:
                        st.warning("ê±°ëž˜ì²˜ ì •ë³´ê°€ ì—†ìŠµë‹ˆë‹¤. customers.csvë¥¼ GitHubì— ì—…ë¡œë“œí•´ì£¼ì„¸ìš”.")
                    
                    st.markdown("---")
                    
                    # ========== ê¸°ì¡´ ë°©ë¬¸ ì¼ì • ê¸°ë°˜ ì§€ì—­ë³„ í˜„í™© ==========
                    st.markdown("### ðŸ“Š ë°˜ë³µ ê±°ëž˜ ê¸°ì¤€ ì§€ì—­ë³„ í˜„í™©")
                    
                    if len(ë°˜ë³µ_ê±°ëž˜ì²˜) > 0 and ë°©ë¬¸_ì¼ì •:
                        ì¼ì •_df = pd.DataFrame(ë°©ë¬¸_ì¼ì •)
                        
                        ì§€ì—­ë³„_í†µê³„ = ì¼ì •_df.groupby('ì§€ì—­').agg({
                            'ê±°ëž˜ì²˜': 'count',
                            'ê±°ëž˜íšŸìˆ˜': 'sum',
                            'í‰ê· ì£¼ê¸°': 'mean'
                        }).reset_index()
                        ì§€ì—­ë³„_í†µê³„.columns = ['ì§€ì—­', 'ê±°ëž˜ì²˜ìˆ˜', 'ì´ê±°ëž˜íšŸìˆ˜', 'í‰ê· ì£¼ê¸°']
                        ì§€ì—­ë³„_í†µê³„ = ì§€ì—­ë³„_í†µê³„.sort_values('ê±°ëž˜ì²˜ìˆ˜', ascending=False)
                        ì§€ì—­ë³„_í†µê³„['í‰ê· ì£¼ê¸°'] = ì§€ì—­ë³„_í†µê³„['í‰ê· ì£¼ê¸°'].round(0).astype(int)
                        
                        st.dataframe(ì§€ì—­ë³„_í†µê³„, use_container_width=True, hide_index=True)
                        
                        # ì°¨íŠ¸
                        if len(ì§€ì—­ë³„_í†µê³„) > 1:
                            fig = px.bar(
                                ì§€ì—­ë³„_í†µê³„, 
                                x='ì§€ì—­', 
                                y='ê±°ëž˜ì²˜ìˆ˜',
                                title='ì§€ì—­ë³„ ë°˜ë³µ ê±°ëž˜ì²˜ ìˆ˜',
                                color='ê±°ëž˜ì²˜ìˆ˜',
                                color_continuous_scale='Blues'
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # ì§€ì—­ ë¯¸ì§€ì • ê±°ëž˜ì²˜ ëª©ë¡
                        ë¯¸ì§€ì •_df = ì¼ì •_df[ì¼ì •_df['ì§€ì—­'] == 'ë¯¸ì§€ì •']
                        if len(ë¯¸ì§€ì •_df) > 0:
                            st.markdown("---")
                            st.markdown("### âš ï¸ ì§€ì—­ ë¯¸ì§€ì • ê±°ëž˜ì²˜")
                            st.info("ì•„ëž˜ ê±°ëž˜ì²˜ë“¤ì˜ ì§€ì—­ì„ ì„¤ì •í•´ì£¼ì„¸ìš”. (ðŸ‘¥ ê±°ëž˜ì²˜ ê´€ë¦¬)")
                            
                            # ì—‘ì…€ ë‹¤ìš´ë¡œë“œìš© ë°ì´í„° ì¤€ë¹„
                            ë‹¤ìš´ë¡œë“œ_df = ë¯¸ì§€ì •_df[['ê±°ëž˜ì²˜', 'ê±°ëž˜íšŸìˆ˜', 'í‰ê· ì£¼ê¸°', 'ë§ˆì§€ë§‰ê±°ëž˜']].copy()
                            ë‹¤ìš´ë¡œë“œ_df['ë§ˆì§€ë§‰ê±°ëž˜'] = ë‹¤ìš´ë¡œë“œ_df['ë§ˆì§€ë§‰ê±°ëž˜'].dt.strftime('%Y-%m-%d')
                            ë‹¤ìš´ë¡œë“œ_df.columns = ['ê±°ëž˜ì²˜ëª…', 'ê±°ëž˜íšŸìˆ˜', 'í‰ê· ë°©ë¬¸ì£¼ê¸°(ì¼)', 'ë§ˆì§€ë§‰ê±°ëž˜ì¼']
                            
                            # ì—‘ì…€ ë‹¤ìš´ë¡œë“œ ë²„íŠ¼
                            from io import BytesIO
                            output = BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                ë‹¤ìš´ë¡œë“œ_df.to_excel(writer, index=False, sheet_name='ì§€ì—­ë¯¸ì§€ì •ê±°ëž˜ì²˜')
                            excel_data = output.getvalue()
                            
                            st.download_button(
                                label="ðŸ“¥ ì§€ì—­ ë¯¸ì§€ì • ê±°ëž˜ì²˜ ì—‘ì…€ ë‹¤ìš´ë¡œë“œ",
                                data=excel_data,
                                file_name=f"ì§€ì—­ë¯¸ì§€ì •ê±°ëž˜ì²˜_{get_kst_now().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            
                            st.markdown("")
                            for _, row in ë¯¸ì§€ì •_df.iterrows():
                                st.markdown(f"- **{row['ê±°ëž˜ì²˜']}** (ê±°ëž˜ {row['ê±°ëž˜íšŸìˆ˜']}íšŒ)")
                    else:
                        st.info("ì§€ì—­ë³„ í†µê³„ë¥¼ í‘œì‹œí•˜ë ¤ë©´ ë°˜ë³µ ê±°ëž˜ ë°ì´í„°ê°€ í•„ìš”í•©ë‹ˆë‹¤.")
    
    except Exception as e:
        st.error(f"ì˜¤ë¥˜ê°€ ë°œìƒí–ˆìŠµë‹ˆë‹¤: {str(e)}")
        st.info("ê±°ëž˜ ë°ì´í„°ê°€ ì¶©ë¶„ížˆ ìŒ“ì´ë©´ ì •ìƒì ìœ¼ë¡œ í‘œì‹œë©ë‹ˆë‹¤.")

# ==================== ì˜ì—… ì¼ì§€ ====================
elif menu == "ðŸ“ ì˜ì—… ì¼ì§€":
    st.title("ðŸ“ ì˜ì—… ì¼ì§€")
    
    from pathlib import Path
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # ìƒë‹´ ì¼ì§€ íŒŒì¼
    journal_file = data_dir / "sales_journal.csv"
    if journal_file.exists():
        journal_df = pd.read_csv(journal_file)
        journal_df['ë‚ ì§œ'] = pd.to_datetime(journal_df['ë‚ ì§œ'])
    else:
        journal_df = pd.DataFrame(columns=['ë‚ ì§œ', 'ê±°ëž˜ì²˜ëª…', 'ê±°ëž˜ì²˜êµ¬ë¶„', 'ìƒë‹´ë‚´ìš©', 'ë‹¤ìŒì•¡ì…˜', 'ì˜ì—…ë‹¨ê³„', 'ìž‘ì„±ì¼ì‹œ'])
    
    # ìž ìž¬ê±°ëž˜ì²˜ íŒŒì¼
    prospects_file = data_dir / "prospects.csv"
    if prospects_file.exists():
        prospects_df = pd.read_csv(prospects_file)
    else:
        prospects_df = pd.DataFrame(columns=['ì—…ì²´ëª…', 'ì§€ì—­', 'ì—…ì¢…', 'ì „í™”ë²ˆí˜¸', 'ì£¼ì†Œ', 'ë‹´ë‹¹ìž', 'ì˜ì—…ë‹¨ê³„', 'ë©”ëª¨', 'ë“±ë¡ì¼'])
    
    # ê¸°ì¡´ ê±°ëž˜ì²˜ ëª©ë¡
    try:
        ledger_data = st.session_state.get('ledger_df', None)
        if ledger_data is not None and len(ledger_data) > 0:
            ê¸°ì¡´_ê±°ëž˜ì²˜_list = sorted(ledger_data['ê±°ëž˜ì²˜'].dropna().unique().tolist())
        else:
            ê¸°ì¡´_ê±°ëž˜ì²˜_list = []
    except:
        ê¸°ì¡´_ê±°ëž˜ì²˜_list = []
    
    # ìž ìž¬ê±°ëž˜ì²˜ ëª©ë¡
    ìž ìž¬_ê±°ëž˜ì²˜_list = prospects_df['ì—…ì²´ëª…'].tolist() if len(prospects_df) > 0 else []
    
    # íƒ­ êµ¬ì„±
    tab1, tab2, tab3 = st.tabs(["ðŸ“ ìƒë‹´ ì¼ì§€", "ðŸŽ¯ ìž ìž¬ê±°ëž˜ì²˜ ê´€ë¦¬", "ðŸ“¤ ì—‘ì…€ ì—…ë¡œë“œ"])
    
    # ===== íƒ­1: ìƒë‹´ ì¼ì§€ =====
    with tab1:
        st.markdown("### ðŸ“ ì˜ì—… ìƒë‹´ ì¼ì§€")
        
        col_input, col_search = st.columns([1, 1])
        
        with col_input:
            st.markdown("#### âœï¸ ìƒë‹´ ë‚´ìš© ê¸°ë¡")
            
            # ë‚ ì§œ
            ìƒë‹´_ë‚ ì§œ = st.date_input("ðŸ“… ìƒë‹´ ë‚ ì§œ", value=get_kst_now(), key="journal_date")
            
            # ê±°ëž˜ì²˜ êµ¬ë¶„
            ê±°ëž˜ì²˜_êµ¬ë¶„ = st.radio("ê±°ëž˜ì²˜ êµ¬ë¶„", ["ê¸°ì¡´ ê±°ëž˜ì²˜", "ìž ìž¬ ê±°ëž˜ì²˜", "ì§ì ‘ ìž…ë ¥"], horizontal=True, key="customer_type")
            
            if ê±°ëž˜ì²˜_êµ¬ë¶„ == "ê¸°ì¡´ ê±°ëž˜ì²˜":
                if ê¸°ì¡´_ê±°ëž˜ì²˜_list:
                    ìƒë‹´_ê±°ëž˜ì²˜ = st.selectbox("ê±°ëž˜ì²˜ ì„ íƒ", [""] + ê¸°ì¡´_ê±°ëž˜ì²˜_list, key="journal_existing")
                else:
                    st.warning("ê¸°ì¡´ ê±°ëž˜ì²˜ê°€ ì—†ìŠµë‹ˆë‹¤.")
                    ìƒë‹´_ê±°ëž˜ì²˜ = ""
            elif ê±°ëž˜ì²˜_êµ¬ë¶„ == "ìž ìž¬ ê±°ëž˜ì²˜":
                if ìž ìž¬_ê±°ëž˜ì²˜_list:
                    ìƒë‹´_ê±°ëž˜ì²˜ = st.selectbox("ìž ìž¬ê±°ëž˜ì²˜ ì„ íƒ", [""] + ìž ìž¬_ê±°ëž˜ì²˜_list, key="journal_prospect")
                else:
                    st.info("ìž ìž¬ê±°ëž˜ì²˜ë¥¼ ë¨¼ì € ë“±ë¡í•´ì£¼ì„¸ìš”.")
                    ìƒë‹´_ê±°ëž˜ì²˜ = ""
            else:
                ìƒë‹´_ê±°ëž˜ì²˜ = st.text_input("ê±°ëž˜ì²˜ëª… ì§ì ‘ ìž…ë ¥", key="journal_new")
            
            # ìƒë‹´ ë‚´ìš©
            ìƒë‹´_ë‚´ìš© = st.text_area("ðŸ“‹ ìƒë‹´ ë‚´ìš©", height=100, placeholder="ìƒë‹´í•œ ë‚´ìš©ì„ ê¸°ë¡í•˜ì„¸ìš”...", key="journal_content")
            
            # ë‹¤ìŒ ì•¡ì…˜
            ë‹¤ìŒ_ì•¡ì…˜ = st.text_input("ðŸ“Œ ë‹¤ìŒ ì•¡ì…˜", placeholder="ì˜ˆ: ê²¬ì ì„œ ë°œì†¡, ìƒ˜í”Œ ì „ë‹¬, ìž¬ë°©ë¬¸ ì˜ˆì •", key="journal_action")
            
            # ì˜ì—… ë‹¨ê³„
            ì˜ì—…ë‹¨ê³„_ì˜µì…˜ = ["ë°œêµ´", "ì ‘ì´‰", "ìƒë‹´ì¤‘", "ê²¬ì ", "í˜‘ìƒ", "ê³„ì•½ì™„ë£Œ", "ë³´ë¥˜", "ì‹¤íŒ¨"]
            ì˜ì—…_ë‹¨ê³„ = st.selectbox("ðŸ“Š ì˜ì—… ë‹¨ê³„", ì˜ì—…ë‹¨ê³„_ì˜µì…˜, key="journal_stage")
            
            # ì €ìž¥ ë²„íŠ¼
            if st.button("ðŸ’¾ ìƒë‹´ ì¼ì§€ ì €ìž¥", type="primary", use_container_width=True):
                if ìƒë‹´_ê±°ëž˜ì²˜ and ìƒë‹´_ë‚´ìš©:
                    new_journal = pd.DataFrame([{
                        'ë‚ ì§œ': ìƒë‹´_ë‚ ì§œ,
                        'ê±°ëž˜ì²˜ëª…': ìƒë‹´_ê±°ëž˜ì²˜,
                        'ê±°ëž˜ì²˜êµ¬ë¶„': ê±°ëž˜ì²˜_êµ¬ë¶„,
                        'ìƒë‹´ë‚´ìš©': ìƒë‹´_ë‚´ìš©,
                        'ë‹¤ìŒì•¡ì…˜': ë‹¤ìŒ_ì•¡ì…˜,
                        'ì˜ì—…ë‹¨ê³„': ì˜ì—…_ë‹¨ê³„,
                        'ìž‘ì„±ì¼ì‹œ': get_kst_now().strftime('%Y-%m-%d %H:%M:%S')
                    }])
                    journal_df = pd.concat([journal_df, new_journal], ignore_index=True)
                    journal_df.to_csv(journal_file, index=False, encoding='utf-8-sig')
                    st.success(f"âœ… '{ìƒë‹´_ê±°ëž˜ì²˜}' ìƒë‹´ ì¼ì§€ê°€ ì €ìž¥ë˜ì—ˆìŠµë‹ˆë‹¤!")
                    st.rerun()
                else:
                    st.error("âŒ ê±°ëž˜ì²˜ëª…ê³¼ ìƒë‹´ ë‚´ìš©ì„ ìž…ë ¥í•´ì£¼ì„¸ìš”.")
        
        with col_search:
            st.markdown("#### ðŸ” ìƒë‹´ ì´ë ¥ ê²€ìƒ‰")
            
            ê²€ìƒ‰_ê±°ëž˜ì²˜ = st.text_input("ê±°ëž˜ì²˜ëª… ê²€ìƒ‰", placeholder="ê±°ëž˜ì²˜ëª…ì„ ìž…ë ¥í•˜ì„¸ìš”", key="journal_search")
            
            if ê²€ìƒ‰_ê±°ëž˜ì²˜ and len(journal_df) > 0:
                ê²€ìƒ‰_ê²°ê³¼ = journal_df[journal_df['ê±°ëž˜ì²˜ëª…'].str.contains(ê²€ìƒ‰_ê±°ëž˜ì²˜, case=False, na=False)]
                ê²€ìƒ‰_ê²°ê³¼ = ê²€ìƒ‰_ê²°ê³¼.sort_values('ë‚ ì§œ', ascending=False)
                
                if len(ê²€ìƒ‰_ê²°ê³¼) > 0:
                    st.success(f"ðŸ” '{ê²€ìƒ‰_ê±°ëž˜ì²˜}' ê²€ìƒ‰ ê²°ê³¼: **{len(ê²€ìƒ‰_ê²°ê³¼)}ê±´**")
                    
                    for idx, row in ê²€ìƒ‰_ê²°ê³¼.iterrows():
                        ë‚ ì§œ_str = row['ë‚ ì§œ'].strftime('%Y-%m-%d') if pd.notna(row['ë‚ ì§œ']) else ''
                        with st.expander(f"ðŸ“… {ë‚ ì§œ_str} - {row['ê±°ëž˜ì²˜ëª…']} ({row['ì˜ì—…ë‹¨ê³„']})"):
                            st.markdown(f"**ìƒë‹´ ë‚´ìš©:** {row['ìƒë‹´ë‚´ìš©']}")
                            if pd.notna(row['ë‹¤ìŒì•¡ì…˜']) and row['ë‹¤ìŒì•¡ì…˜']:
                                st.markdown(f"**ë‹¤ìŒ ì•¡ì…˜:** {row['ë‹¤ìŒì•¡ì…˜']}")
                            st.caption(f"êµ¬ë¶„: {row['ê±°ëž˜ì²˜êµ¬ë¶„']} | ìž‘ì„±: {row['ìž‘ì„±ì¼ì‹œ']}")
                else:
                    st.warning(f"'{ê²€ìƒ‰_ê±°ëž˜ì²˜}'ì— ëŒ€í•œ ìƒë‹´ ì´ë ¥ì´ ì—†ìŠµë‹ˆë‹¤.")
            elif len(journal_df) > 0:
                st.markdown("##### ðŸ“‹ ìµœê·¼ ìƒë‹´ ì¼ì§€")
                ìµœê·¼_ì¼ì§€ = journal_df.sort_values('ë‚ ì§œ', ascending=False).head(10)
                for idx, row in ìµœê·¼_ì¼ì§€.iterrows():
                    ë‚ ì§œ_str = row['ë‚ ì§œ'].strftime('%Y-%m-%d') if pd.notna(row['ë‚ ì§œ']) else ''
                    st.markdown(f"- **{ë‚ ì§œ_str}** | {row['ê±°ëž˜ì²˜ëª…']} | {row['ì˜ì—…ë‹¨ê³„']}")
            else:
                st.info("ìƒë‹´ ì¼ì§€ê°€ ì—†ìŠµë‹ˆë‹¤. ì²« ìƒë‹´ì„ ê¸°ë¡í•´ë³´ì„¸ìš”!")
        
        # ì „ì²´ ìƒë‹´ ì¼ì§€ í‘œì‹œ
        if len(journal_df) > 0:
            st.markdown("---")
            st.markdown("### ðŸ“Š ì „ì²´ ìƒë‹´ ì¼ì§€")
            
            # í•„í„°
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                ë‹¨ê³„_í•„í„° = st.multiselect("ì˜ì—… ë‹¨ê³„ í•„í„°", ì˜ì—…ë‹¨ê³„_ì˜µì…˜, default=ì˜ì—…ë‹¨ê³„_ì˜µì…˜, key="journal_filter_stage")
            with col_f2:
                êµ¬ë¶„_í•„í„° = st.multiselect("ê±°ëž˜ì²˜ êµ¬ë¶„", ["ê¸°ì¡´ ê±°ëž˜ì²˜", "ìž ìž¬ ê±°ëž˜ì²˜", "ì§ì ‘ ìž…ë ¥"], default=["ê¸°ì¡´ ê±°ëž˜ì²˜", "ìž ìž¬ ê±°ëž˜ì²˜", "ì§ì ‘ ìž…ë ¥"], key="journal_filter_type")
            
            í•„í„°_df = journal_df[
                (journal_df['ì˜ì—…ë‹¨ê³„'].isin(ë‹¨ê³„_í•„í„°)) &
                (journal_df['ê±°ëž˜ì²˜êµ¬ë¶„'].isin(êµ¬ë¶„_í•„í„°))
            ].sort_values('ë‚ ì§œ', ascending=False)
            
            st.dataframe(í•„í„°_df[['ë‚ ì§œ', 'ê±°ëž˜ì²˜ëª…', 'ìƒë‹´ë‚´ìš©', 'ë‹¤ìŒì•¡ì…˜', 'ì˜ì—…ë‹¨ê³„']], use_container_width=True, hide_index=True)
            
            st.caption(f"ì´ {len(í•„í„°_df)}ê±´")
    
    # ===== íƒ­2: ìž ìž¬ê±°ëž˜ì²˜ ê´€ë¦¬ =====
    with tab2:
        st.markdown("### ðŸŽ¯ ìž ìž¬ê±°ëž˜ì²˜ ê´€ë¦¬ (ì „êµ­)")
        
        # ì˜ì—…ë‹¨ê³„ ì»¬ëŸ¼ ì—†ìœ¼ë©´ ì¶”ê°€
        if 'ì˜ì—…ë‹¨ê³„' not in prospects_df.columns:
            prospects_df['ì˜ì—…ë‹¨ê³„'] = 'ë¯¸ë°©ë¬¸'
        if 'ë°©ë¬¸ì¼' not in prospects_df.columns:
            prospects_df['ë°©ë¬¸ì¼'] = ''
        if 'ê·œëª¨' not in prospects_df.columns:
            prospects_df['ê·œëª¨'] = ''
        
        # ìƒë‹¨ í†µê³„
        if len(prospects_df) > 0:
            col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
            ì´_ê±´ìˆ˜ = len(prospects_df)
            ë¯¸ë°©ë¬¸ = len(prospects_df[prospects_df['ì˜ì—…ë‹¨ê³„'] == 'ë¯¸ë°©ë¬¸'])
            ìœ ë§ = len(prospects_df[prospects_df['ì˜ì—…ë‹¨ê³„'] == 'ìœ ë§'])
            ìƒë‹´ì¤‘ = len(prospects_df[prospects_df['ì˜ì—…ë‹¨ê³„'].isin(['ìƒë‹´ì¤‘', 'ê²¬ì ', 'í˜‘ìƒ'])])
            íƒˆë½ = len(prospects_df[prospects_df['ì˜ì—…ë‹¨ê³„'] == 'íƒˆë½'])
            
            col_s1.metric("ðŸ“Š ì „ì²´", f"{ì´_ê±´ìˆ˜:,}ê°œ")
            col_s2.metric("ðŸ†• ë¯¸ë°©ë¬¸", f"{ë¯¸ë°©ë¬¸:,}ê°œ")
            col_s3.metric("â­ ìœ ë§", f"{ìœ ë§:,}ê°œ")
            col_s4.metric("ðŸ’¬ ìƒë‹´ì¤‘", f"{ìƒë‹´ì¤‘:,}ê°œ")
            col_s5.metric("âŒ íƒˆë½", f"{íƒˆë½:,}ê°œ")
        
        st.markdown("---")
        
        # ì„œë¸Œíƒ­
        subtab1, subtab2, subtab3 = st.tabs(["ðŸ“‹ ëª©ë¡ ì¡°íšŒ", "âž• ê°œë³„ ë“±ë¡", "ðŸ“Š í˜„í™© ë¶„ì„"])
        
        # ===== ì„œë¸Œíƒ­1: ëª©ë¡ ì¡°íšŒ (ë©”ì¸) =====
        with subtab1:
            if len(prospects_df) > 0:
                # ì§€ì—­ ê³„ì¸µ ê²€ìƒ‰
                st.markdown("#### ðŸ—ºï¸ ì§€ì—­ ê²€ìƒ‰")
                
                col_search1, col_search2 = st.columns([1, 2])
                
                with col_search1:
                    ì§€ì—­_ê²€ìƒ‰ì–´ = st.text_input("ðŸ” ì§€ì—­ ê²€ìƒ‰", placeholder="ì˜ˆ: ì²­ì£¼, ëŒ€ì „, ê°•ì›", key="region_search")
                
                with col_search2:
                    if ì§€ì—­_ê²€ìƒ‰ì–´:
                        # ê²€ìƒ‰ì–´ê°€ í¬í•¨ëœ ëª¨ë“  ì§€ì—­ ì°¾ê¸°
                        ë§¤ì¹­_ì§€ì—­ = prospects_df[prospects_df['ì§€ì—­'].astype(str).str.contains(ì§€ì—­_ê²€ìƒ‰ì–´, case=False, na=False)]['ì§€ì—­'].unique()
                        ë§¤ì¹­_ì§€ì—­ = sorted(ë§¤ì¹­_ì§€ì—­.tolist())
                        
                        if ë§¤ì¹­_ì§€ì—­:
                            # ì§€ì—­ë³„ ì—…ì²´ ìˆ˜ í‘œì‹œ
                            ì§€ì—­_ì˜µì…˜ = ['ì „ì²´ ì„ íƒ']
                            for ì§€ì—­ in ë§¤ì¹­_ì§€ì—­:
                                cnt = len(prospects_df[prospects_df['ì§€ì—­'] == ì§€ì—­])
                                ì§€ì—­_ì˜µì…˜.append(f"{ì§€ì—­} ({cnt}ê°œ)")
                            
                            ì„ íƒ_ì§€ì—­_í‘œì‹œ = st.selectbox(
                                f"ðŸ“ '{ì§€ì—­_ê²€ìƒ‰ì–´}' ê²€ìƒ‰ ê²°ê³¼: {len(ë§¤ì¹­_ì§€ì—­)}ê°œ ì§€ì—­", 
                                ì§€ì—­_ì˜µì…˜, 
                                key="region_select"
                            )
                            
                            # ì„ íƒí•œ ì§€ì—­ ì¶”ì¶œ (ì—…ì²´ìˆ˜ ì œê±°)
                            if ì„ íƒ_ì§€ì—­_í‘œì‹œ == 'ì „ì²´ ì„ íƒ':
                                ì„ íƒ_ì§€ì—­ = ì§€ì—­_ê²€ìƒ‰ì–´  # ê²€ìƒ‰ì–´ë¡œ í•„í„°
                            else:
                                ì„ íƒ_ì§€ì—­ = ì„ íƒ_ì§€ì—­_í‘œì‹œ.rsplit(' (', 1)[0]
                        else:
                            st.warning(f"'{ì§€ì—­_ê²€ìƒ‰ì–´}' ê²€ìƒ‰ ê²°ê³¼ê°€ ì—†ìŠµë‹ˆë‹¤.")
                            ì„ íƒ_ì§€ì—­ = 'ì „ì²´'
                    else:
                        # ê²€ìƒ‰ì–´ ì—†ìœ¼ë©´ ì „ì²´ ì§€ì—­ ëª©ë¡
                        ì§€ì—­_ëª©ë¡ = ['ì „ì²´'] + sorted(prospects_df['ì§€ì—­'].dropna().unique().tolist())
                        ì„ íƒ_ì§€ì—­ = st.selectbox("ðŸ“ ì§€ì—­ ì„ íƒ", ì§€ì—­_ëª©ë¡, key="region_select_all")
                
                # ì¶”ê°€ í•„í„°
                st.markdown("#### ðŸ” ì¶”ê°€ í•„í„°")
                col_f2, col_f3, col_f4 = st.columns(3)
                
                with col_f2:
                    ì—…ì¢…_ëª©ë¡ = ['ì „ì²´'] + sorted(prospects_df['ì—…ì¢…'].dropna().unique().tolist())
                    ì„ íƒ_ì—…ì¢… = st.selectbox("ì—…ì¢…", ì—…ì¢…_ëª©ë¡, key="filter_type")
                
                with col_f3:
                    ë‹¨ê³„_ëª©ë¡ = ['ì „ì²´', 'ë¯¸ë°©ë¬¸', 'ìœ ë§', 'ìƒë‹´ì¤‘', 'ê²¬ì ', 'í˜‘ìƒ', 'ë³´ë¥˜', 'íƒˆë½']
                    ì„ íƒ_ë‹¨ê³„ = st.selectbox("ì˜ì—…ë‹¨ê³„", ë‹¨ê³„_ëª©ë¡, key="filter_stage")
                
                with col_f4:
                    ê²€ìƒ‰ì–´ = st.text_input("ì—…ì²´ëª… ê²€ìƒ‰", placeholder="ê²€ìƒ‰ì–´", key="filter_search")
                
                # í•„í„° ì ìš©
                í•„í„°_df = prospects_df.copy()
                
                # ì§€ì—­ í•„í„°
                if ì§€ì—­_ê²€ìƒ‰ì–´:
                    if ì„ íƒ_ì§€ì—­ == ì§€ì—­_ê²€ìƒ‰ì–´:  # ì „ì²´ ì„ íƒ
                        í•„í„°_df = í•„í„°_df[í•„í„°_df['ì§€ì—­'].astype(str).str.contains(ì§€ì—­_ê²€ìƒ‰ì–´, case=False, na=False)]
                    else:
                        í•„í„°_df = í•„í„°_df[í•„í„°_df['ì§€ì—­'] == ì„ íƒ_ì§€ì—­]
                elif ì„ íƒ_ì§€ì—­ != 'ì „ì²´':
                    í•„í„°_df = í•„í„°_df[í•„í„°_df['ì§€ì—­'] == ì„ íƒ_ì§€ì—­]
                
                if ì„ íƒ_ì—…ì¢… != 'ì „ì²´':
                    í•„í„°_df = í•„í„°_df[í•„í„°_df['ì—…ì¢…'] == ì„ íƒ_ì—…ì¢…]
                if ì„ íƒ_ë‹¨ê³„ != 'ì „ì²´':
                    í•„í„°_df = í•„í„°_df[í•„í„°_df['ì˜ì—…ë‹¨ê³„'] == ì„ íƒ_ë‹¨ê³„]
                if ê²€ìƒ‰ì–´:
                    í•„í„°_df = í•„í„°_df[
                        (í•„í„°_df['ì—…ì²´ëª…'].astype(str).str.contains(ê²€ìƒ‰ì–´, case=False, na=False)) |
                        (í•„í„°_df['ì£¼ì†Œ'].astype(str).str.contains(ê²€ìƒ‰ì–´, case=False, na=False))
                    ]
                
                # íƒˆë½ ì œì™¸ ì˜µì…˜
                íƒˆë½_ì œì™¸ = st.checkbox("âŒ íƒˆë½ ì—…ì²´ ìˆ¨ê¸°ê¸°", value=True, key="hide_failed")
                if íƒˆë½_ì œì™¸:
                    í•„í„°_df = í•„í„°_df[í•„í„°_df['ì˜ì—…ë‹¨ê³„'] != 'íƒˆë½']
                
                st.success(f"ðŸ” ê²€ìƒ‰ ê²°ê³¼: **{len(í•„í„°_df):,}ê°œ** ì—…ì²´")
                
                # ëª©ë¡ í‘œì‹œ (íŽ˜ì´ì§€ë„¤ì´ì…˜)
                íŽ˜ì´ì§€_í¬ê¸° = 20
                ì´_íŽ˜ì´ì§€ = max(1, (len(í•„í„°_df) - 1) // íŽ˜ì´ì§€_í¬ê¸° + 1)
                
                col_pg1, col_pg2 = st.columns([1, 3])
                with col_pg1:
                    í˜„ìž¬_íŽ˜ì´ì§€ = st.number_input("íŽ˜ì´ì§€", min_value=1, max_value=ì´_íŽ˜ì´ì§€, value=1, key="page_num")
                with col_pg2:
                    st.caption(f"ì´ {ì´_íŽ˜ì´ì§€} íŽ˜ì´ì§€")
                
                ì‹œìž‘_idx = (í˜„ìž¬_íŽ˜ì´ì§€ - 1) * íŽ˜ì´ì§€_í¬ê¸°
                ë_idx = min(ì‹œìž‘_idx + íŽ˜ì´ì§€_í¬ê¸°, len(í•„í„°_df))
                íŽ˜ì´ì§€_df = í•„í„°_df.iloc[ì‹œìž‘_idx:ë_idx]
                
                # ë°ì´í„° í…Œì´ë¸” í‘œì‹œ
                st.markdown("---")
                
                for idx, row in íŽ˜ì´ì§€_df.iterrows():
                    ì‹¤ì œ_idx = row.name  # ì›ë³¸ ì¸ë±ìŠ¤
                    ë‹¨ê³„_ìƒ‰ìƒ = {
                        'ë¯¸ë°©ë¬¸': 'ðŸ”µ', 'ìœ ë§': 'â­', 'ìƒë‹´ì¤‘': 'ðŸ’¬', 
                        'ê²¬ì ': 'ðŸ“‹', 'í˜‘ìƒ': 'ðŸ¤', 'ë³´ë¥˜': 'â¸ï¸', 'íƒˆë½': 'âŒ'
                    }
                    ì˜ì—…ë‹¨ê³„ = row.get('ì˜ì—…ë‹¨ê³„', 'ë¯¸ë°©ë¬¸')
                    ë‹¨ê³„_ì•„ì´ì½˜ = ë‹¨ê³„_ìƒ‰ìƒ.get(ì˜ì—…ë‹¨ê³„, 'ðŸ”µ')
                    
                    # ì„¸ë¶€ ì£¼ì†Œ ì¶”ì¶œ (ì‹œêµ°êµ¬ ì´í›„ ë¶€ë¶„)
                    ì£¼ì†Œ_ì „ì²´ = str(row.get('ì£¼ì†Œ', ''))
                    ì£¼ì†Œ_parts = ì£¼ì†Œ_ì „ì²´.split()
                    if len(ì£¼ì†Œ_parts) > 3:
                        # ì‹œë„, ì‹œêµ°êµ¬ ì œì™¸í•˜ê³  ë‚˜ë¨¸ì§€ (ë„ë¡œëª… + ë²ˆì§€)
                        ì„¸ë¶€ì£¼ì†Œ = ' '.join(ì£¼ì†Œ_parts[-3:]) if len(ì£¼ì†Œ_parts) > 3 else ì£¼ì†Œ_ì „ì²´
                    else:
                        ì„¸ë¶€ì£¼ì†Œ = ì£¼ì†Œ_ì „ì²´
                    
                    # í‘œì‹œ: ì—…ì²´ëª… | ì˜ì—…ë‹¨ê³„ | ì„¸ë¶€ì£¼ì†Œ
                    with st.expander(f"{ë‹¨ê³„_ì•„ì´ì½˜} **{row['ì—…ì²´ëª…']}** | {ì˜ì—…ë‹¨ê³„} | {ì„¸ë¶€ì£¼ì†Œ}"):
                        col_info, col_action = st.columns([2, 1])
                        
                        with col_info:
                            st.markdown(f"**ðŸ“ ì „ì²´ì£¼ì†Œ:** {ì£¼ì†Œ_ì „ì²´}")
                            st.markdown(f"**ðŸ­ ì—…ì¢…:** {row.get('ì—…ì¢…', '')}")
                            st.markdown(f"**ðŸ“ž ì „í™”:** {row.get('ì „í™”ë²ˆí˜¸', '')}")
                            st.markdown(f"**ðŸ“ ë©”ëª¨:** {row.get('ë©”ëª¨', '')}")
                            if pd.notna(row.get('ë°©ë¬¸ì¼', '')) and row.get('ë°©ë¬¸ì¼', '') != '':
                                st.markdown(f"**ðŸ“… ìµœê·¼ë°©ë¬¸:** {row['ë°©ë¬¸ì¼']}")
                            if pd.notna(row.get('ê·œëª¨', '')) and row.get('ê·œëª¨', '') != '':
                                st.markdown(f"**ðŸ“ ê·œëª¨:** {row['ê·œëª¨']}")
                        
                        with col_action:
                            st.markdown("**ìƒíƒœ ë³€ê²½:**")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("â­ ìœ ë§", key=f"fav_{ì‹¤ì œ_idx}", use_container_width=True):
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ì˜ì—…ë‹¨ê³„'] = 'ìœ ë§'
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ë°©ë¬¸ì¼'] = get_kst_now().strftime('%Y-%m-%d')
                                    prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                                    st.rerun()
                            
                            with col_btn2:
                                if st.button("ðŸ’¬ ìƒë‹´ì¤‘", key=f"talk_{ì‹¤ì œ_idx}", use_container_width=True):
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ì˜ì—…ë‹¨ê³„'] = 'ìƒë‹´ì¤‘'
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ë°©ë¬¸ì¼'] = get_kst_now().strftime('%Y-%m-%d')
                                    prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                                    st.rerun()
                            
                            col_btn3, col_btn4 = st.columns(2)
                            with col_btn3:
                                if st.button("â¸ï¸ ë³´ë¥˜", key=f"hold_{ì‹¤ì œ_idx}", use_container_width=True):
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ì˜ì—…ë‹¨ê³„'] = 'ë³´ë¥˜'
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ë°©ë¬¸ì¼'] = get_kst_now().strftime('%Y-%m-%d')
                                    prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                                    st.rerun()
                            
                            with col_btn4:
                                if st.button("âŒ íƒˆë½", key=f"fail_{ì‹¤ì œ_idx}", use_container_width=True):
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ì˜ì—…ë‹¨ê³„'] = 'íƒˆë½'
                                    prospects_df.loc[ì‹¤ì œ_idx, 'ë°©ë¬¸ì¼'] = get_kst_now().strftime('%Y-%m-%d')
                                    prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                                    st.rerun()
                            
                            # ê·œëª¨ ìž…ë ¥
                            ê·œëª¨_ì˜µì…˜ = ['', 'ëŒ€í˜•', 'ì¤‘í˜•', 'ì†Œí˜•']
                            í˜„ìž¬_ê·œëª¨ = row.get('ê·œëª¨', '') if pd.notna(row.get('ê·œëª¨', '')) else ''
                            ê·œëª¨_idx = ê·œëª¨_ì˜µì…˜.index(í˜„ìž¬_ê·œëª¨) if í˜„ìž¬_ê·œëª¨ in ê·œëª¨_ì˜µì…˜ else 0
                            ìƒˆ_ê·œëª¨ = st.selectbox("ê·œëª¨", ê·œëª¨_ì˜µì…˜, index=ê·œëª¨_idx, key=f"size_{ì‹¤ì œ_idx}")
                            if ìƒˆ_ê·œëª¨ != í˜„ìž¬_ê·œëª¨:
                                prospects_df.loc[ì‹¤ì œ_idx, 'ê·œëª¨'] = ìƒˆ_ê·œëª¨
                                prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                            
                            st.markdown("---")
                            
                            # ì™„ì „ ì‚­ì œ
                            if st.button("ðŸ—‘ï¸ ì™„ì „ì‚­ì œ", key=f"del_{ì‹¤ì œ_idx}", type="secondary"):
                                prospects_df = prospects_df.drop(ì‹¤ì œ_idx).reset_index(drop=True)
                                prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                                st.success(f"'{row['ì—…ì²´ëª…']}' ì‚­ì œë¨")
                                st.rerun()
                
                # ì¼ê´„ ì²˜ë¦¬
                st.markdown("---")
                st.markdown("#### ðŸ”„ ì¼ê´„ ì²˜ë¦¬")
                col_bulk1, col_bulk2 = st.columns(2)
                
                with col_bulk1:
                    if st.button("ðŸ—‘ï¸ íƒˆë½ ì—…ì²´ ì „ì²´ ì‚­ì œ", type="secondary"):
                        íƒˆë½_ìˆ˜ = len(prospects_df[prospects_df['ì˜ì—…ë‹¨ê³„'] == 'íƒˆë½'])
                        if íƒˆë½_ìˆ˜ > 0:
                            prospects_df = prospects_df[prospects_df['ì˜ì—…ë‹¨ê³„'] != 'íƒˆë½'].reset_index(drop=True)
                            prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                            st.success(f"âœ… íƒˆë½ ì—…ì²´ {íƒˆë½_ìˆ˜}ê°œ ì‚­ì œë¨")
                            st.rerun()
                        else:
                            st.info("íƒˆë½ ì—…ì²´ê°€ ì—†ìŠµë‹ˆë‹¤.")
                
            else:
                st.info("ë“±ë¡ëœ ìž ìž¬ê±°ëž˜ì²˜ê°€ ì—†ìŠµë‹ˆë‹¤. 'ðŸ“¤ ì—‘ì…€ ì—…ë¡œë“œ' íƒ­ì—ì„œ ë°ì´í„°ë¥¼ ì—…ë¡œë“œí•˜ì„¸ìš”.")
        
        # ===== ì„œë¸Œíƒ­2: ê°œë³„ ë“±ë¡ =====
        with subtab2:
            st.markdown("#### âž• ìž ìž¬ê±°ëž˜ì²˜ ê°œë³„ ë“±ë¡")
            
            col_reg1, col_reg2 = st.columns(2)
            
            with col_reg1:
                ì‹ ê·œ_ì—…ì²´ëª… = st.text_input("ðŸ¢ ì—…ì²´ëª…", placeholder="ì˜ˆ: ëŒ€ì „ì¢…í•©ì² ë¬¼", key="prospect_name")
                ì‹ ê·œ_ì§€ì—­ = st.text_input("ðŸ“ ì§€ì—­", placeholder="ì˜ˆ: ëŒ€ì „ê´‘ì—­ì‹œ", key="prospect_region")
                ì—…ì¢…_ì˜µì…˜ = ["ì² ë¬¼ì ", "ê±´ìžìž¬ì ", "ë†ìžìž¬ì "]
                ì‹ ê·œ_ì—…ì¢… = st.selectbox("ðŸ­ ì—…ì¢…", ì—…ì¢…_ì˜µì…˜, key="prospect_type")
            
            with col_reg2:
                ì‹ ê·œ_ì „í™” = st.text_input("ðŸ“ž ì „í™”ë²ˆí˜¸", placeholder="000-000-0000", key="prospect_phone")
                ì‹ ê·œ_ì£¼ì†Œ = st.text_input("ðŸ  ì£¼ì†Œ", placeholder="ìƒì„¸ ì£¼ì†Œ", key="prospect_address")
                ì‹ ê·œ_ë©”ëª¨ = st.text_input("ðŸ“ ë©”ëª¨", placeholder="íŠ¹ì´ì‚¬í•­", key="prospect_memo")
            
            if st.button("ðŸ’¾ ìž ìž¬ê±°ëž˜ì²˜ ë“±ë¡", type="primary"):
                if ì‹ ê·œ_ì—…ì²´ëª…:
                    # ê¸°ì¡´ ê±°ëž˜ì²˜ ì¤‘ë³µ ì²´í¬
                    if ì‹ ê·œ_ì—…ì²´ëª… in ê¸°ì¡´_ê±°ëž˜ì²˜_list:
                        st.warning(f"âš ï¸ '{ì‹ ê·œ_ì—…ì²´ëª…}'ì€(ëŠ”) ì´ë¯¸ ê¸°ì¡´ ê±°ëž˜ì²˜ì— ìžˆìŠµë‹ˆë‹¤!")
                    elif ì‹ ê·œ_ì—…ì²´ëª… in ìž ìž¬_ê±°ëž˜ì²˜_list:
                        st.warning(f"âš ï¸ '{ì‹ ê·œ_ì—…ì²´ëª…}'ì€(ëŠ”) ì´ë¯¸ ìž ìž¬ê±°ëž˜ì²˜ì— ìžˆìŠµë‹ˆë‹¤!")
                    else:
                        new_prospect = pd.DataFrame([{
                            'ì—…ì²´ëª…': ì‹ ê·œ_ì—…ì²´ëª…,
                            'ì§€ì—­': ì‹ ê·œ_ì§€ì—­,
                            'ì—…ì¢…': ì‹ ê·œ_ì—…ì¢…,
                            'ì „í™”ë²ˆí˜¸': ì‹ ê·œ_ì „í™”,
                            'ì£¼ì†Œ': ì‹ ê·œ_ì£¼ì†Œ,
                            'ë‹´ë‹¹ìž': '',
                            'ì˜ì—…ë‹¨ê³„': 'ë¯¸ë°©ë¬¸',
                            'ë©”ëª¨': ì‹ ê·œ_ë©”ëª¨,
                            'ë“±ë¡ì¼': get_kst_now().strftime('%Y-%m-%d'),
                            'ë°©ë¬¸ì¼': '',
                            'ê·œëª¨': ''
                        }])
                        prospects_df = pd.concat([prospects_df, new_prospect], ignore_index=True)
                        prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                        st.success(f"âœ… '{ì‹ ê·œ_ì—…ì²´ëª…}' ë“±ë¡ ì™„ë£Œ!")
                        st.rerun()
                else:
                    st.error("âŒ ì—…ì²´ëª…ì„ ìž…ë ¥í•´ì£¼ì„¸ìš”.")
        
        # ===== ì„œë¸Œíƒ­3: í˜„í™© ë¶„ì„ =====
        with subtab3:
            if len(prospects_df) > 0:
                st.markdown("#### ðŸ“Š ìž ìž¬ê±°ëž˜ì²˜ í˜„í™© ë¶„ì„")
                
                col_a1, col_a2 = st.columns(2)
                
                with col_a1:
                    st.markdown("##### ðŸ—ºï¸ ì§€ì—­ë³„ í˜„í™©")
                    ì§€ì—­_í†µê³„ = prospects_df.groupby('ì§€ì—­').agg({
                        'ì—…ì²´ëª…': 'count'
                    }).reset_index()
                    ì§€ì—­_í†µê³„.columns = ['ì§€ì—­', 'ì—…ì²´ìˆ˜']
                    ì§€ì—­_í†µê³„ = ì§€ì—­_í†µê³„.sort_values('ì—…ì²´ìˆ˜', ascending=False).head(15)
                    st.dataframe(ì§€ì—­_í†µê³„, use_container_width=True, hide_index=True)
                
                with col_a2:
                    st.markdown("##### ðŸ“ˆ ì˜ì—…ë‹¨ê³„ë³„ í˜„í™©")
                    ë‹¨ê³„_í†µê³„ = prospects_df['ì˜ì—…ë‹¨ê³„'].value_counts().reset_index()
                    ë‹¨ê³„_í†µê³„.columns = ['ì˜ì—…ë‹¨ê³„', 'ì—…ì²´ìˆ˜']
                    st.dataframe(ë‹¨ê³„_í†µê³„, use_container_width=True, hide_index=True)
                
                # ì—…ì¢…ë³„ í˜„í™©
                st.markdown("##### ðŸ­ ì—…ì¢…ë³„ í˜„í™©")
                ì—…ì¢…_í†µê³„ = prospects_df['ì—…ì¢…'].value_counts().reset_index()
                ì—…ì¢…_í†µê³„.columns = ['ì—…ì¢…', 'ì—…ì²´ìˆ˜']
                
                import plotly.express as px
                fig = px.bar(ì—…ì¢…_í†µê³„, x='ì—…ì¢…', y='ì—…ì²´ìˆ˜', title='ì—…ì¢…ë³„ ìž ìž¬ê±°ëž˜ì²˜ ìˆ˜')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # ê·œëª¨ë³„ í˜„í™© (ë°ì´í„° ìžˆìœ¼ë©´)
                if 'ê·œëª¨' in prospects_df.columns:
                    ê·œëª¨_df = prospects_df[prospects_df['ê·œëª¨'].notna() & (prospects_df['ê·œëª¨'] != '')]
                    if len(ê·œëª¨_df) > 0:
                        st.markdown("##### ðŸ“ ê·œëª¨ë³„ í˜„í™©")
                        ê·œëª¨_í†µê³„ = ê·œëª¨_df['ê·œëª¨'].value_counts().reset_index()
                        ê·œëª¨_í†µê³„.columns = ['ê·œëª¨', 'ì—…ì²´ìˆ˜']
                        st.dataframe(ê·œëª¨_í†µê³„, use_container_width=True, hide_index=True)
            else:
                st.info("ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
    
    # ===== íƒ­3: ì—‘ì…€ ì—…ë¡œë“œ =====
    with tab3:
        st.markdown("### ðŸ“¤ ì „êµ­ ìž ìž¬ê±°ëž˜ì²˜ ì¼ê´„ ì—…ë¡œë“œ")
        st.info("""
        **ì „êµ­ 6,618ê°œ ìž ìž¬ê±°ëž˜ì²˜ ì—…ë¡œë“œ ê°€ëŠ¥!**
        
        ì†Œìƒê³µì¸ì‹œìž¥ì§„í¥ê³µë‹¨ ë°ì´í„° ë˜ëŠ” ì§ì ‘ ì •ë¦¬í•œ ì—‘ì…€ì„ ì—…ë¡œë“œí•˜ì„¸ìš”.
        
        **í•„ìˆ˜ ì»¬ëŸ¼:** ì—…ì²´ëª…, ì§€ì—­, ì—…ì¢…
        **ì„ íƒ ì»¬ëŸ¼:** ì „í™”ë²ˆí˜¸, ì£¼ì†Œ, ë‹´ë‹¹ìž, ë©”ëª¨
        """)
        
        # ì–‘ì‹ ë‹¤ìš´ë¡œë“œ
        st.markdown("#### ðŸ“¥ ì–‘ì‹ ë‹¤ìš´ë¡œë“œ")
        ì–‘ì‹_df = pd.DataFrame(columns=['ì—…ì²´ëª…', 'ì§€ì—­', 'ì—…ì¢…', 'ì „í™”ë²ˆí˜¸', 'ì£¼ì†Œ', 'ë‹´ë‹¹ìž', 'ë©”ëª¨'])
        ì–‘ì‹_df.loc[0] = ['ì˜ˆì‹œì² ë¬¼', 'ëŒ€ì „ê´‘ì—­ì‹œ', 'ì² ë¬¼ì ', '042-000-0000', 'ëŒ€ì „ì‹œ ì„œêµ¬ ì˜ˆì‹œë¡œ 123', 'í™ê¸¸ë™', 'ëŒ€í˜• ë§¤ìž¥']
        
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            ì–‘ì‹_df.to_excel(writer, index=False, sheet_name='ìž ìž¬ê±°ëž˜ì²˜')
        excel_data = output.getvalue()
        
        st.download_button(
            label="ðŸ“¥ ì—‘ì…€ ì–‘ì‹ ë‹¤ìš´ë¡œë“œ",
            data=excel_data,
            file_name="ìž ìž¬ê±°ëž˜ì²˜_ì–‘ì‹.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        
        # íŒŒì¼ ì—…ë¡œë“œ
        st.markdown("#### ðŸ“¤ íŒŒì¼ ì—…ë¡œë“œ")
        uploaded_file = st.file_uploader("ì—‘ì…€ íŒŒì¼ ì„ íƒ (.xlsx, .xls, .csv)", type=['xlsx', 'xls', 'csv'], key="prospect_upload")
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    upload_df = pd.read_csv(uploaded_file)
                else:
                    upload_df = pd.read_excel(uploaded_file)
                
                st.success(f"ðŸ“Š **{len(upload_df):,}ê°œ** ì—…ì²´ ë°ì´í„° í™•ì¸")
                
                # ë¯¸ë¦¬ë³´ê¸°
                st.markdown("##### ë¯¸ë¦¬ë³´ê¸° (ì²˜ìŒ 10ê°œ)")
                st.dataframe(upload_df.head(10), use_container_width=True, hide_index=True)
                
                # ì—…ì¢… ë¶„í¬
                if 'ì—…ì¢…' in upload_df.columns:
                    st.markdown("##### ì—…ì¢…ë³„ ë¶„í¬")
                    ì—…ì¢…_ë¶„í¬ = upload_df['ì—…ì¢…'].value_counts()
                    st.write(ì—…ì¢…_ë¶„í¬.to_string())
                
                # ê¸°ì¡´ ê±°ëž˜ì²˜ì™€ ì¤‘ë³µ ì²´í¬ ì˜µì…˜
                ê¸°ì¡´_ê±°ëž˜ì²˜_ì œì™¸ = st.checkbox("âœ… ê¸°ì¡´ ê±°ëž˜ì²˜ì™€ ì¤‘ë³µëœ ì—…ì²´ ì œì™¸", value=True)
                ìž ìž¬_ì¤‘ë³µ_ì œì™¸ = st.checkbox("âœ… ì´ë¯¸ ë“±ë¡ëœ ìž ìž¬ê±°ëž˜ì²˜ ì œì™¸", value=True)
                
                if st.button("ðŸ’¾ ì¼ê´„ ë“±ë¡", type="primary", use_container_width=True):
                    # í•„ìˆ˜ ì»¬ëŸ¼ í™•ì¸
                    if 'ì—…ì²´ëª…' not in upload_df.columns:
                        st.error("'ì—…ì²´ëª…' ì»¬ëŸ¼ì´ í•„ìš”í•©ë‹ˆë‹¤.")
                    else:
                        # í•„ìš”í•œ ì»¬ëŸ¼ ì¶”ê°€
                        for col in ['ì§€ì—­', 'ì—…ì¢…', 'ì „í™”ë²ˆí˜¸', 'ì£¼ì†Œ', 'ë‹´ë‹¹ìž', 'ë©”ëª¨']:
                            if col not in upload_df.columns:
                                upload_df[col] = ''
                        
                        upload_df['ì˜ì—…ë‹¨ê³„'] = 'ë¯¸ë°©ë¬¸'
                        upload_df['ë“±ë¡ì¼'] = get_kst_now().strftime('%Y-%m-%d')
                        upload_df['ë°©ë¬¸ì¼'] = ''
                        upload_df['ê·œëª¨'] = ''
                        
                        ì›ë³¸_ìˆ˜ = len(upload_df)
                        ì œì™¸_ê¸°ì¡´ = 0
                        ì œì™¸_ìž ìž¬ = 0
                        
                        # ê¸°ì¡´ ê±°ëž˜ì²˜ ì¤‘ë³µ ì œì™¸
                        if ê¸°ì¡´_ê±°ëž˜ì²˜_ì œì™¸ and ê¸°ì¡´_ê±°ëž˜ì²˜_list:
                            before = len(upload_df)
                            upload_df = upload_df[~upload_df['ì—…ì²´ëª…'].isin(ê¸°ì¡´_ê±°ëž˜ì²˜_list)]
                            ì œì™¸_ê¸°ì¡´ = before - len(upload_df)
                        
                        # ìž ìž¬ê±°ëž˜ì²˜ ì¤‘ë³µ ì œì™¸
                        if ìž ìž¬_ì¤‘ë³µ_ì œì™¸ and len(prospects_df) > 0:
                            ê¸°ì¡´_ìž ìž¬ = set(prospects_df['ì—…ì²´ëª…'].tolist())
                            before = len(upload_df)
                            upload_df = upload_df[~upload_df['ì—…ì²´ëª…'].isin(ê¸°ì¡´_ìž ìž¬)]
                            ì œì™¸_ìž ìž¬ = before - len(upload_df)
                        
                        if len(upload_df) > 0:
                            # í•„ìš”í•œ ì»¬ëŸ¼ë§Œ ì„ íƒ
                            í•„ìš”_ì»¬ëŸ¼ = ['ì—…ì²´ëª…', 'ì§€ì—­', 'ì—…ì¢…', 'ì „í™”ë²ˆí˜¸', 'ì£¼ì†Œ', 'ë‹´ë‹¹ìž', 'ì˜ì—…ë‹¨ê³„', 'ë©”ëª¨', 'ë“±ë¡ì¼', 'ë°©ë¬¸ì¼', 'ê·œëª¨']
                            upload_df = upload_df[[col for col in í•„ìš”_ì»¬ëŸ¼ if col in upload_df.columns]]
                            
                            prospects_df = pd.concat([prospects_df, upload_df], ignore_index=True)
                            prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                            
                            st.success(f"""
                            âœ… **{len(upload_df):,}ê°œ** ì—…ì²´ ë“±ë¡ ì™„ë£Œ!
                            
                            - ì›ë³¸: {ì›ë³¸_ìˆ˜:,}ê°œ
                            - ê¸°ì¡´ ê±°ëž˜ì²˜ ì¤‘ë³µ ì œì™¸: {ì œì™¸_ê¸°ì¡´:,}ê°œ
                            - ìž ìž¬ê±°ëž˜ì²˜ ì¤‘ë³µ ì œì™¸: {ì œì™¸_ìž ìž¬:,}ê°œ
                            - **ìµœì¢… ë“±ë¡: {len(upload_df):,}ê°œ**
                            """)
                            st.rerun()
                        else:
                            st.warning("ëª¨ë“  ì—…ì²´ê°€ ì´ë¯¸ ë“±ë¡ë˜ì–´ ìžˆê±°ë‚˜ ê¸°ì¡´ ê±°ëž˜ì²˜ì™€ ì¤‘ë³µë©ë‹ˆë‹¤.")
            except Exception as e:
                st.error(f"íŒŒì¼ ì²˜ë¦¬ ì˜¤ë¥˜: {str(e)}")
        
        # ì „ì²´ ë°ì´í„° ê´€ë¦¬
        if len(prospects_df) > 0:
            st.markdown("---")
            st.markdown("#### ðŸ—„ï¸ ë°ì´í„° ê´€ë¦¬")
            
            col_dl1, col_dl2 = st.columns(2)
            
            with col_dl1:
                # ì „ì²´ ë‹¤ìš´ë¡œë“œ
                output2 = BytesIO()
                with pd.ExcelWriter(output2, engine='openpyxl') as writer:
                    prospects_df.to_excel(writer, index=False, sheet_name='ìž ìž¬ê±°ëž˜ì²˜')
                excel_data2 = output2.getvalue()
                
                st.download_button(
                    label=f"ðŸ“¥ ì „ì²´ ë‹¤ìš´ë¡œë“œ ({len(prospects_df):,}ê°œ)",
                    data=excel_data2,
                    file_name=f"ìž ìž¬ê±°ëž˜ì²˜_ì „ì²´_{get_kst_now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col_dl2:
                # ì „ì²´ ì‚­ì œ (ìœ„í—˜)
                ì‚­ì œ_í™•ì¸ = st.checkbox("âš ï¸ ì „ì²´ ì‚­ì œ í™•ì¸ (ì²´í¬ í›„ ì‚­ì œ ë²„íŠ¼ í´ë¦­)", key="delete_confirm_check")
                
                if ì‚­ì œ_í™•ì¸:
                    if st.button("ðŸ—‘ï¸ ì „ì²´ ë°ì´í„° ì‚­ì œ", type="secondary", key="delete_all_btn"):
                        prospects_df = pd.DataFrame(columns=['ì—…ì²´ëª…', 'ì§€ì—­', 'ì—…ì¢…', 'ì „í™”ë²ˆí˜¸', 'ì£¼ì†Œ', 'ë‹´ë‹¹ìž', 'ì˜ì—…ë‹¨ê³„', 'ë©”ëª¨', 'ë“±ë¡ì¼', 'ë°©ë¬¸ì¼', 'ê·œëª¨'])
                        prospects_df.to_csv(prospects_file, index=False, encoding='utf-8-sig')
                        st.success("âœ… ì „ì²´ ì‚­ì œ ì™„ë£Œ")
                        st.rerun()

# ==================== í˜‘ì•½ì„œ ê´€ë¦¬ ====================
elif menu == "ðŸ“œ í˜‘ì•½ì„œ ê´€ë¦¬":
    st.title("ðŸ“œ í˜‘ì•½ì„œ ê´€ë¦¬")
    st.info("ê±°ëž˜ì²˜ì™€ íŒë§¤í˜‘ì•½ì„ ì²´ê²°í•˜ê³  ì „ìžì„œëª…ìœ¼ë¡œ í˜‘ì•½ì„œë¥¼ ìƒì„±í•©ë‹ˆë‹¤.")
    
    # ë°ì´í„° ë””ë ‰í† ë¦¬
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # í˜‘ì•½ ë°ì´í„° íŒŒì¼
    agreement_file = os.path.join(data_dir, "agreements.csv")
    if os.path.exists(agreement_file):
        agreements_df = pd.read_csv(agreement_file, encoding='utf-8-sig')
    else:
        agreements_df = pd.DataFrame(columns=['í˜‘ì•½ë²ˆí˜¸', 'êµ¬ë§¤ìž_ìƒí˜¸', 'êµ¬ë§¤ìž_ëŒ€í‘œ', 'êµ¬ë§¤ìž_ì‚¬ì—…ìžë²ˆí˜¸', 'ê²°ì œë°©ì‹', 'ì™¸ìƒí•œë„', 'í˜‘ì•½ì‹œìž‘ì¼', 'í˜‘ì•½ì¢…ë£Œì¼', 'ì²´ê²°ì¼', 'ìƒíƒœ'])
    
    # íƒ­
    tab1, tab2 = st.tabs(["ðŸ“ í˜‘ì•½ì„œ ìž‘ì„±", "ðŸ“‹ í˜‘ì•½ ì´ë ¥"])
    
    # ===== íƒ­1: í˜‘ì•½ì„œ ìž‘ì„± =====
    with tab1:
        st.markdown("### ðŸ“ ì‹ ê·œ í˜‘ì•½ì„œ ìž‘ì„±")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ðŸ­ ê³µê¸‰ìž (ê°‘)")
            st.text("ìƒí˜¸: ëˆ„ë¦¬ì— ì•Œì˜¤")
            st.text("ëŒ€í‘œ: ë°•ìˆ˜ì˜")
            st.text("ì‚¬ì—…ìžë²ˆí˜¸: 320-14-00707")
        
        with col2:
            st.markdown("#### ðŸ¢ êµ¬ë§¤ìž (ì„)")
            êµ¬ë§¤ìž_ìƒí˜¸ = st.text_input("ìƒí˜¸", key="buyer_company")
            êµ¬ë§¤ìž_ëŒ€í‘œ = st.text_input("ëŒ€í‘œìž", key="buyer_ceo")
            êµ¬ë§¤ìž_ì‚¬ì—…ìžë²ˆí˜¸ = st.text_input("ì‚¬ì—…ìžë²ˆí˜¸", placeholder="000-00-00000", key="buyer_bizno")
        
        st.markdown("---")
        st.markdown("#### ðŸ“‹ í˜‘ì•½ ì¡°ê±´")
        
        col3, col4 = st.columns(2)
        with col3:
            ê²°ì œë°©ì‹ = st.selectbox("ê²°ì œë°©ì‹", ["í˜„ê¸ˆ", "ì›”ë§ê²°ì œ", "ìµì›”ê²°ì œ", "ê¸°íƒ€"], key="payment_method")
            ì™¸ìƒí•œë„ = st.number_input("ì™¸ìƒí•œë„ (ì›)", min_value=0, step=100000, value=1000000, key="credit_limit")
        
        with col4:
            í˜‘ì•½ì‹œìž‘ì¼ = st.date_input("í˜‘ì•½ ì‹œìž‘ì¼", value=get_kst_today(), key="start_date")
            í˜‘ì•½ì¢…ë£Œì¼ = st.date_input("í˜‘ì•½ ì¢…ë£Œì¼", value=get_kst_today().replace(year=get_kst_today().year + 1), key="end_date")
        
        st.markdown("---")
        st.markdown("#### âœï¸ ì „ìžì„œëª…")
        st.info("âœï¸ ì•„ëž˜ ì„œëª… í™•ì¸ëž€ì— ì²´í¬í•´ì£¼ì„¸ìš”.")
        
        # ì„œëª… í™•ì¸ (ì²´í¬ë°•ìŠ¤ ë°©ì‹)
        col_sign1, col_sign2 = st.columns(2)
        with col_sign1:
            st.markdown("**ê³µê¸‰ìž (ê°‘)**")
            ê³µê¸‰ìž_ì„œëª…í™•ì¸ = st.checkbox("âœ… ë°•ìˆ˜ì˜ ì„œëª… í™•ì¸", key="supplier_sign_check")
        with col_sign2:
            st.markdown(f"**êµ¬ë§¤ìž (ì„)**")
            êµ¬ë§¤ìž_ì„œëª…í™•ì¸ = st.checkbox(f"âœ… {êµ¬ë§¤ìž_ëŒ€í‘œ if êµ¬ë§¤ìž_ëŒ€í‘œ else 'êµ¬ë§¤ìž'} ì„œëª… í™•ì¸", key="buyer_sign_check")
        
        st.markdown("---")
        
        # í˜‘ì•½ì„œ ìƒì„± ë²„íŠ¼
        if st.button("ðŸ“„ í˜‘ì•½ì„œ ìƒì„± ë° ì €ìž¥", type="primary", use_container_width=True):
            if not êµ¬ë§¤ìž_ìƒí˜¸:
                st.error("âŒ êµ¬ë§¤ìž ìƒí˜¸ë¥¼ ìž…ë ¥í•´ì£¼ì„¸ìš”.")
            elif not êµ¬ë§¤ìž_ëŒ€í‘œ:
                st.error("âŒ êµ¬ë§¤ìž ëŒ€í‘œìžë¥¼ ìž…ë ¥í•´ì£¼ì„¸ìš”.")
            else:
                # í˜‘ì•½ë²ˆí˜¸ ìƒì„±
                í˜‘ì•½ë²ˆí˜¸ = f"AGR-{get_kst_now().strftime('%Y%m%d%H%M%S')}"
                
                # ë°ì´í„° ì €ìž¥
                new_agreement = {
                    'í˜‘ì•½ë²ˆí˜¸': í˜‘ì•½ë²ˆí˜¸,
                    'êµ¬ë§¤ìž_ìƒí˜¸': êµ¬ë§¤ìž_ìƒí˜¸,
                    'êµ¬ë§¤ìž_ëŒ€í‘œ': êµ¬ë§¤ìž_ëŒ€í‘œ,
                    'êµ¬ë§¤ìž_ì‚¬ì—…ìžë²ˆí˜¸': êµ¬ë§¤ìž_ì‚¬ì—…ìžë²ˆí˜¸,
                    'ê²°ì œë°©ì‹': ê²°ì œë°©ì‹,
                    'ì™¸ìƒí•œë„': ì™¸ìƒí•œë„,
                    'í˜‘ì•½ì‹œìž‘ì¼': str(í˜‘ì•½ì‹œìž‘ì¼),
                    'í˜‘ì•½ì¢…ë£Œì¼': str(í˜‘ì•½ì¢…ë£Œì¼),
                    'ì²´ê²°ì¼': get_kst_now().strftime('%Y-%m-%d %H:%M'),
                    'ìƒíƒœ': 'ìœ íš¨'
                }
                
                agreements_df = pd.concat([agreements_df, pd.DataFrame([new_agreement])], ignore_index=True)
                agreements_df.to_csv(agreement_file, index=False, encoding='utf-8-sig')
                
                # í˜‘ì•½ì„œ HTML ìƒì„±
                í˜‘ì•½ì„œ_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Malgun Gothic', sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }}
                        h1 {{ text-align: center; font-size: 28px; margin-bottom: 30px; }}
                        .section {{ margin-bottom: 15px; }}
                        .section-title {{ font-weight: bold; font-size: 14px; margin-bottom: 5px; }}
                        .section-content {{ font-size: 13px; line-height: 1.6; }}
                        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                        th, td {{ border: 1px solid #000; padding: 8px; text-align: left; font-size: 12px; }}
                        th {{ background-color: #f0f0f0; text-align: center; }}
                        .signature-area {{ display: flex; justify-content: space-around; margin-top: 40px; }}
                        .signature-box {{ text-align: center; width: 45%; }}
                        .signature-line {{ border-bottom: 1px solid #000; height: 60px; margin-bottom: 10px; }}
                        .center {{ text-align: center; }}
                        .small {{ font-size: 11px; color: #666; }}
                    </style>
                </head>
                <body>
                    <h1>íŒ ë§¤ í˜‘ ì•½ ì„œ</h1>
                    
                    <div class="section">
                        <div class="section-title">ì œ1ì¡° (ëª©ì )</div>
                        <div class="section-content">ë³¸ í˜‘ì•½ì€ ê³µê¸‰ìžì™€ êµ¬ë§¤ìž ê°„ì˜ ìƒí˜¸ ì‹ ë¢°ë¥¼ ë°”íƒ•ìœ¼ë¡œ ìž¥ê¸°ì ì´ê³  ì•ˆì •ì ì¸ ê±°ëž˜ê´€ê³„ë¥¼ êµ¬ì¶•í•˜ë©°, íŠ¹ë³„ í• ì¸ê°€ê²©ìœ¼ë¡œ ë¬¼í’ˆì„ ê³µê¸‰í•¨ì— ìžˆì–´ í•„ìš”í•œ ì‚¬í•­ì„ ì •í•¨ì„ ëª©ì ìœ¼ë¡œ í•œë‹¤.</div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">ì œ2ì¡° (ë‹¹ì‚¬ìž)</div>
                        <table>
                            <tr><th>êµ¬ë¶„</th><th>ê³µê¸‰ìž (ê°‘)</th><th>êµ¬ë§¤ìž (ì„)</th></tr>
                            <tr><td>ìƒí˜¸</td><td>ëˆ„ë¦¬ì— ì•Œì˜¤</td><td>{êµ¬ë§¤ìž_ìƒí˜¸}</td></tr>
                            <tr><td>ëŒ€í‘œ</td><td>ë°•ìˆ˜ì˜</td><td>{êµ¬ë§¤ìž_ëŒ€í‘œ}</td></tr>
                            <tr><td>ì‚¬ì—…ìžë²ˆí˜¸</td><td>320-14-00707</td><td>{êµ¬ë§¤ìž_ì‚¬ì—…ìžë²ˆí˜¸}</td></tr>
                        </table>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">ì œ3ì¡° (ê³µê¸‰í’ˆëª©)</div>
                        <div class="section-content">"ê°‘"ì€ "ì„"ì—ê²Œ ëˆ„ë¦¬ì— ì•Œì˜¤ ì ˆë‹¨ì„ ì œí’ˆ ë“±ì„ ê³µê¸‰í•œë‹¤.</div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">ì œ4ì¡° (ê°€ê²© ë° ê²°ì œì¡°ê±´)</div>
                        <div class="section-content">
                            1. "ê°‘"ì€ "ì„"ì—ê²Œ íŠ¹ë³„ í• ì¸ëœ í˜‘ì•½ê°€ê²©ìœ¼ë¡œ ê³µê¸‰í•œë‹¤.<br>
                            2. ê²°ì œë°©ì‹: {ê²°ì œë°©ì‹} / ì™¸ìƒí•œë„: {ì™¸ìƒí•œë„:,}ì›
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">ì œ5ì¡° (ë‚©í’ˆì¡°ê±´)</div>
                        <div class="section-content">1. ë‚©í’ˆìž¥ì†Œ: "ì„"ì´ ì§€ì •í•˜ëŠ” ìž¥ì†Œ / ë°°ì†¡ë¹„: ë¬´ë£Œ(100,000ì› ì´ìƒ), ìœ ë£Œ(100,000ì› ì´í•˜)</div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">ì œ6ì¡° (í˜‘ì•½ê¸°ê°„)</div>
                        <div class="section-content">1. í˜‘ì•½ê¸°ê°„: {í˜‘ì•½ì‹œìž‘ì¼} ~ {í˜‘ì•½ì¢…ë£Œì¼} / ë§Œë£Œ 30ì¼ ì „ ì´ì˜ ì—†ìœ¼ë©´ ìžë™ ì—°ìž¥</div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">ì œ7ì¡° (ê¸°íƒ€)</div>
                        <div class="section-content">1. í’ˆì§ˆ ë¶ˆëŸ‰ ì‹œ ë¬´ìƒ êµí™˜ ë˜ëŠ” í™˜ë¶ˆ 2. í˜‘ì•½ ë‚´ìš©ì€ ì˜ì—…ë¹„ë°€ë¡œ ì œ3ìž ëˆ„ì„¤ ê¸ˆì§€ 3. ë¶„ìŸ ì‹œ "ê°‘" ì†Œìž¬ì§€ ê´€í• ë²•ì›</div>
                    </div>
                    
                    <p class="center" style="margin-top: 30px;">ìœ„ í˜‘ì•½ ë‚´ìš©ì„ í™•ì¸í•˜ê³  ì‹ ì˜ì„±ì‹¤ì˜ ì›ì¹™ì— ë”°ë¼ ì´í–‰í•  ê²ƒì„ í™•ì•½í•˜ë©°,<br>í˜‘ì•½ì„œ 2ë¶€ë¥¼ ìž‘ì„±í•˜ì—¬ ì„œëª… ë‚ ì¸ í›„ ê° 1ë¶€ì”© ë³´ê´€í•œë‹¤.</p>
                    
                    <p class="center" style="font-weight: bold; margin-top: 20px;">í˜‘ì•½ ì²´ê²°ì¼: {get_kst_now().strftime('%Yë…„ %mì›” %dì¼')}</p>
                    
                    <div class="signature-area">
                        <div class="signature-box">
                            <div style="font-weight: bold;">ê³µê¸‰ìž (ê°‘)</div>
                            <div>ëˆ„ë¦¬ì— ì•Œì˜¤</div>
                            <div>ëŒ€í‘œ: ë°•ìˆ˜ì˜</div>
                            <div class="signature-line"></div>
                            <div>(ì„œëª…ë‚ ì¸)</div>
                        </div>
                        <div class="signature-box">
                            <div style="font-weight: bold;">êµ¬ë§¤ìž (ì„)</div>
                            <div>{êµ¬ë§¤ìž_ìƒí˜¸}</div>
                            <div>ëŒ€í‘œ: {êµ¬ë§¤ìž_ëŒ€í‘œ}</div>
                            <div class="signature-line"></div>
                            <div>(ì„œëª…ë‚ ì¸)</div>
                        </div>
                    </div>
                    
                    <p class="small center" style="margin-top: 30px;">í˜‘ì•½ë²ˆí˜¸: {í˜‘ì•½ë²ˆí˜¸}</p>
                </body>
                </html>
                """
                
                st.success(f"âœ… í˜‘ì•½ì„œê°€ ìƒì„±ë˜ì—ˆìŠµë‹ˆë‹¤! (í˜‘ì•½ë²ˆí˜¸: {í˜‘ì•½ë²ˆí˜¸})")
                
                # HTML ë‹¤ìš´ë¡œë“œ (UTF-8 ì¸ì½”ë”©)
                st.download_button(
                    label="ðŸ“¥ í˜‘ì•½ì„œ ë‹¤ìš´ë¡œë“œ (HTML)",
                    data=í˜‘ì•½ì„œ_html.encode('utf-8'),
                    file_name=f"íŒë§¤í˜‘ì•½ì„œ_{êµ¬ë§¤ìž_ìƒí˜¸}_{get_kst_now().strftime('%Y%m%d')}.html",
                    mime="text/html; charset=utf-8"
                )
                
                # ë¯¸ë¦¬ë³´ê¸°
                with st.expander("ðŸ“„ í˜‘ì•½ì„œ ë¯¸ë¦¬ë³´ê¸°", expanded=True):
                    st.components.v1.html(í˜‘ì•½ì„œ_html, height=800, scrolling=True)
    
    # ===== íƒ­2: í˜‘ì•½ ì´ë ¥ =====
    with tab2:
        st.markdown("### ðŸ“‹ í˜‘ì•½ ì´ë ¥")
        
        if len(agreements_df) > 0:
            # ìƒíƒœë³„ í•„í„°
            ìƒíƒœ_í•„í„° = st.selectbox("ìƒíƒœ í•„í„°", ["ì „ì²´", "ìœ íš¨", "ë§Œë£Œ", "í•´ì§€"], key="agreement_status_filter")
            
            if ìƒíƒœ_í•„í„° != "ì „ì²´":
                í‘œì‹œ_df = agreements_df[agreements_df['ìƒíƒœ'] == ìƒíƒœ_í•„í„°]
            else:
                í‘œì‹œ_df = agreements_df
            
            st.info(f"ðŸ“Š ì´ {len(í‘œì‹œ_df)}ê±´ì˜ í˜‘ì•½")
            
            for idx, row in í‘œì‹œ_df.iterrows():
                with st.expander(f"ðŸ“œ {row['êµ¬ë§¤ìž_ìƒí˜¸']} ({row['í˜‘ì•½ë²ˆí˜¸']}) - {row['ìƒíƒœ']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**êµ¬ë§¤ìž:** {row['êµ¬ë§¤ìž_ìƒí˜¸']}")
                        st.markdown(f"**ëŒ€í‘œ:** {row['êµ¬ë§¤ìž_ëŒ€í‘œ']}")
                        st.markdown(f"**ì‚¬ì—…ìžë²ˆí˜¸:** {row['êµ¬ë§¤ìž_ì‚¬ì—…ìžë²ˆí˜¸']}")
                    with col2:
                        st.markdown(f"**ê²°ì œë°©ì‹:** {row['ê²°ì œë°©ì‹']}")
                        st.markdown(f"**ì™¸ìƒí•œë„:** {row['ì™¸ìƒí•œë„']:,}ì›")
                        st.markdown(f"**ê¸°ê°„:** {row['í˜‘ì•½ì‹œìž‘ì¼']} ~ {row['í˜‘ì•½ì¢…ë£Œì¼']}")
                    
                    st.markdown(f"**ì²´ê²°ì¼:** {row['ì²´ê²°ì¼']}")
                    
                    # ìƒíƒœ ë³€ê²½
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if row['ìƒíƒœ'] == 'ìœ íš¨':
                            if st.button("ðŸš« í•´ì§€", key=f"terminate_{idx}"):
                                agreements_df.loc[idx, 'ìƒíƒœ'] = 'í•´ì§€'
                                agreements_df.to_csv(agreement_file, index=False, encoding='utf-8-sig')
                                st.rerun()
                    with col_btn2:
                        if st.button("ðŸ—‘ï¸ ì‚­ì œ", key=f"delete_{idx}"):
                            agreements_df = agreements_df.drop(idx)
                            agreements_df.to_csv(agreement_file, index=False, encoding='utf-8-sig')
                            st.rerun()
        else:
            st.info("ðŸ“­ ë“±ë¡ëœ í˜‘ì•½ì´ ì—†ìŠµë‹ˆë‹¤.")

# ==================== ì„¤ì • ====================
elif menu == "ðŸ”§ ì„¤ì •":
    st.title("ðŸ”§ ì„¤ì •")
    
    # íƒ­ ìƒì„±
    tab1, tab2, tab3, tab4 = st.tabs(["ðŸ¢ ì‚¬ì—…ìž ì •ë³´", "ðŸ—„ï¸ ë°ì´í„° ê´€ë¦¬", "ðŸ’° ì™¸ìƒ í˜„í™©", "ðŸ“Š í†µê³„"])
    
    # ===== íƒ­1: ì‚¬ì—…ìž ì •ë³´ =====
    with tab1:
        st.markdown("### ðŸ¢ ì‚¬ì—…ìž ì •ë³´ ì„¤ì •")
        st.info("ê±°ëž˜ëª…ì„¸ì„œ ì¶œë ¥ ì‹œ ì‚¬ìš©ë˜ëŠ” ì •ë³´ìž…ë‹ˆë‹¤.")
        
        company = st.session_state.company_info
        
        col1, col2 = st.columns(2)
        
        with col1:
            ìƒí˜¸ = st.text_input("ìƒí˜¸ (ì—…ì²´ëª…)", value=company.get('ìƒí˜¸', ''), key="company_name")
            ëŒ€í‘œìž = st.text_input("ëŒ€í‘œìžëª…", value=company.get('ëŒ€í‘œìž', ''), key="company_ceo")
            ì‚¬ì—…ìžë²ˆí˜¸ = st.text_input("ì‚¬ì—…ìžë²ˆí˜¸", value=company.get('ì‚¬ì—…ìžë²ˆí˜¸', ''), key="company_bizno")
        
        with col2:
            ì „í™”ë²ˆí˜¸ = st.text_input("ì „í™”ë²ˆí˜¸", value=company.get('ì „í™”ë²ˆí˜¸', ''), key="company_tel")
            íŒ©ìŠ¤ë²ˆí˜¸ = st.text_input("íŒ©ìŠ¤ë²ˆí˜¸", value=company.get('íŒ©ìŠ¤ë²ˆí˜¸', ''), key="company_fax")
        
        ì£¼ì†Œ = st.text_input("ì£¼ì†Œ", value=company.get('ì£¼ì†Œ', ''), key="company_addr")
        
        if st.button("ðŸ’¾ ì‚¬ì—…ìž ì •ë³´ ì €ìž¥", type="primary"):
            st.session_state.company_info = {
                'ìƒí˜¸': ìƒí˜¸,
                'ëŒ€í‘œìž': ëŒ€í‘œìž,
                'ì‚¬ì—…ìžë²ˆí˜¸': ì‚¬ì—…ìžë²ˆí˜¸,
                'ì£¼ì†Œ': ì£¼ì†Œ,
                'ì „í™”ë²ˆí˜¸': ì „í™”ë²ˆí˜¸,
                'íŒ©ìŠ¤ë²ˆí˜¸': íŒ©ìŠ¤ë²ˆí˜¸
            }
            save_company_info()
            st.success("âœ… ì‚¬ì—…ìž ì •ë³´ê°€ ì €ìž¥ë˜ì—ˆìŠµë‹ˆë‹¤!")
        
        st.markdown("---")
        st.markdown("#### ðŸ“„ í˜„ìž¬ ì €ìž¥ëœ ì •ë³´")
        st.markdown(f"""
        | í•­ëª© | ë‚´ìš© |
        |------|------|
        | ìƒí˜¸ | {company.get('ìƒí˜¸', '-')} |
        | ëŒ€í‘œìž | {company.get('ëŒ€í‘œìž', '-')} |
        | ì‚¬ì—…ìžë²ˆí˜¸ | {company.get('ì‚¬ì—…ìžë²ˆí˜¸', '-')} |
        | ì£¼ì†Œ | {company.get('ì£¼ì†Œ', '-')} |
        | ì „í™”ë²ˆí˜¸ | {company.get('ì „í™”ë²ˆí˜¸', '-')} |
        | íŒ©ìŠ¤ë²ˆí˜¸ | {company.get('íŒ©ìŠ¤ë²ˆí˜¸', '-')} |
        """)
    
    # ===== íƒ­2: ë°ì´í„° ê´€ë¦¬ =====
    with tab2:
        st.markdown("### ðŸ—„ï¸ ë°ì´í„° ê´€ë¦¬")
        
        # Google Sheets ë™ê¸°í™” ì„¹ì…˜
        st.markdown("#### â˜ï¸ Google Sheets ë™ê¸°í™”")
        if GSPREAD_AVAILABLE and "gcp_service_account" in st.secrets:
            st.success("âœ… Google Sheets ì—°ê²°ë¨")
            
            col_gs1, col_gs2 = st.columns(2)
            
            with col_gs1:
                if st.button("ðŸ“¤ Google Sheetsì— ë°±ì—…", type="primary", use_container_width=True):
                    with st.spinner("ë™ê¸°í™” ì¤‘..."):
                        success_count = 0
                        
                        # ê±°ëž˜ ë°ì´í„° ë™ê¸°í™”
                        if sync_to_google_sheets(st.session_state.ledger_df, "ê±°ëž˜ë‚´ì—­"):
                            success_count += 1
                        
                        # í’ˆëª© ë°ì´í„° ë™ê¸°í™”
                        if sync_to_google_sheets(st.session_state.products_df, "í’ˆëª©ëª©ë¡"):
                            success_count += 1
                        
                        # ê±°ëž˜ì²˜ ë°ì´í„° ë™ê¸°í™”
                        try:
                            from pathlib import Path
                            customers_file = Path("data") / "customers.csv"
                            if customers_file.exists():
                                customers_df = pd.read_csv(customers_file)
                                if sync_to_google_sheets(customers_df, "ê±°ëž˜ì²˜ëª©ë¡"):
                                    success_count += 1
                        except:
                            pass
                        
                        if success_count > 0:
                            st.success(f"âœ… {success_count}ê°œ ì‹œíŠ¸ ë™ê¸°í™” ì™„ë£Œ!")
                            st.balloons()
                        else:
                            st.error("ë™ê¸°í™” ì‹¤íŒ¨. ì„¤ì •ì„ í™•ì¸í•´ì£¼ì„¸ìš”.")
            
            with col_gs2:
                if st.button("ðŸ“¥ Google Sheetsì—ì„œ ë³µì›", use_container_width=True):
                    with st.spinner("ë°ì´í„° ë¶ˆëŸ¬ì˜¤ëŠ” ì¤‘..."):
                        # ê±°ëž˜ ë°ì´í„° ë³µì›
                        loaded_df = load_from_google_sheets("ê±°ëž˜ë‚´ì—­")
                        if loaded_df is not None and len(loaded_df) > 0:
                            # ë‚ ì§œ ì»¬ëŸ¼ ë³€í™˜
                            if 'ë‚ ì§œ' in loaded_df.columns:
                                loaded_df['ë‚ ì§œ'] = pd.to_datetime(loaded_df['ë‚ ì§œ'])
                            # ìˆ«ìž ì»¬ëŸ¼ ë³€í™˜
                            for col in ['ìˆ˜ëŸ‰', 'ë‹¨ê°€', 'ê³µê¸‰ê°€ì•¡', 'ë¶€ê°€ì„¸']:
                                if col in loaded_df.columns:
                                    loaded_df[col] = pd.to_numeric(loaded_df[col], errors='coerce').fillna(0)
                            
                            # âœ… 2019-08-01 ì´ì „ ë¶ˆí•„ìš”í•œ ë°ì´í„° í•„í„°ë§
                            loaded_df = loaded_df[loaded_df['ë‚ ì§œ'] >= '2019-08-01'].reset_index(drop=True)
                            
                            st.session_state.ledger_df = loaded_df
                            save_data()
                            st.success(f"âœ… {len(loaded_df)}ê±´ ê±°ëž˜ ë°ì´í„° ë³µì› ì™„ë£Œ!")
                            st.rerun()
                        else:
                            st.warning("Google Sheetsì— ë³µì›í•  ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
            
            st.caption("ðŸ’¡ ë°ì´í„°ê°€ ì˜êµ¬ ë³´ì¡´ë©ë‹ˆë‹¤. ì •ê¸°ì ìœ¼ë¡œ 'ë°±ì—…' ë²„íŠ¼ì„ ëˆŒëŸ¬ì£¼ì„¸ìš”!")
        else:
            st.warning("âš ï¸ Google Sheets ì—°ê²°ì´ ì„¤ì •ë˜ì§€ ì•Šì•˜ìŠµë‹ˆë‹¤.")
            st.caption("Streamlit Cloud â†’ Settings â†’ Secretsì—ì„œ ì„¤ì •í•´ì£¼ì„¸ìš”.")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ðŸ’¾ ë¡œì»¬ ë°±ì—…")
            if st.button("ðŸ“¥ ë°±ì—… íŒŒì¼ ë‹¤ìš´ë¡œë“œ"):
                df = st.session_state.ledger_df
                excel_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label="ðŸ“¥ CSV ë‹¤ìš´ë¡œë“œ",
                    data=excel_data,
                    file_name=f"ìž¥ë¶€ë°±ì—…_{get_kst_now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            st.markdown("#### ðŸ—‘ï¸ ë°ì´í„° ì´ˆê¸°í™”")
            if st.button("ðŸ—‘ï¸ ëª¨ë“  ë°ì´í„° ì‚­ì œ", type="secondary"):
                if st.checkbox("ì •ë§ ì‚­ì œí•˜ì‹œê² ìŠµë‹ˆê¹Œ?"):
                    st.session_state.ledger_df = pd.DataFrame(columns=['ë‚ ì§œ', 'ê±°ëž˜ì²˜', 'í’ˆëª©', 'ìˆ˜ëŸ‰', 'ë‹¨ê°€', 'ê³µê¸‰ê°€ì•¡', 'ë¶€ê°€ì„¸', 'ì°¸ì¡°', 'ë¹„ê³ '])
                    save_data()
                    st.success("ë°ì´í„°ê°€ ì´ˆê¸°í™”ë˜ì—ˆìŠµë‹ˆë‹¤.")
                    st.rerun()
    
    # ===== íƒ­3: ì™¸ìƒ í˜„í™© (ìžë™ ê³„ì‚°) =====
    with tab3:
        st.markdown("### ðŸ’° ì™¸ìƒ í˜„í™© (ì‹¤ì‹œê°„ ìžë™ ê³„ì‚°)")
        
        st.success("""
        **âœ… ìžë™ ê³„ì‚° ë°©ì‹:**
        - **ë¯¸ìˆ˜ê¸ˆ** = íŒë§¤(ì–‘ìˆ˜) + ë¶€ê°€ì„¸ - ìž…ê¸ˆ â†’ íŒë§¤ì²˜ì—ì„œ ë°›ì„ ëˆ
        - **ë¯¸ì§€ê¸‰ê¸ˆ** = |ë§¤ìž…(ìŒìˆ˜)| + |ë¶€ê°€ì„¸| - |ì¶œê¸ˆ| â†’ ë§¤ìž…ì²˜ì— ì¤„ ëˆ
        - ì»´ìž¥ë¶€ ì „ì²´ ë°ì´í„° ê¸°ë°˜ìœ¼ë¡œ ìžë™ ê³„ì‚°ë©ë‹ˆë‹¤.
        """)
        
        st.markdown("---")
        
        df = st.session_state.ledger_df
        
        if len(df) > 0:
            # ë¯¸ìˆ˜ê¸ˆ/ë¯¸ì§€ê¸‰ê¸ˆ ê³„ì‚°
            ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼ = calculate_all_receivables(df)
            ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼ = calculate_all_payables(df)
            
            # ìš”ì•½ í†µê³„
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ë¯¸ìˆ˜ê¸ˆ_df = ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼[ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼['ë¯¸ìˆ˜ê¸ˆ'] > 0] if len(ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼) > 0 else pd.DataFrame()
                ì´_ë¯¸ìˆ˜ê¸ˆ = ë¯¸ìˆ˜ê¸ˆ_df['ë¯¸ìˆ˜ê¸ˆ'].sum() if len(ë¯¸ìˆ˜ê¸ˆ_df) > 0 else 0
                st.metric("ì´ ë¯¸ìˆ˜ê¸ˆ", f"{ì´_ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›", help="íŒë§¤ì²˜ì—ì„œ ë°›ì„ ëˆ")
            
            with col2:
                st.metric("ë¯¸ìˆ˜ ê±°ëž˜ì²˜", f"{len(ë¯¸ìˆ˜ê¸ˆ_df)}ê°œ")
            
            with col3:
                ë¯¸ì§€ê¸‰ê¸ˆ_df = ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼[ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼['ë¯¸ì§€ê¸‰ê¸ˆ'] > 0] if len(ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼) > 0 else pd.DataFrame()
                ì´_ë¯¸ì§€ê¸‰ê¸ˆ = ë¯¸ì§€ê¸‰ê¸ˆ_df['ë¯¸ì§€ê¸‰ê¸ˆ'].sum() if len(ë¯¸ì§€ê¸‰ê¸ˆ_df) > 0 else 0
                st.metric("ì´ ë¯¸ì§€ê¸‰ê¸ˆ", f"{ì´_ë¯¸ì§€ê¸‰ê¸ˆ:,.0f}ì›", help="ë§¤ìž…ì²˜ì— ì¤„ ëˆ")
            
            with col4:
                st.metric("ë¯¸ì§€ê¸‰ ê±°ëž˜ì²˜", f"{len(ë¯¸ì§€ê¸‰ê¸ˆ_df)}ê°œ")
            
            st.markdown("---")
            
            # ê±°ëž˜ì²˜ë³„ ì¡°íšŒ
            st.markdown("#### ðŸ” ê±°ëž˜ì²˜ë³„ ì™¸ìƒ ì¡°íšŒ")
            ê±°ëž˜ì²˜_list = sorted(df['ê±°ëž˜ì²˜'].dropna().unique().tolist())
            ì„ íƒ_ê±°ëž˜ì²˜ = st.selectbox("ê±°ëž˜ì²˜ ì„ íƒ", [""] + ê±°ëž˜ì²˜_list, key="settings_recv_search")
            
            if ì„ íƒ_ê±°ëž˜ì²˜:
                ê±°ëž˜ì²˜_ë¯¸ìˆ˜ê¸ˆ = calculate_receivable(ì„ íƒ_ê±°ëž˜ì²˜)
                ê±°ëž˜ì²˜_ë¯¸ì§€ê¸‰ê¸ˆ = calculate_payable(ì„ íƒ_ê±°ëž˜ì²˜)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if ê±°ëž˜ì²˜_ë¯¸ìˆ˜ê¸ˆ > 0:
                        st.warning(f"âš ï¸ **ë¯¸ìˆ˜ê¸ˆ**: {ê±°ëž˜ì²˜_ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›")
                    elif ê±°ëž˜ì²˜_ë¯¸ìˆ˜ê¸ˆ < 0:
                        st.info(f"ðŸ’° **ì„ ìˆ˜ê¸ˆ**: {abs(ê±°ëž˜ì²˜_ë¯¸ìˆ˜ê¸ˆ):,.0f}ì›")
                    else:
                        st.success("âœ… ë¯¸ìˆ˜ê¸ˆ ì—†ìŒ")
                
                with col2:
                    if ê±°ëž˜ì²˜_ë¯¸ì§€ê¸‰ê¸ˆ > 0:
                        st.error(f"ðŸ’¸ **ë¯¸ì§€ê¸‰ê¸ˆ**: {ê±°ëž˜ì²˜_ë¯¸ì§€ê¸‰ê¸ˆ:,.0f}ì›")
                    elif ê±°ëž˜ì²˜_ë¯¸ì§€ê¸‰ê¸ˆ < 0:
                        st.info(f"ðŸ’µ **ì„ ê¸‰ê¸ˆ**: {abs(ê±°ëž˜ì²˜_ë¯¸ì§€ê¸‰ê¸ˆ):,.0f}ì›")
                    else:
                        st.success("âœ… ë¯¸ì§€ê¸‰ê¸ˆ ì—†ìŒ")
                
                # ìµœê·¼ ê±°ëž˜ ë‚´ì—­
                ê±°ëž˜ì²˜_df = df[df['ê±°ëž˜ì²˜'] == ì„ íƒ_ê±°ëž˜ì²˜].sort_values('ë‚ ì§œ', ascending=False)
                if len(ê±°ëž˜ì²˜_df) > 0:
                    st.markdown(f"#### ðŸ“‹ {ì„ íƒ_ê±°ëž˜ì²˜} ìµœê·¼ ê±°ëž˜ ë‚´ì—­")
                    
                    display_ê±°ëž˜ = ê±°ëž˜ì²˜_df.head(20).copy()
                    display_ê±°ëž˜['ë‚ ì§œ'] = pd.to_datetime(display_ê±°ëž˜['ë‚ ì§œ']).dt.strftime('%Y-%m-%d')
                    display_ê±°ëž˜ = display_ê±°ëž˜[['ë‚ ì§œ', 'í’ˆëª©', 'ê³µê¸‰ê°€ì•¡', 'ë¶€ê°€ì„¸']]
                    
                    for col in ['ê³µê¸‰ê°€ì•¡', 'ë¶€ê°€ì„¸']:
                        display_ê±°ëž˜[col] = display_ê±°ëž˜[col].apply(lambda x: f"{x:,.0f}")
                    
                    st.dataframe(display_ê±°ëž˜, use_container_width=True, hide_index=True)
        else:
            st.info("ì•„ì§ ê±°ëž˜ ë°ì´í„°ê°€ ì—†ìŠµë‹ˆë‹¤.")
    
    # ===== íƒ­4: í†µê³„ =====
    with tab4:
        st.markdown("### ðŸ“Š í†µê³„")
        
        df = st.session_state.ledger_df
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ì´ ê±°ëž˜ ê±´ìˆ˜", f"{len(df)}ê±´")
        with col2:
            st.metric("ê±°ëž˜ì²˜ ìˆ˜", f"{df['ê±°ëž˜ì²˜'].nunique()}ê°œ")
        with col3:
            st.metric("ë°ì´í„° ê¸°ê°„", f"{(df['ë‚ ì§œ'].max() - df['ë‚ ì§œ'].min()).days}ì¼" if len(df) > 0 else "0ì¼")
        
        st.markdown("---")
        
        # ì‹¤ì‹œê°„ ì™¸ìƒ í†µê³„
        ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼ = calculate_all_receivables(df)
        ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼ = calculate_all_payables(df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### ðŸ“¤ ë¯¸ìˆ˜ê¸ˆ (ë°›ì„ ëˆ)")
            ë¯¸ìˆ˜ê¸ˆ_df = ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼[ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼['ë¯¸ìˆ˜ê¸ˆ'] > 0] if len(ë¯¸ìˆ˜ê¸ˆ_ê²°ê³¼) > 0 else pd.DataFrame()
            ì´_ë¯¸ìˆ˜ê¸ˆ = ë¯¸ìˆ˜ê¸ˆ_df['ë¯¸ìˆ˜ê¸ˆ'].sum() if len(ë¯¸ìˆ˜ê¸ˆ_df) > 0 else 0
            st.metric("ì´ ë¯¸ìˆ˜ê¸ˆ", f"{ì´_ë¯¸ìˆ˜ê¸ˆ:,.0f}ì›")
        
        with col2:
            st.markdown("##### ðŸ“¥ ë¯¸ì§€ê¸‰ê¸ˆ (ì¤„ ëˆ)")
            ë¯¸ì§€ê¸‰ê¸ˆ_df = ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼[ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼['ë¯¸ì§€ê¸‰ê¸ˆ'] > 0] if len(ë¯¸ì§€ê¸‰ê¸ˆ_ê²°ê³¼) > 0 else pd.DataFrame()
            ì´_ë¯¸ì§€ê¸‰ê¸ˆ = ë¯¸ì§€ê¸‰ê¸ˆ_df['ë¯¸ì§€ê¸‰ê¸ˆ'].sum() if len(ë¯¸ì§€ê¸‰ê¸ˆ_df) > 0 else 0
            st.metric("ì´ ë¯¸ì§€ê¸‰ê¸ˆ", f"{ì´_ë¯¸ì§€ê¸‰ê¸ˆ:,.0f}ì›")

# í‘¸í„°
st.sidebar.markdown("---")
st.sidebar.markdown("### ðŸ“Œ ì •ë³´")
st.sidebar.info(f"""
**í”„ë¡œê·¸ëž¨:** ëˆ„ë¦¬ì— ì•Œì˜¤ ìž¥ë¶€ê´€ë¦¬  
**ë²„ì „:** 1.2.0  
**ë°ì´í„°:** {len(st.session_state.ledger_df)}ê±´  
**ìµœì¢… ìˆ˜ì •:** {get_kst_now().strftime('%Y-%m-%d %H:%M')}
""")

st.sidebar.markdown("---")
if st.sidebar.button("ðŸ”’ ë¡œê·¸ì•„ì›ƒ", use_container_width=True):
    logout()