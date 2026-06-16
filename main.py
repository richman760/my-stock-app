import streamlit as st
import finance_datareader as fdr
import datetime

st.title("🇰🇷 한국장 검색기")

code = st.text_input("종목코드(6자리) 입력")

if code and len(code) == 6:
    try:
        # finance-datareader 라이브러리 사용
        df = fdr.DataReader(code, datetime.date.today())
        price = int(df['Close'].iloc[-1])
        
        st.metric("현재가", f"{price:,}원")
        st.success(f"매수: {int(price*1.01):,}원")
        st.error(f"손절: {int(price*0.98):,}원")
    except Exception as e:
        st.error("데이터를 불러올 수 없습니다.")
