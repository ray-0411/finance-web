import streamlit as st

#streamlit run app.py

from add_transaction import add_transaction_page
from manage_categories import manage_categories_page
from get_transaction import get_transaction_page




# ========== Streamlit UI ==========
st.sidebar.title("📌 選單")

# 👉 在這裡設定初始分頁（方便開發）
DEFAULT_PAGE = "新增交易"

if "page" not in st.session_state:
    st.session_state.page = DEFAULT_PAGE
if "user_id" not in st.session_state:
    st.session_state.user_id = 1  
###

if st.sidebar.button("➕ 新增交易"):
    st.session_state.page = "新增交易"
if st.sidebar.button("📊 檢視交易"):
    st.session_state.page = "檢視交易"
if st.sidebar.button("📂 分類管理"):
    st.session_state.page = "分類管理"

# --- 頁面切換 ---
if st.session_state.page == "新增交易":
    add_transaction_page()
elif st.session_state.page == "檢視交易":
    get_transaction_page()
elif st.session_state.page == "分類管理":
    manage_categories_page()
