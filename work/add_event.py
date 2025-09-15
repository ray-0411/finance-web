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
    df_cat = pd.read_sql("SELECT id, name, parent_id FROM work_category WHERE is_deleted = FALSE ORDER BY id", conn)
    conn.close()

    if event_id != 0:
        conn = connect_sql()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, date, time, category_id, repeat_type, 
                repeat_value, priority, expire, score
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


    title = st.text_input("事件標題",value=title)
    description = st.text_area("事件描述（選填）",value=description)
    event_date = st.date_input("開始日期", value=event_date)
    event_time = st.text_input("事件時間",value=event_time)


    # 先找父分類（parent_id 為 NULL 的）
    parent_options = df_cat[df_cat["parent_id"].isna()]

    # 預設父分類
    if category_id in parent_options["id"].values:
        parent_index = int(parent_options.index[parent_options["id"] == category_id].tolist()[0])
    else:
        # 如果 category_id 是子分類，就找到它的父分類
        if category_id in df_cat["id"].values:
            parent_id = int(df_cat.loc[df_cat["id"] == category_id, "parent_id"].iloc[0])
            parent_index = int(parent_options.index[parent_options["id"] == parent_id].tolist()[0])
        else:
            parent_index = 0

    parent_name = st.selectbox("父分類", parent_options["name"].tolist(), index=parent_index)
    parent_id = int(parent_options.loc[parent_options["name"] == parent_name, "id"].iloc[0])

    # 再選子分類（parent_id = 父分類 id）
    child_options = df_cat[df_cat["parent_id"] == parent_id].copy()

    # ➕ 在最前面加上一個「(無)」選項
    child_options = pd.concat([
        pd.DataFrame([{"id": parent_id, "name": "(無)"}]), 
        child_options
    ], ignore_index=True)

    # 判斷預設 index
    if category_id in child_options["id"].values:
        child_index = int(child_options.index[child_options["id"] == category_id].tolist()[0])
    else:
        child_index = 0

    child_name = st.selectbox("子分類", child_options["name"].tolist(), index=child_index)

    # 取選中的 id
    category_id = int(child_options.loc[child_options["name"] == child_name, "id"].iloc[0])
    
    

    repeat_type = st.selectbox("重複類型", ["none", "day", "week", "month"], index=["none", "day", "week", "month"].index(repeat_type))
    repeat_value = st.number_input("重複值", min_value=1, step=1, value=repeat_value)

    priority = st.slider("重要度(5重要 1不重要)", 1, 5, priority)
    score = st.number_input("工作分數", min_value=0, step=1, value=score)
    expire_val = st.checkbox("是否過期依舊提醒", value=expire)


    
    if st.button("✅ " + ("新增" if eid == 0 else "更新")):
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
                generate_main_from_events()
                st.session_state.page = "work_工作區塊"
                st.rerun()