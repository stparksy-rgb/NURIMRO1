import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# 페이지 설정
st.set_page_config(
    page_title="누리엠알오 장부관리",
    page_icon="📊",
    layout="wide"
)

# 커스텀 CSS - 다크 테마 + 글자 크기/두께 개선
st.markdown("""
<style>
    /* 전체 배경 다크 모드 */
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
    }
    
    /* 모든 텍스트 크기 1.5배 + 두껍게 */
    .stApp, p, span, div, label {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }
    
    /* 제목 크기 */
    h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    h2 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    h3 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    /* 입력란 스타일 - 하얀 배경 + 진한 테두리 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 3px solid #4a4a4a !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        padding: 12px !important;
        border-radius: 8px !important;
    }
    
    /* 드롭다운 선택창 */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 3px solid #4a4a4a !important;
    }
    
    /* 라벨 텍스트 */
    .stTextInput > label,
    .stTextArea > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stDateInput > label,
    .stRadio > label {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-bottom: 8px !important;
    }
    
    /* 버튼 */
    .stButton > button {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        padding: 15px 30px !important;
        border-radius: 8px !important;
    }
    
    /* 메트릭 (지표) */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }
    
    /* 데이터프레임 */
    .stDataFrame {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
    }
    
    /* 카드 배경 */
    [data-testid="stVerticalBlock"] > div {
        background-color: #2a2a2a;
        padding: 20px;
        border-radius: 10px;
    }
    
    /* Info 박스 */
    .stAlert {
        background-color: #3a3a3a !important;
        color: #ffffff !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        border: 2px solid #4a4a4a !important;
    }
    
    /* 라디오 버튼 텍스트 */
    .stRadio > div {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* 체크박스 */
    .stCheckbox > label {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }
    
    /* 구분선 */
    hr {
        border-color: #4a4a4a !important;
        border-width: 2px !important;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 파일 경로
DATA_FILE = "data/ledger.csv"

# 세션 상태 초기화
if 'ledger_df' not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state.ledger_df = pd.read_csv(DATA_FILE, parse_dates=['날짜'])
    else:
        st.session_state.ledger_df = pd.DataFrame(columns=['날짜', '거래처', '품목', '수량', '단가', '공급가액', '부가세', '참조'])

# 데이터 저장 함수
def save_data():
    st.session_state.ledger_df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 사이드바 - 메뉴
st.sidebar.title("📋 장부 관리 시스템")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "메뉴 선택",
    ["🏠 대시보드", "➕ 거래 입력", "📄 거래 내역", "📊 통계 분석", "💰 외상 관리", "⚙️ 설정"]
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
    
    # 기존 거래처, 품목 목록
    거래처_list = sorted(df['거래처'].dropna().unique().tolist()) if len(df) > 0 else []
    
    col1, col2 = st.columns(2)
    
    with col1:
        거래일자 = st.date_input("거래 날짜", value=datetime.now())
        
        # 거래처 입력 (자동완성)
        거래처_입력방식 = st.radio("거래처 입력 방식", ["기존 거래처 선택", "새 거래처 입력"], horizontal=True)
        
        if 거래처_입력방식 == "기존 거래처 선택":
            거래처 = st.selectbox("거래처 선택", [""] + 거래처_list)
        else:
            거래처 = st.text_input("거래처명")
        
        품목 = st.text_area("품목 [적요]", height=100)
        
    with col2:
        거래유형 = st.selectbox("거래 유형", ["=입금", "=출금", "=외입", "=견적"])
        
        수량 = st.number_input("수량", min_value=0.0, value=0.0, step=1.0)
        단가 = st.number_input("단가", min_value=0.0, value=0.0, step=100.0)
        
        # 공급가액 자동 계산
        if 거래유형 == "=출금":
            공급가액 = -(수량 * 단가 if 수량 > 0 and 단가 > 0 else st.number_input("공급가액", value=0.0, step=1000.0))
        else:
            공급가액 = 수량 * 단가 if 수량 > 0 and 단가 > 0 else st.number_input("공급가액", value=0.0, step=1000.0)
        
        # 부가세 자동 계산 (외입인 경우)
        if 거래유형 == "=외입":
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
        거래처별_외상['미수금'] = 거래처별_외상['공급가액'] + 거래처별_외상['부가세'] - 거래처별_외상['입금액']
        
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
        else:
            st.success("✅ 미수금이 없습니다!")

# ==================== 설정 ====================
elif menu == "⚙️ 설정":
    st.title("⚙️ 설정")
    
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
    
    st.markdown("---")
    st.markdown("### 📊 통계")
    
    df = st.session_state.ledger_df
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 거래 건수", f"{len(df)}건")
    with col2:
        st.metric("거래처 수", f"{df['거래처'].nunique()}개")
    with col3:
        st.metric("데이터 기간", f"{(df['날짜'].max() - df['날짜'].min()).days}일" if len(df) > 0 else "0일")

# 푸터
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 정보")
st.sidebar.info(f"""
**프로그램:** 누리엠알오 장부관리  
**버전:** 1.0.0  
**데이터:** {len(st.session_state.ledger_df)}건  
**최종 수정:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
""")