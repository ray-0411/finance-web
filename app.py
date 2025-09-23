import streamlit as st

#streamlit run app.py

from main.main_page import main_page

from finance.add_transaction import finance_add_transaction_page
from finance.add_category import finance_add_category_page
from finance.get_transaction import get_transaction_page
from finance.show_category import show_category_page

from work.work_main import work_page
from work.add_event import add_event_page
from work.refresh_work import generate_main_from_events
from work.event_list import show_events_page
from work.work_category import work_categories_page
from work.main_setting import work_main_setting_page

from drink.drink_add import drink_add_page
from drink.drink_category import drink_category_page
from drink.drink_main import drink_main_page
from drink.drink_calendar import drink_calendar_page




# ========== Streamlit UI ==========
st.sidebar.title("📌 選單")

# 👉 在這裡設定初始分頁（方便開發）
DEFAULT_PAGE = "main"
DEFAULT_SIDEBAR = "main"


# 全域變數
if "page" not in st.session_state:
    st.session_state.page = DEFAULT_PAGE
if "user_id" not in st.session_state:
    st.session_state.user_id = 1  
if "sidebar_page" not in st.session_state:
    st.session_state.sidebar_page = DEFAULT_SIDEBAR

# 頁面切換左側欄
if st.session_state.sidebar_page == "main":
    if st.sidebar.button("💰 記帳區塊"):
        st.session_state.sidebar_page = "finance"
        st.session_state.page = "finance_新增交易"
        st.rerun()
    if st.sidebar.button("🛠️ 工作區塊"):
        st.session_state.sidebar_page = "work"
        st.session_state.page = "work_工作區塊"
        st.rerun()
    if st.sidebar.button("🍔 吃飯評價"):
        st.session_state.sidebar_page = "eat"
        st.session_state.page = "eat_查看評價"
        st.rerun()
    if st.sidebar.button("💧 喝水紀錄"):
        st.session_state.sidebar_page = "drink"
        st.session_state.page = "drink_喝水紀錄"
        st.rerun()

elif st.session_state.sidebar_page == "finance":
    if st.sidebar.button("➕ 新增交易"):
        st.session_state.page = "finance_新增交易"
        st.rerun()
    if st.sidebar.button("📊 檢視交易"):
        st.session_state.page = "finance_檢視交易"
        st.rerun()
    if st.sidebar.button("📂 分類總表"):
        st.session_state.page = "finance_分類總表"
        st.rerun()
    if st.sidebar.button("📂 新增分類"):
        st.session_state.page = "finance_新增分類"
        st.rerun()
    if st.sidebar.button("🔙 回主選單"):
        st.session_state.sidebar_page = "main"
        st.rerun()

elif st.session_state.sidebar_page == "work":
    if st.sidebar.button("🛠️ 工作區塊"):
        st.session_state.page = "work_工作區塊"
        generate_main_from_events()
        st.rerun()
    if st.sidebar.button("➕ 新增事件"):
        st.session_state.page = "work_新增事件"
        st.rerun()
    if st.sidebar.button("📅 事件列表"):
        st.session_state.page = "work_事件列表"
        st.rerun()
    if st.sidebar.button("📂 分類管理"):
        st.session_state.page = "work_分類管理"
        st.rerun()
    if st.sidebar.button("🔙 回主選單"):
        st.session_state.sidebar_page = "main"
        st.rerun()

elif st.session_state.sidebar_page == "eat":
    if st.sidebar.button("📊 查看評價"):
        st.session_state.page = "eat_查看評價"
        st.rerun()
    if st.sidebar.button("➕ 新增評價"):
        st.session_state.page = "eat_新增評價"
        st.rerun()
    if st.sidebar.button("➕ 新增店家"):
        st.session_state.page = "eat_新增店家"
        st.rerun()
    if st.sidebar.button("📂 分類管理"):
        st.session_state.page = "eat_分類管理"
        st.rerun()
    if st.sidebar.button("🔙 回主選單"):
        st.session_state.sidebar_page = "main"
        st.rerun()

elif st.session_state.sidebar_page == "drink":
    if st.sidebar.button("📋 飲用紀錄"):
        st.session_state.page = "drink_喝水紀錄"
        st.rerun()
    if st.sidebar.button("💧 新增紀錄"):
        st.session_state.page = "drink_新增紀錄"
        st.rerun()
    if st.sidebar.button("📂 分類管理"):
        st.session_state.page = "drink_分類管理"
        st.rerun()
    if st.sidebar.button("📅 月曆檢視"):
        st.session_state.page = "drink_月曆檢視"
        st.rerun()
    if st.sidebar.button("🔙 回主選單"):
        st.session_state.sidebar_page = "main"
        st.rerun()


# --- 頁面切換 ---
if st.session_state.sidebar_page == "main":
    main_page()
elif st.session_state.sidebar_page == "finance":
    if st.session_state.page == "finance_新增交易":
        finance_add_transaction_page()
    elif st.session_state.page == "finance_檢視交易":
        get_transaction_page()
    elif st.session_state.page == "finance_新增分類":
        finance_add_category_page()
    elif st.session_state.page == "finance_分類總表":
        show_category_page()

elif st.session_state.sidebar_page == "work":
    if st.session_state.page == "work_工作區塊":
        work_page()
    elif st.session_state.page == "work_新增事件":
        add_event_page(0)
    elif st.session_state.page == "work_事件列表":
        show_events_page()
    elif st.session_state.page == "work_分類管理":
        work_categories_page()
    elif st.session_state.page == "work_編輯事件":
        add_event_page(st.session_state.edit_event_id)
    elif st.session_state.page == "work_設定":
        work_main_setting_page()

elif st.session_state.sidebar_page == "eat":
    if st.session_state.page == "eat_查看評價":
        pass
    elif st.session_state.page == "eat_新增評價":
        pass
    elif st.session_state.page == "eat_新增店家":
        pass
    elif st.session_state.page == "eat_分類管理":
        pass
    elif st.session_state.page == "eat_編輯評價":
        pass

elif st.session_state.sidebar_page == "drink":
    if st.session_state.page == "drink_新增紀錄":
        drink_add_page()
    elif st.session_state.page == "drink_分類管理":
        drink_category_page()
    elif st.session_state.page == "drink_喝水紀錄":
        drink_main_page()
    elif st.session_state.page == "drink_月曆檢視":
        drink_calendar_page()