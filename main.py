import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
import datetime

# 🖥️ 화면을 넓게 쓰기 위한 설정
st.set_page_config(layout="wide") 

# 💾 1. 새로고침(F5) 방어 및 세션 기억 설정
if "code" in st.query_params:
    if "current_stock" not in st.session_state:
        st.session_state.current_stock = st.query_params["code"]
else:
    if "current_stock" not in st.session_state:
        st.session_state.current_stock = ""

if "search_box" not in st.session_state:
    st.session_state.search_box = ""

# 🧹 2. 검색 실행 및 검색창 비우기 함수
def handle_search():
    input_val = st.session_state.search_box.strip()
    if len(input_val) == 6:
        st.session_state.current_stock = input_val
        st.query_params["code"] = input_val  # URL에 코드를 박아서 새로고침해도 유지되게 함
    st.session_state.search_box = ""         # 검색창 텍스트 비우기

st.title("🇰🇷 한국장 10분봉/일봉 타점 검색기")

# 🔍 3. 검색창 (엔터 치면 handle_search 함수 실행)
st.text_input("종목코드(6자리) 입력 후 엔터", key="search_box", on_change=handle_search)

# 🚀 종목명 리스트 캐싱
@st.cache_data
def load_stock_list():
    return fdr.StockListing('KRX')

stock_list = load_stock_list()

# ⚡ 네이버 금융 API 10분봉 데이터 호출
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
            
            try:
                dt = datetime.datetime.strptime(date_str, "%Y%m%d%H%M")
            except:
                dt = date_str
                
            data_list.append({"Date": dt, "Close": close_price})
            
        df = pd.DataFrame(data_list)
        df.set_index("Date", inplace=True)
        return df
    return pd.DataFrame()

# --- 화면 출력부 ---
code = st.session_state.current_stock

if code and len(code) == 6:
    try:
        # 🏢 종목명 찾기
        stock_info = stock_list[stock_list['Code'] == code]
        name = stock_info['Name'].values[0] if not stock_info.empty else "알 수 없는 종목"
        
        # 📊 데이터 호출
        df_daily = fdr.DataReader(code, datetime.date.today() - datetime.timedelta(days=90))
        df_10m = get_10m_data(code)
        
        # ⏰ 실시간 데이터 갱신 시간 가져오기
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 🔄 종목명, 갱신 시간, 최신화 버튼 배치
        col_title, col_btn = st.columns([8, 2])
        with col_title:
            st.subheader(f"🏢 {name} ({code})")
            st.caption(f"⏱️ **마지막 갱신 시간:** {now_time}")  # <--- 이 부분이 추가되었습니다!
        with col_btn:
            if st.button("🔄 현재 종목 최신화"):
                st.rerun()  # 화면 즉시 갱신
                
        price = int(df_daily['Close'].iloc[-1])
        
        # 🎯 타점 계산
        buy = price                     
        target = int(price * 1.03)      
        stop = int(price * 0.98)        
        
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
        st.error("데이터를 불러올 수 없거나 코드가 잘못되었습니다.")
