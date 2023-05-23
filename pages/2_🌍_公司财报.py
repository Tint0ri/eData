import streamlit as st
import time, base64
import urllib
from urllib.error import URLError
import pandas as pd
import akshare as ak
import streamlit_js_eval

st.set_page_config(page_title="公司公告演示", page_icon="🌍")

st.markdown("# 公司财报")
st.markdown("沪深A股公告类展示")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            div[data-testid="stToolbar"]{visibility: hidden;}
            div[class^="viewerBadge_link"]{visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.write(
    """
    展示指定A股的相关公告，网上的信息来源，可能存在错误
    * 嵌入查看PDF文件功能目前暂时只支持2M以内文件大小的PDF *
    """
)

user_agent = streamlit_js_eval.get_user_agent()
while user_agent is None:
    pass
bMoile = 'Android' in user_agent or 'iOS' in user_agent
# st.write(user_agent)

@st.cache_data
def get_A_stocklist():
    return ak.stock_info_a_code_name()

#function to display the PDF of a given file 
def displayPDF(file):
    # Opening file from file path. this is used to open the file from a website rather than local
    # Embedding PDF in HTML
    if bMoile:
        pdf_display = F'<object data="{file}" width="100%" height="950" type="application/pdf" aria-labelledby="PDF document"><p>浏览器不支持嵌入查看PDF。<a href="{file}">下载研报</a></p></object>'
    else:
        with urllib.request.urlopen(file) as f:
            if int(f.headers['content-length']) < 2 * 1024 * 1024:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'
            else:
                st.write("📨文件过大，无法嵌入PDF，需要下载查看")
                pdf_display = F'<object data="{file}" width="700" height="950" type="application/pdf" aria-labelledby="PDF document"><p>浏览器不支持嵌入查看这个PDF。<a href="{file}">下载研报</a></p></object>'
    
    # use google preview is the perfect way 😒
    # pdf_display = F'<embed src="https://drive.google.com/viewerng/viewer?embedded=true&url={file}" width="100%" height="950">'
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)
    
# https://wxly.p5w.net/api/data/getnoticefulllist?code=000001
# 包含公告链接接
#https://wxly.p5w.net/api/data/getresearchreportlist?code=000001
# 研报链接
@st.cache_data
def get_stock_report(stockcode, f_date='20220331'):
    import requests

    url = f"https://wxly.p5w.net/api/data/getnoticefulllist?code={stockcode}" 
    response = requests.get(url)
    return pd.json_normalize(response.json()['rows'])
    # all_stock_report = ak.stock_yjbb_em(date=f_date)
    # return all_stock_report[all_stock_report['股票代码'] == stockcode].reset_index()

try:
    df = get_A_stocklist()
    if stocks := st.selectbox("请选择一只股票", list(df.name)):
        stock = df[df.name == stocks].reset_index()
        st.write(f"### 展示 *{stock.name[0]}* 最新业绩报告")
        st.write("*数据来源于全景网*")
    else:
        st.error("请至少选择一只股票.")
    # stock_report = get_stock_report(stock.code[0]).reset_index()
    stock_report = get_stock_report(stock.code[0])
    
    # st.table(stock_report)

    if report := st.selectbox("请选择一个报告", list(stock_report.title)):
        displayPDF(stock_report[stock_report.title == report].reset_index().url[0])
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