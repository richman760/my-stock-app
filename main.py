import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(layout="wide")

# 세션 및 새로고침 방어
if "current_stock" not in st.session_state: st.session_state.current_stock = ""
if "code" in st.query_params: st.session_state.current_stock = st.query_params["code"]

st.title("💰 실전 매매 전략 가이드")

code_input = st.text_input("종목코드 6자리 입력", key="search_box")

if code_input and len(code_input) == 6:
    code = code_input + (".KS" if int(code_input) < 300000 else ".KQ")
    st.session_state.current_stock = code
    st.query_params["code"] = code

if st.session_state.current_stock:
    try:
        ticker = yf.Ticker(st.session_state.current_stock)
        df_10m = ticker.history(period="5d", interval="15m")
        df_daily = ticker.history(period="1mo")
        
        for df in [df_daily, df_10m]:
            df.ffill(inplace=True)
            df['MA20'] = df['Close'].rolling(20, min_periods=1).mean()

        cur = float(df_10m['Close'].iloc[-1])
        ma20_10m = float(df_10m['MA20'].iloc[-1])
        target_daily = float(df_daily['Close'].iloc[-1] * 1.03) # 종가 기준 3% 목표

        st.subheader(f"🏢 {ticker.info.get('longName', '조회 종목')}")
        st.caption(f"⏱️ 갱신: {datetime.datetime.now().strftime('%H:%M:%S')}")
        if st.button("🔄 새로고침"): st.rerun()

        # 🤖 3단계 매매 전략 엔진
        st.subheader("🤖 AI 매매 전략 가이드")
        
        if cur < ma20_10m:
            # 전략 1: 10분봉 눌림목 진입
            profit_target = cur * 1.015 # 단기 1.5% 목표
            st.info(f"### 🟢 [단기 타점] 10분봉 20선 아래 진입 구간")
            st.write(f"1. **단기 전략:** 현재가에서 진입하여 **{int(profit_target):,}원(+1.5%)** 도달 시 **즉시 익절**하세요.")
            st.write(f"2. **종가 추세:** 일봉 흐름상 추가 상승 여력이 보이므로, 익절 후 남은 물량은 **{int(target_daily):,}원**까지 종가 보유를 고려하세요.")
        
        elif cur < ma20_10m * 1.02:
            # 전략 2: 애매한 구간
            st.warning("### 🟡 [대기/관망] 방향성 탐색 구간")
            st.write("20선 근처에서 등락 중입니다. 확실하게 20선을 지지받는지 확인 후 진입하세요.")
            
        else:
            # 전략 3: 과열 구간
            st.error("### 🔴 [매도/관망] 과열 구간")
            st.write("단기 고점입니다. 신규 진입은 절대 금지하며, 보유 물량은 수익 실현하세요.")

        col1, col2, col3 = st.columns(3)
        col1.metric("현재가", f"{int(cur):,}원")
        col2.metric("단기 익절가(1.5%)", f"{int(cur * 1.015):,}원")
        col3.metric("일봉 종가 목표", f"{int(target_daily):,}원")

    except Exception as e:
        st.error(f"데이터 오류: {e}")
