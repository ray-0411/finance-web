import streamlit as st

#streamlit run app.py

from finance.add_transaction import add_transaction_page
from finance.manage_categories import manage_categories_page
from finance.get_transaction import get_transaction_page




# ========== Streamlit UI ==========
st.sidebar.title("📌 選單")

# 👉 在這裡設定初始分頁（方便開發）
DEFAULT_PAGE = "新增交易"

if "page" not in st.session_state:
    st.session_state.page = DEFAULT_PAGE
if "user_id" not in st.session_state:
    st.session_state.user_id = 1  
if "sidebar_page" not in st.session_state:
    st.session_state.sidebar_page = "main"

if st.session_state.sidebar_page == "main":
    if st.sidebar.button("💰 記帳區塊"):
        st.session_state.sidebar_page = "finance"
        st.rerun()
    if st.sidebar.button("🛠️ 工作區塊"):
        st.session_state.sidebar_page = "work"
        st.rerun()
elif st.session_state.sidebar_page == "finance":
    if st.sidebar.button("➕ 新增交易"):
        st.session_state.page = "新增交易"
        st.rerun()
    if st.sidebar.button("📊 檢視交易"):
        st.session_state.page = "檢視交易"
        st.rerun()
    if st.sidebar.button("📂 分類管理"):
        st.session_state.page = "分類管理"
        st.rerun()
    if st.sidebar.button("🔙 回主選單"):
        st.session_state.sidebar_page = "main"
        st.rerun()
elif st.session_state.sidebar_page == "work":
    if st.sidebar.button("🔙 回主選單"):
        st.session_state.sidebar_page = "main"
        st.rerun()

# --- 頁面切換 ---
if st.session_state.sidebar_page == "main":
    #main_page()
    pass
elif st.session_state.sidebar_page == "finance":
    if st.session_state.page == "新增交易":
        add_transaction_page()
    elif st.session_state.page == "檢視交易":
        get_transaction_page()
    elif st.session_state.page == "分類管理":
        manage_categories_page()
elif st.session_state.sidebar_page == "work":
    if st.session_state.page == "工作區塊":
        #work_page()
        pass