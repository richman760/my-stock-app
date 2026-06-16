import streamlit as st
import finance_datareader as fdr
import pandas as pd
import requests
import datetime

# 🖥️ 화면을 넓게 쓰기 위한 설정 (반드시 맨 윗줄에 있어야 함)
st.set_page_config(layout="wide") 

st.title("🇰🇷 한국장 10분봉/일봉 타점 검색기")

# 1. 🚀 종목명 리스트 미리 불러오기 (서버 속도를 위해 캐싱)
@st.cache_data
def load_stock_list():
    return fdr.StockListing('KRX')

stock_list = load_stock_list()

# 2. ⚡ 네이버 금융 API로 10분봉 데이터 가져오는 함수 (에러 없는 안전한 방식)
def get_10m_data(code):
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={code}&timeframe=minute10&count=150&requestType=0"
    res = requests.get(url)
    items = res.text.split('<item data="')
    
    data_list = []
    if len(items) > 1:
        for item in items[1:]:
            row = item.split('"')[0].split('|')
            date_str = row[0]
            close_price = int(row[4])
            
            # 날짜 형식 변환
            try:
                dt = datetime.datetime.strptime(date_str, "%Y%m%d%H%M")
            except:
                dt = date_str
                
            data_list.append({"Date": dt, "Close": close_price})
            
        df = pd.DataFrame(data_list)
        df.set_index("Date", inplace=True)
        return df
    return pd.DataFrame()

# --- 메인 화면 시작 ---
code = st.text_input("종목코드(6자리) 입력", max_chars=6)

if code and len(code) == 6:
    try:
        # 🏢 종목명 찾기
        stock_info = stock_list[stock_list['Code'] == code]
        name = stock_info['Name'].values[0] if not stock_info.empty else "알 수 없는 종목"
        
        # 입력창 바로 아래에 종목명 표시
        st.subheader(f"🏢 {name} ({code})")

        # 📊 데이터 호출 (일봉은 최근 3개월, 10분봉은 최근 흐름)
        df_daily = fdr.DataReader(code, datetime.date.today() - datetime.timedelta(days=90))
        df_10m = get_10m_data(code)
        
        price = int(df_daily['Close'].iloc[-1])
        
        # 🎯 타점 계산 (형의 상식에 맞게 재설정)
        buy = price                     # 매수가
        target = int(price * 1.03)      # 목표가 (+3%)
        stop = int(price * 0.98)        # 손절가 (-2%)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("현재가", f"{price:,}원")
        c2.success(f"🎯 목표: {target:,}원")
        c3.info(f"✅ 매수: {buy:,}원")
        c4.error(f"🛡️ 손절: {stop:,}원")
        
        st.markdown("---")
        
        # 📉 차트 2분할 비교 (10분봉 / 일봉)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### ⏱️ 10분봉 차트 (최근 흐름)")
            if not df_10m.empty:
                st.line_chart(df_10m['Close'])
            else:
                st.warning("10분봉 데이터를 불러올 수 없습니다.")
                
        with col2:
            st.markdown("##### 📅 일봉 차트 (최근 3개월)")
            if not df_daily.empty:
                st.line_chart(df_daily['Close'])
                
    except Exception as e:
        st.error(f"데이터를 불러올 수 없거나 코드가 잘못되었습니다.")
