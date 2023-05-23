import streamlit as st
import time
from urllib.error import URLError

import akshare as ak

st.set_page_config(page_title="股市行情演示", page_icon="📈")

st.markdown("# 行情走势")
st.markdown("沪深A股行情类演示")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

@st.cache_data
def get_A_stocklist():
    return ak.stock_info_a_code_name()

st.write(
    """展示A股的实时行情，网上的信息来源，可能存在一定的延时"""
)

def get_stock_min(stockcode, period='1'):
    return ak.stock_zh_a_hist_min_em(symbol=stockcode, 
                                        period=period, 
                                        adjust="qfq")

try:
    df = get_A_stocklist()
    
    col1, col2 = st.columns([4,1])
    with col1:
        if stocks := st.selectbox("请选择一只股票", list(df.name)):
            stock = df[df.name == stocks].reset_index()
            st.write(f"### 展示 *{stock.name[0]}* 最近交易日的分钟走势行情")
        else:
            st.error("请至少选择一只股票.")
    with col2:
        st.write(' ')
        st.button("刷新")    

    stock_hist = get_stock_min(stock.code[0])[-4*60:]
    stock_hist = stock_hist[stock_hist['开盘'] != 0]
    # st.table(stock_hist)
    
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Candlestick(x=stock_hist['时间'],
                    open=stock_hist['开盘'], high=stock_hist['最高'],
                    low=stock_hist['最低'], close=stock_hist['收盘'])
                         ])

    fig.layout = dict(xaxis=dict(type="category"))
    fig.update_layout(autosize=False,
                        width=800,
                        height=800,)

    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
except URLError as e:
    st.error(
        """
        **需要网络访问实时数据.**
        连接错误信息: %s
    """
        % e.reason
    )