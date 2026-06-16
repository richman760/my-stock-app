import streamlit as st
import FinanceDataReader as fdr
import datetime

st.title("KR 한국장 검색기")

code = st.text_input("종목코드(6자리) 입력")

if code and len(code) == 6:
    try:
        df = fdr.DataReader(code, datetime.date.today())
        price = int(df['Close'].iloc[-1])
        
        # 📊 타점 상식적으로 재설정
        buy = price                     # 매수가: 현재가 기준 (또는 int(price * 0.99) 로 하면 -1% 눌림목 매수)
        target = int(price * 1.03)      # 목표가: +3% 수익 
        stop = int(price * 0.98)        # 손절가: -2% 하락 시 손절
        
        st.metric("현재가", f"{price:,}원")
        st.success(f"🎯 목표: {target:,}원")
        st.info(f"✅ 매수: {buy:,}원")
        st.error(f"🛡️ 손절: {stop:,}원")
        
    except Exception as e:
        st.error("데이터를 불러올 수 없습니다.")
