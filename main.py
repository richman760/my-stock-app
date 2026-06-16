import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(layout="wide")

# 🔍 검색창 상태 유지
if "current_stock" not in st.session_state: st.session_state.current_stock = ""

st.title("🇰🇷 한국장 실전 타점 분석기 (yfinance 버전)")

code_input = st.text_input("종목코드 입력 (예: 005930.KS)", key="search_box")

if code_input:
    st.session_state.current_stock = code_input

if st.session_state.current_stock:
    code = st.session_state.current_stock
    # 한국 주식은 뒤에 .KS나 .KQ를 붙여야 합니다.
    if not code.endswith(('.KS', '.KQ')):
        code += ".KS"
    
    try:
        # 데이터 호출
        ticker = yf.Ticker(code)
        df_daily = ticker.history(period="6mo")
        df_10m = ticker.history(period="5d", interval="15m") # yfinance는 10분봉 대신 15분봉 지원
        
        if df_daily.empty:
            st.error("데이터를 찾을 수 없습니다. 종목코드를 확인하세요.")
        else:
            st.subheader(f"🏢 {ticker.info.get('longName', code)}")
            
            # 볼린저 밴드 계산
            for df in [df_daily, df_10m]:
                df['MA20'] = df['Close'].rolling(20).mean()
                df['STD'] = df['Close'].rolling(20).std()
                df['Upper'] = df['MA20'] + (df['STD'] * 2)
                df['Lower'] = df['MA20'] - (df['STD'] * 2)
            
            current_price = df_daily['Close'].iloc[-1]
            st.metric("현재가", f"{int(current_price):,}원")
            
            # 타점 분석
            if current_price < df_10m['Lower'].iloc[-1]:
                status = "🟢 [진입] 눌림목 구간"
            else:
                status = "🔴 [관망] 고점 구간"
            
            st.markdown(f"### AI 상태: {status}")
            
            # 차트
            c1, c2 = st.columns(2)
            with c1: st.line_chart(df_10m[['Close', 'MA20']])
            with c2: st.line_chart(df_daily[['Close', 'MA20']])
            
    except Exception as e:
        st.error(f"오류 발생: {e}")
