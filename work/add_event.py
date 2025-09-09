import streamlit as st
import pandas as pd
from datetime import date
import time

from db import connect_sql 

from work.refresh_work import generate_main_from_events

def add_event_page(event_id = 0):
    
    mode = "新增" if event_id == 0 else "編輯"
    st.title(f"✏️ {mode}事件")
    
    # 讀取分類資料
    conn = connect_sql()
    df_cat = pd.read_sql("SELECT id, name FROM work_category WHERE is_deleted = FALSE ORDER BY id", conn)
    conn.close()

    if event_id != 0:
        conn = connect_sql()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, date, time, category_id, repeat_type, repeat_value, priority, expire, score
            FROM work_events WHERE id = %s
        """, (event_id,))
        event = cursor.fetchone()
        conn.close()

        if not event:
            st.error("❌ 找不到該事件")
            return

        (eid, title, description, event_date, event_time, category_id,
        repeat_type, repeat_value, priority, expire, score) = event
    else:
        # 新增模式 → 預設值
        eid = 0
        title = ""
        description = ""
        event_date = date.today()
        event_time = ""
        category_id = int(df_cat["id"].iloc[0])
        repeat_type = "none"
        repeat_value = 1
        priority = 3
        expire = False
        score = 0

    with st.form("add_event_form"):
        title = st.text_input("事件標題",value=title)
        description = st.text_area("事件描述（選填）",value=description)
        event_date = st.date_input("開始日期", value=event_date)
        event_time = st.text_input("事件時間",value=event_time)

        # 分類選擇
        cat_name_list = df_cat["name"].tolist()
        if category_id in df_cat["id"].values:
            cat_index = int(df_cat.index[df_cat["id"] == category_id].tolist()[0])
        else:
            cat_index = 0
        category_name = st.selectbox("分類", cat_name_list, index=cat_index)
        category_id = int(df_cat.loc[df_cat["name"] == category_name, "id"].iloc[0])

        repeat_type = st.selectbox("重複類型", ["none", "day", "week", "month"], index=["none", "day", "week", "month"].index(repeat_type))
        repeat_value = st.number_input("重複值", min_value=1, step=1, value=repeat_value)

        priority = st.slider("重要度(5重要 1不重要)", 1, 5, priority)
        score = st.number_input("工作分數", min_value=0, step=1, value=score)
        expire_val = st.checkbox("是否過期依舊提醒", value=expire)


        submitted = st.form_submit_button("新增" if eid == 0 else "更新")
        if submitted:
            if title.strip() == "":
                st.error("❌ 標題不能為空")
            else:
                conn = connect_sql()
                cursor = conn.cursor()
                
                if eid == 0:
                    
                    cursor.execute("""
                        INSERT INTO work_events (title, description, date, time, category_id, 
                            repeat_type, repeat_value, priority, expire, score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (title, description, event_date, event_time, category_id, 
                            repeat_type, repeat_value, priority, expire_val, score))
                    st.success(f"✅ 已新增事件：{title}")
                    conn.commit()
                    conn.close()
                    time.sleep(0.5)
                    generate_main_from_events()
                    st.session_state.page = "work_工作區塊"
                    st.rerun()

                else:
                    cursor.execute("""
                        UPDATE work_events
                        SET title = %s, description = %s, date = %s, "time" = %s,
                            category_id = %s, repeat_type = %s, repeat_value = %s,
                            priority = %s, expire = %s, score = %s
                        WHERE id = %s
                    """, (title, description, event_date, event_time,
                        category_id, repeat_type, repeat_value,
                        priority, expire_val, score, eid))
                    st.success(f"✅ 已更新事件：{title}")
                    conn.commit()
                    conn.close()
                    time.sleep(0.5)
                    st.rerun()