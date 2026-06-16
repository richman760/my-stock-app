import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(layout="wide")

# 세션 및 새로고침 방어 (삭제 절대 금지!)
if "current_stock" not in st.session_state: st.session_state.current_stock = ""
if "code" in st.query_params: st.session_state.current_stock = st.query_params["code"]

st.title("💰 실전 매매 & 홀딩 판단 엔진")

# 검색창
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
        
        # 데이터 정제
        for df in [df_daily, df_10m]:
            df.ffill(inplace=True)
            df['MA20'] = df['Close'].rolling(20, min_periods=1).mean()

        cur = float(df_10m['Close'].iloc[-1])
        ma20_10m = float(df_10m['MA20'].iloc[-1])
        open_price = float(df_10m['Open'].iloc[-1])
        target_daily = float(df_daily['Close'].iloc[-1] * 1.03)

        # 🏢 [추가] 종목명과 갱신 시간 표시
        st.subheader(f"🏢 {ticker.info.get('longName', '조회 종목')}")
        st.caption(f"⏱️ 마지막 갱신 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if st.button("🔄 새로고침"): st.rerun()

        # 🤖 매매 판단 로직
        is_strong = (cur > ma20_10m) and (cur > open_price)
        
        st.subheader("🤖 AI 매매 전략 가이드")
        if is_strong:
            decision = "🔥 [보유 전략] 추세가 강합니다. 단기 익절 후 종가까지 추세 보유를 강력 추천합니다."
        elif cur < ma20_10m:
            decision = "🟢 [단기 타점] 10분봉 눌림목입니다. 1.5% 수익 시 분할 매도하고 나머지는 흐름을 보세요."
        else:
            decision = "🔴 [관망/매도] 추세가 꺾였습니다. 수익 중이라면 전량 매도하세요."

        st.info(f"### {decision}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("현재가", f"{int(cur):,}원")
        col2.metric("단기 목표가", f"{int(cur * 1.015):,}원")
        col3.metric("🛡️ 손절가", f"{int(cur * 0.98):,}원")
        col4.metric("종가 목표", f"{int(target_daily):,}원")

        st.write("---")
        st.write("📌 **전략:** 추세가 '강함'일 때는 종가까지 홀딩, 아닐 때는 단기 목표가에서 분할 매도하세요.")

    except Exception as e:
        st.error(f"데이터 분석 오류: {e}")
