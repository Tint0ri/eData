import streamlit as st
import time, base64, os
import urllib
from urllib.error import URLError
import pandas as pd
import akshare as ak
import streamlit_js_eval
import fitz

st.set_page_config(page_title="公司公告演示", page_icon="🌍")

st.markdown("# 公司财报")
st.markdown("沪深A股公告类展示")

            # div[data-testid="stToolbar"]{visibility: hidden;}
            # div[class^="viewerBadge_link"]{hidden: true;}

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.write(
    """
    展示指定A股的相关公告，网上的信息来源，可能存在错误
    """
)

user_agent = streamlit_js_eval.get_user_agent()
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

while user_agent is None:
    pass
bMoile = 'Android' in user_agent or 'iOS' in user_agent
# st.write(user_agent)

@st.cache_data(show_spinner=False, ttl=12*3600)
def get_A_stocklist():
    return ak.stock_info_a_code_name()

#function to display the PDF of a given file 
@st.cache_data(show_spinner=False)
def PDF2images(url_file):
    progressbar = st.progress(0.0, text='准备')
    st.session_state.page_number = 0
    root_report = os.path.join('report')
    if not os.path.exists(root_report):
        os.mkdir(root_report)

    images = []
    progressbar.progress(0.1, text='查询财报')
    filename = url_file.split('/')[-1]
    if filename.split('.')[-1].lower() != 'pdf':
        st.write("目前只处理PDF类型的文件")
        st.write("当前文件名为：", filename)
        return images

    progressbar.progress(0.3, text='获取详细财报文档')
    filepath = os.path.join(root_report, filename)
    if not os.path.exists(filepath):
        with urllib.request.urlopen(url_file) as f:
            with open(filepath, 'wb') as code:
                code.write(f.read())

    progressbar.progress(0.6, text='处理财报')
    with fitz.open(filepath) as f:
        images.extend(page.get_pixmap().tobytes() for page in f)

    progressbar.progress(1.0, text='财报处理完成！')
    time.sleep(1)
    progressbar.empty()

    return images

def displayPDF(file):
#     # Opening file from file path. this is used to open the file from a website rather than local
#     # Embedding PDF in HTML
#     file.replace("http://","https://")
#     if bMoile:
#         pdf_display = F'<object data="{file}" width="100%" height="950" type="application/pdf" aria-labelledby="PDF document"><p>浏览器不支持嵌入查看PDF。<a href="{file}">下载研报</a></p></object>'
#     else:
#         with urllib.request.urlopen(file) as f:
#             if int(f.headers['content-length']) < 2 * 1024 * 1024:
#                 base64_pdf = base64.b64encode(f.read()).decode('utf-8')
#                 pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'
#             else:
#                 st.write("📨文件过大，无法嵌入PDF，需要下载查看")
#                 pdf_display = F'<object data="{file}" width="700" height="950" type="application/pdf" aria-labelledby="PDF document"><p>浏览器不支持嵌入查看这个PDF。<a href="{file}">下载研报</a></p></object>'

#     # use google preview is the perfect way 😒
#     # pdf_display = F'<embed src="https://drive.google.com/viewerng/viewer?embedded=true&url={file}" width="100%" height="950">'
#     # Displaying File
#     st.markdown(pdf_display, unsafe_allow_html=True)
    images = PDF2images(file)
    if lastpage := (len(images) - 1):
        prev, _, next = st.columns([1, 3, 1])
        if next.button("下一页 ⏭️"):
            if st.session_state.page_number + 1 > lastpage:
                st.session_state.page_number = 0
            else:
                st.session_state.page_number += 1
        if prev.button("⏮️ 上一页"):
            if st.session_state.page_number < 1:
                st.session_state.page_number = lastpage
            else:
                st.session_state.page_number -= 1

        st.image(images[st.session_state.page_number], use_column_width=True)

# https://wxly.p5w.net/api/data/getnoticefulllist?code=000001
# 包含公告链接接
#https://wxly.p5w.net/api/data/getresearchreportlist?code=000001
# 研报链接
@st.cache_data(show_spinner=False)
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