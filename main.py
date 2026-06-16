import sys
import subprocess

# 혹시 모를 라이브러리 설치 문제 해결
try:
    import finance_datareader as fdr
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "finance-datareader"])
    import finance_datareader as fdr

import streamlit as st
import datetime
# ... (나머지 코드 그대로)
st.title("🇰🇷 한국장 검색기")

code = st.text_input("종목코드(6자리) 입력")

if code and len(code) == 6:
    try:
        # 데이터 호출
        df = fdr.DataReader(code, datetime.date.today())
        price = int(df['Close'].iloc[-1])
        
        # 타점 계산
        target = int(price * 1.01)
        stop = int(price * 0.98)
        
        st.metric("현재가", f"{price:,}원")
        st.success(f"매수: {price:,}원")
        st.info(f"목표: {target:,}원")
        st.error(f"손절: {stop:,}원")
    except Exception as e:
        st.error(f"데이터를 불러올 수 없습니다: {e}")
# ... (위쪽 기존 퀀트 코드 그대로 유지)

# 🚀 [추가] 사이드바에 한국장 검색기 추가 (기존 환경 그대로 활용)
st.sidebar.markdown("---")
st.sidebar.subheader("🇰🇷 한국장 단일 검색")
code = st.sidebar.text_input("종목코드 6자리 입력", key="side_search")

if code and len(code) == 6:
    try:
        # 이미 퀀트 앱에 있는 fdr 환경을 그대로 가져다 씁니다.
        df = fdr.DataReader(code, datetime.date.today())
        price = int(df['Close'].iloc[-1])
        st.sidebar.success(f"현재가: {price:,}원")
        st.sidebar.info(f"목표: {int(price*1.01):,}원")
        st.sidebar.error(f"손절: {int(price*0.98):,}원")
    except:
        st.sidebar.error("코드를 확인하세요.")

# ... (아래쪽 히스토리 코드 그대로 유지)
