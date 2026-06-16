import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(layout="wide")

# 세션 및 새로고침 방어 (삭제 금지)
if "current_stock" not in st.session_state: st.session_state.current_stock = ""
if "code" in st.query_params: st.session_state.current_stock = st.query_params["code"]

st.title("💰 실전 타점 & 매매 판단 엔진")

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
        target_daily = float(df_daily['MA20'].iloc[-1] * 1.05)

        st.caption(f"⏱️ 갱신: {datetime.datetime.now().strftime('%H:%M:%S')}")
        
        # 🤖 AI 판단 로직 (신호등 시스템)
        st.subheader("🤖 AI 매매 판단")
        if cur <= ma20_10m:
            # 단기 눌림목일 때
            if cur < df_daily['Close'].iloc[-1]: # 일봉보다 아래면 저점
                decision = "🟢 [매수 OK] 10분봉 눌림목 구간입니다. 진입 후 종가까지 추세 보유하세요."
            else:
                decision = "🟡 [분할 매도] 단기 반등 시 일부 익절 후 일봉 흐름을 확인하세요."
        else:
            decision = "🔴 [관망] 현재가 고점 구간입니다. 눌림목(10분봉 20선)까지 기다리세요."

        st.info(f"### {decision}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("현재가", f"{int(cur):,}원")
        col2.metric("단기 목표(1.5%)", f"{int(cur * 1.015):,}원")
        col3.metric("일봉 종가 목표", f"{int(target_daily):,}원")
        
        st.write("---")
        st.write("📌 **전략:** 10분봉 20선 근처에서 매수하고, 단기 목표가 도달 시 분할 매도 후 일봉 종가 목표가까지 홀딩 여부를 결정하세요.")

    except Exception as e:
        st.error(f"데이터 분석 오류: {e}")
