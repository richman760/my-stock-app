import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import requests
import datetime
import numpy as np

st.set_page_config(layout="wide") 

# 💾 새로고침 방어
if "code" in st.query_params:
    if "current_stock" not in st.session_state:
        st.session_state.current_stock = st.query_params["code"]
else:
    if "current_stock" not in st.session_state:
        st.session_state.current_stock = ""

if "search_box" not in st.session_state:
    st.session_state.search_box = ""

def handle_search():
    input_val = st.session_state.search_box.strip()
    if len(input_val) == 6:
        st.session_state.current_stock = input_val
        st.query_params["code"] = input_val 
    st.session_state.search_box = ""

st.title("🇰🇷 한국장 실전 타점 분석기 (10분봉 vs 일봉)")

# 🔍 검색창
st.text_input("종목코드(6자리) 입력 후 엔터", key="search_box", on_change=handle_search)

@st.cache_data
def load_stock_list():
    return fdr.StockListing('KRX')

stock_list = load_stock_list()

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
        
        # 10분봉 볼린저 밴드
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['STD'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['MA20'] + (df['STD'] * 2)
        df['BB_Lower'] = df['MA20'] - (df['STD'] * 2)
        return df.dropna()
    return pd.DataFrame()

# --- 화면 출력부 ---
code = st.session_state.current_stock

if code and len(code) == 6:
    try:
        stock_info = stock_list[stock_list['Code'] == code]
        name = stock_info['Name'].values[0] if not stock_info.empty else "알 수 없는 종목"
        
        df_daily = fdr.DataReader(code, datetime.date.today() - datetime.timedelta(days=120))
        df_10m = get_10m_data(code)
        
        # 일봉 볼린저 밴드 계산 (종가 홀딩 가치 판단용)
        df_daily['MA20'] = df_daily['Close'].rolling(window=20).mean()
        df_daily['STD'] = df_daily['Close'].rolling(window=20).std()
        df_daily['BB_Upper'] = df_daily['MA20'] + (df_daily['STD'] * 2)
        df_daily['BB_Lower'] = df_daily['MA20'] - (df_daily['STD'] * 2)
        df_daily = df_daily.dropna()
        
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        col_title, col_btn = st.columns([8, 2])
        with col_title:
            st.subheader(f"🏢 {name} ({code})")
            st.caption(f"⏱️ **마지막 갱신 시간:** {now_time}")
        with col_btn:
            if st.button("🔄 현재 종목 최신화"):
                st.rerun()
                
        # 📊 지표 값 추출
        current_price = int(df_10m['Close'].iloc[-1])
        
        m10_ma20 = int(df_10m['MA20'].iloc[-1])
        m10_upper = int(df_10m['BB_Upper'].iloc[-1])
        m10_lower = int(df_10m['BB_Lower'].iloc[-1])
        
        d_ma20 = int(df_daily['MA20'].iloc[-1])
        d_upper = int(df_daily['BB_Upper'].iloc[-1])
        d_lower = int(df_daily['BB_Lower'].iloc[-1])
        
        # 🧠 1. 단기 타점 분석 (10분봉 기준)
        is_short_good = current_price <= m10_ma20  # 단기적으로 눌림목인가?
        short_buy = current_price if current_price <= m10_lower else m10_lower
        short_target = m10_ma20 if current_price < m10_lower else m10_upper
        
        # 🧠 2. 장기 타점 분석 (일봉 기준 - 종가 홀딩용)
        is_long_good = current_price >= d_ma20  # 일봉 추세가 20일선 위로 살아있는가?
        long_target = d_upper
        long_stop = d_ma20
        
        # 🤖 3. 종합 판단 (크로스 체크)
        if is_short_good and is_long_good:
            status_msg = "🔥 [최상] 단기 눌림목 + 일봉 상승장. 진입 후 종가 오버나잇도 좋습니다!"
        elif is_short_good and not is_long_good:
            status_msg = "⚠️ [주의] 단기 반등 자리이나 일봉 역배열. 짧게 10분봉 수익만 먹고 종가 전 매도 추천!"
        elif not is_short_good and is_long_good:
            status_msg = "⏳ [대기] 일봉 추세는 좋으나 현재 단기 고점. 10분봉이 20선 아래로 눌릴 때까지 관망하세요."
        else:
            status_msg = "❄️ [위험] 단기 고점 + 일봉 하락장. 절대 진입 금지!"
            
        st.markdown(f"### 🤖 AI 종합 판단: **{status_msg}**")
        
        # 타점 비교 UI
        st.markdown("---")
        col_s, col_l = st.columns(2)
        
        with col_s:
            st.info("⏱️ **[단기] 10분봉 기준 타점 (빠른 치고 빠지기)**")
            st.write(f"- 🟢 **베스트 진입가:** {int(short_buy):,}원")
            st.write(f"- 🎯 **단기 목표가:** {int(short_target):,}원")
            st.write(f"- 🛡️ **단기 손절가:** {int(short_buy * 0.98):,}원 (-2%)")
            
        with col_l:
            st.success("📅 **[스윙] 일봉 기준 타점 (종가 홀딩 여부 판별)**")
            trend_str = "상승 추세 📈" if is_long_good else "하락 역배열 📉"
            st.write(f"- 📊 **현재 일봉 추세:** {trend_str}")
            st.write(f"- 🎯 **일봉 최종 목표가:** {int(long_target):,}원 (상단 밴드)")
            st.write(f"- 🛡️ **종가 기준 손절선:** {int(long_stop):,}원 (일봉 20선)")

        st.markdown("---")
        
        # 차트 비교 (볼린저 밴드 포함)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### ⏱️ 10분봉 차트 (단기 흐름)")
            st.line_chart(df_10m[['Close', 'MA20', 'BB_Upper', 'BB_Lower']])
                
        with col2:
            st.markdown("##### 📅 일봉 차트 (장기 추세)")
            st.line_chart(df_daily[['Close', 'MA20', 'BB_Upper', 'BB_Lower']])
                
    except Exception as e:
        st.error("분석 중 오류가 발생했습니다. 신규 상장주이거나 데이터가 부족할 수 있습니다.")
