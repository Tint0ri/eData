import streamlit as st
import time
from urllib.error import URLError
import akshare as ak
import requests
import pandas as pd

st.set_page_config(page_title="股市行情演示", page_icon="📈")

st.markdown("# 行情走势")
st.markdown("沪深A股行情及公司概况演示")

if st.secrets["showmenu"] != '1':
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                div[data-testid="stToolbar"]{visibility: hidden;}
                div[class^="viewerBadge_link"]{hidden: true;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

@st.cache_data(show_spinner=False, ttl=12*3600)
def get_A_stocklist():
    return ak.stock_info_a_code_name()

def get_stock_min(stockcode, period='1'):
    return ak.stock_zh_a_hist_min_em(symbol=stockcode, 
                                        period=period, 
                                        adjust="qfq")

@st.cache_data(show_spinner=False)
def get_company_info(stockcode):
    url = f"https://wxly.p5w.net/api/data/getcompanysurvey?code={stockcode}" 
    # st.write(url)
    response = requests.get(url)
    return pd.json_normalize(response.json()['obj'])

try:
    df = get_A_stocklist()

    st.write(
        """展示A股的实时行情，网上的信息来源，可能存在一定的延时"""
    )

    col1, col2 = st.columns([4,1])

    with col1:
        if stocks := st.selectbox("请选择一只股票", list(df.name)):
            stock = df[df.name == stocks].reset_index()
        else:
            st.error("请至少选择一只股票.")

    with col2:
        st.write(' ')
        st.button("刷新")    

    tab1, tab2 = st.tabs(["📈 股票行情", "📚 公司背景"])
    css = """
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:1.4rem;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    with tab1:
        st.write(f"### *{stock.name[0]}* 最近交易日的分钟走势行情")

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

    with tab2:
        st.write(f"### 展示 *{stock.name[0]}* 公司概况")

        df = get_company_info(stock.code[0])
        df = df[[   'orgname',
                    'orgjcname',
                    'orgProfile',
                    'englishname',
                    'registeredaddress',
                    'officeaddress',
                    'stocktime',
                    'chairman',
                    'generalmanager',
                    'boardsecretariat',
                    'totalEquity',
                    'category',
                    'mainbusiness',
                    'secretariestelephone',
                    'companyfax',
                    'companywebsite',
                    'mail',
                    'postalcode',
                    'establishmentdate',
                    'modtime',
                    'listingdate',
                    'distribution',
                    'mainunderwriter',
                    'distribution']]
        df.rename(columns={ 'orgname':'公司名称',
                            'orgjcname':'公司简称',
                            'orgProfile':'公司简介',
                            'englishname':'英文名称',
                            'registeredaddress':'注册地址',
                            'officeaddress':'公司地址',
                            'stocktime':'上市时间',
                            'chairman':'法人代表',
                            'generalmanager':'总经理',
                            'boardsecretariat':'董秘',
                            'totalEquity':'注册资本(万元)',
                            'category':'行业种类',
                            'mainbusiness':'主营业务',
                            'secretariestelephone':'公司电话',
                            'companyfax':'公司传真',
                            'companywebsite':'公司网址',
                            'mail':'电子邮件',
                            'postalcode':'邮政编码',
                            'establishmentdate':'成立日期',
                            'modtime':'上市日期',
                            'listingdate':'招股日期',
                            'distribution':'发行方式',
                            'mainunderwriter':'主承销商',
                            'distribution':'发行方式',
                           }, inplace=True)
        style = df.T.style.hide(axis=1)
        style.set_table_styles([dict(selector='th', props='min-width: 100px;'),])
        st.write(style.to_html(), unsafe_allow_html=True)
        # st.dataframe(df.T)

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