import streamlit as st

st.set_page_config(
    page_title="说明",
)

if st.secrets["showmenu"] != '1':
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                div[data-testid="stToolbar"]{visibility: hidden;}
                div[class^="viewerBadge_link"]{visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.write("# 这是一个金融信息提供平台的演示")

st.markdown(
    """
    ** 👈 请在左边的侧边栏选择 ** 想要查询的信息

    ### 信息内容
    - 沪深A股的行情信息
    - 股票的公告信息
    - 股票的研究报告

    ### 说明
    - 信息采集自网上，不保障实时性和准确性
    - 仅作为非常初步的功能展示，存在bug和不完善请多包涵
"""
)



