import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(layout="wide")

if "current_stock" not in st.session_state: st.session_state.current_stock = ""

st.title("🇰🇷 한국장 실전 타점 분석기")

code_input = st.text_input("종목코드 6자리 입력 (예: 005930)", key="search_box")

@st.cache_data
def load_all_stocks():
    import FinanceDataReader as fdr
    return fdr.StockListing('KRX')[['Code', 'Name', 'Market']]

stocks = load_all_stocks()

if code_input and len(code_input) == 6:
    match = stocks[stocks['Code'] == code_input]
    if not match.empty:
        market = match['Market'].iloc[0]
        suffix = ".KS" if market == 'KOSPI' else ".KQ"
        st.session_state.current_stock = code_input + suffix
    else:
        st.error("종목코드를 확인해주세요.")

if st.session_state.current_stock:
    code = st.session_state.current_stock
    
    try:
        ticker = yf.Ticker(code)
        # 데이터가 너무 짧으면 에러가 나므로 기간을 넉넉하게 잡음
        df_daily = ticker.history(period="1mo")
        df_10m = ticker.history(period="5d", interval="15m")
        
        if not df_daily.empty:
            # [핵심] 빈 값(NaN)이 있으면 0으로 채우고 강제로 숫자로 변환
            for df in [df_daily, df_10m]:
                df.fillna(0, inplace=True)
                df['Close'] = pd.to_numeric(df['Close'])
            
            st.subheader(f"🏢 {ticker.info.get('longName', '조회 종목')}")
            
            # 볼린저 밴드 계산
            for df in [df_daily, df_10m]:
                df['MA20'] = df['Close'].rolling(20, min_periods=1).mean()
                df['STD'] = df['Close'].rolling(20, min_periods=1).std()
                df['Upper'] = df['MA20'] + (df['STD'] * 2)
                df['Lower'] = df['MA20'] - (df['STD'] * 2)
            
            current_price = int(df_daily['Close'].iloc[-1])
            st.metric("현재가", f"{current_price:,}원")
            
            # 상태 판단
            lower_val = int(df_10m['Lower'].iloc[-1])
            if current_price < lower_val:
                status = "🟢 [진입] 눌림목 구간"
            else:
                status = "🔴 [관망] 고점 구간"
            
            st.markdown(f"### AI 상태: {status}")
            
            # 차트
            c1, c2 = st.columns(2)
            with c1: 
                st.markdown("##### ⏱️ 15분봉 차트")
                st.line_chart(df_10m[['Close', 'MA20']])
            with c2: 
                st.markdown("##### 📅 일봉 차트")
                st.line_chart(df_daily[['Close', 'MA20']])
            
    except Exception as e:
        st.error(f"데이터 처리 오류: {e}")
