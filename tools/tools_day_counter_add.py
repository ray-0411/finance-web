import streamlit as st
import pandas as pd
from db import connect_sql
from help_fun.time_taipei import t_today

def get_counter(counter_id):
    conn = connect_sql()
    df = pd.read_sql("SELECT * FROM tools_day_counter WHERE id=%s", conn, params=(counter_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None

def add_day_counter(counter_id=0):
    mode = "新增" if counter_id == 0 else "編輯"
    st.title(f"{'➕' if counter_id==0 else '✏️'} {mode} 計日器")

    counter = None
    if counter_id != 0:
        counter = get_counter(counter_id)

    # 表單
    with st.form("counter_form"):
        title = st.text_input("名稱", value=counter["title"] if counter is not None else "")
        target_date = st.date_input(
            "目標日期",
            value=counter["target_date"] if counter is not None else t_today()  # ✅ 用 t_today()
        )
        mode_str = "倒數" if (counter is None or counter["is_countdown"]) else "正數"
        mode = st.radio("模式", ["倒數", "正數"], horizontal=True, index=0 if mode_str=="倒數" else 1)

        submitted = st.form_submit_button("💾 儲存")
        if submitted and title:
            conn = connect_sql()
            cursor = conn.cursor()
            if counter_id == 0:  # ➕ 新增
                cursor.execute("""
                    INSERT INTO tools_day_counter (title, target_date, is_countdown)
                    VALUES (%s, %s, %s)
                """, (title, target_date, mode=="倒數"))
            else:  # ✏️ 更新
                cursor.execute("""
                    UPDATE tools_day_counter
                    SET title=%s, target_date=%s, is_countdown=%s
                    WHERE id=%s
                """, (title, target_date, mode=="倒數", counter_id))
            conn.commit()
            conn.close()

            st.success("✅ 已儲存")
            st.session_state["page"] = "tools_計日器"
            st.rerun()

    if st.button("⬅️ 返回"):
        st.session_state["page"] = "tools_計日器"
        st.rerun()
