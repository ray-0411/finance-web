import streamlit as st
import pandas as pd
from db import connect_sql
from help_fun.time_taipei import t_today
from tools.tools_day_counter_add import add_day_counter

def get_day_counters():
    conn = connect_sql()
    df = pd.read_sql("SELECT * FROM tools_day_counter ORDER BY target_date ASC", conn)
    conn.close()
    return df

def delete_day_counter(counter_id):
    conn = connect_sql()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tools_day_counter WHERE id = %s", (counter_id,))
    conn.commit()
    conn.close()

def day_counter_main_page():
    st.title("⏳ 計日器")

    # ➕ 新增計日器
    if st.button("➕ 新增計日器"):
        st.session_state["page"] = "tools_新增計日器"
        st.session_state["counter_id"] = 0  # 新增模式
        st.rerun()

    st.divider()

    # 📋 顯示所有計日器
    df = get_day_counters()
    today = pd.to_datetime(t_today()).date()

    if df.empty:
        st.info("目前沒有計日器")
        return

    for _, row in df.iterrows():
        # 計算天數
        days = (row["target_date"] - today).days
        if row["is_countdown"]:
            text = f"還有 {days} 天" if days >= 0 else f"已過 {abs(days)} 天"
        else:
            text = f"已過 {abs(days)} 天" if days <= 0 else f"還有 {days} 天"

        # 顯示區塊
        col1, col2, col3, col4 = st.columns([0.2,0.5, 0.15, 0.15])
        with col1:
            st.markdown(f"#### {text}")
        with col2:
            st.markdown(f"#### {row['title']}")
        with col3:
            if st.button("✏️ 編輯", key=f"edit_{row['id']}"):
                st.session_state["page"] = "tools_新增計日器"
                st.session_state["counter_id"] = row["id"]
                st.rerun()
        with col4:
            if st.button("🗑️ 刪除", key=f"del_{row['id']}"):
                delete_day_counter(row["id"])
                st.rerun()
