import streamlit as st
# 라이브러리 이름이 finance_datareader로 호출되는 것이 표준입니다.
import finance_datareader as fdr 
import datetime

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