import streamlit as st
import time, base64
import urllib 
from urllib.error import URLError
import pandas as pd
import akshare as ak
import requests

st.set_page_config(page_title="公司三方研报演示", page_icon="📊")

st.markdown("# 公司相关研究报告")
st.markdown("沪深A股第三方研报类展示")

if st.secrets["showmenu"] != '1':
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                div[data-testid="stToolbar"]{visibility: hidden;}
                a[class^="viewerBadge"]{visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.write(
    """展示指定A股的相关研究报告，网上的信息来源，可能存在错误"""
)
@st.cache_data(show_spinner=False, ttl=12*3600)
def get_A_stocklist():
    return ak.stock_info_a_code_name()

#function to display the PDF of a given file 
def displayContent(file):
    url = f'https://wxly.p5w.net/api/data/getresearchreport?id={file}'
    content = requests.get(url).json()['obj']

    # Displaying File
    # st.markdown(f"## *{content['s4']}*", unsafe_allow_html=True)
    st.markdown(content['s5'], unsafe_allow_html=True)
    
# https://wxly.p5w.net/api/data/getnoticefulllist?code=000001
# 包含公告链接接
# https://wxly.p5w.net/api/data/getresearchreportlist?code=000001
# 研报链接
@st.cache_data(show_spinner=False, ttl=12*3600)
def get_3rd_report(stockcode, f_date='20220331'):
    url = f"https://wxly.p5w.net/api/data/getresearchreportlist?code={stockcode}" 
    response = requests.get(url)
    return pd.json_normalize(response.json()['rows'])
    # all_stock_report = ak.stock_yjbb_em(date=f_date)
    # return all_stock_report[all_stock_report['股票代码'] == stockcode].reset_index()

try:
    df = get_A_stocklist()
    if stocks := st.selectbox("请选择一只股票", list(df.name)):
        stock = df[df.name == stocks].reset_index()
        st.write(f"### 展示 *{stock.name[0]}* 近期研究报告")
        st.write("*数据来源于全景网*")
    else:
        st.error("请至少选择一只股票.")
    # stock_report = get_stock_report(stock.code[0]).reset_index()
    stock_report = get_3rd_report(stock.code[0])
    
    # st.table(stock_report)

    if report := st.selectbox("请选择一个研报", list(stock_report.s2)):
        displayContent(stock_report[stock_report.s2 == report].reset_index().s1[0])
    else:
        st.error("请选择一份报告.")
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