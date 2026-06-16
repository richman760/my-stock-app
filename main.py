import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(layout="wide")

if "current_stock" not in st.session_state: st.session_state.current_stock = ""

st.title("💰 실전 타점 & 수익률 가이드")

code_input = st.text_input("종목코드 6자리 입력", key="search_box")

# 종목 코드 매칭 로직
@st.cache_data
def load_all_stocks():
    import FinanceDataReader as fdr
    return fdr.StockListing('KRX')[['Code', 'Name', 'Market']]

stocks = load_all_stocks()

if code_input and len(code_input) == 6:
    match = stocks[stocks['Code'] == code_input]
    if not match.empty:
        market = match['Market'].iloc[0]
        st.session_state.current_stock = code_input + (".KS" if market == 'KOSPI' else ".KQ")

if st.session_state.current_stock:
    try:
        ticker = yf.Ticker(st.session_state.current_stock)
        df_10m = ticker.history(period="5d", interval="15m")
        df_daily = ticker.history(period="1mo")
        
        # 데이터 정제
        for df in [df_daily, df_10m]:
            df.fillna(method='ffill', inplace=True)
            df['MA20'] = df['Close'].rolling(20).mean()
        
        cur = df_10m['Close'].iloc[-1]
        ma20_10m = df_10m['MA20'].iloc[-1]
        target_daily = df_daily['MA20'].iloc[-1] * 1.05 # 일봉 20선 대비 5% 목표

        st.subheader(f"🏢 {ticker.info.get('longName', '조회 종목')}")
        
        # 1. 진입 여부 판별 (10분봉 기준)
        if cur < ma20_10m:
            buy_price = cur
            advice = "🟢 [진입] 10분봉 20선 아래입니다. 지금 진입하세요."
        else:
            buy_price = ma20_10m
            advice = f"🔴 [대기] 10분봉 20선({int(ma20_10m):,}원)까지 눌릴 때 진입하세요."

        # 2. 수익 분석
        profit_potential = ((target_daily - buy_price) / buy_price) * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("추천 매수가", f"{int(buy_price):,}원")
        col2.metric("일봉 종가 목표가", f"{int(target_daily):,}원")
        col3.metric("예상 수익률", f"{profit_potential:.2f}%")
        
        st.info(f"### 🤖 매매 전략: {advice}")
        st.write(f"- 10분봉 기준으로 {int(buy_price):,}원에 진입하여 일봉 흐름상 {int(target_daily):,}원까지 홀딩하는 전략입니다.")
        st.write(f"- 종가 기준 수익률이 {profit_potential:.2f}% 이상 예상되면 종가까지 보유를 추천합니다.")

    except Exception as e:
        st.error(f"분석 오류: {e}")
