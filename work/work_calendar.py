import streamlit as st
import pandas as pd
from db import connect_sql
from help_fun.time_taipei import t_today
from streamlit_calendar import calendar

priority_colors = {
    5: "red",
    4: "orange",
    3: "black",
    2: "green",
    1: "blue"
}

def get_tasks():
    conn = connect_sql()
    df = pd.read_sql("""
        SELECT m.id, m.event_id, e.title, e.time, e.expire, e.priority, 
               m.occur_date, m.is_completed, c.name AS category_name, e.score, e.description
        FROM work_main m
        JOIN work_events e ON m.event_id = e.id
        JOIN work_category c ON e.category_id = c.id
        WHERE m.is_stop = FALSE
        ORDER BY m.occur_date ASC, m.is_completed ASC, e.priority DESC
    """, conn)
    conn.close()
    return df

def work_calendar_page():
    st.title("📆 月曆檢視")

    tasks = get_tasks()
    if tasks.empty:
        st.info("目前沒有事件")
        return

    today = pd.to_datetime(t_today())

    events = []
    for _, row in tasks.iterrows():
        # 顯示標題
        title = row["title"]
        if row["time"]:
            title = f"{row['time']} {title}"
        if row["score"] and row["score"] > 0:
            title += f" ({row['score']})"
        if row["description"] and row["description"].strip() != "":
            title += " 📝"


        # 顏色
        if row["is_completed"]:
            color = "gray"
        elif row["expire"] and not row["is_completed"] and pd.to_datetime(row["occur_date"]) < today:
            color = "violet"
        else:
            color = priority_colors.get(row["priority"], "black")

        events.append({
            "title": title,
            "start": str(row["occur_date"]),
            "allDay": True,
            "color": color,
            "extendedProps": {
                "category": row["category_name"],
                "completed": bool(row["is_completed"]),
                "event_id": row["event_id"]
            }
        })

    calendar_value = calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "locale": "zh-tw",
            "height": "auto",
            "firstDay": 1,  
        },
        key="work_calendar"
    )


    # 點擊事件後顯示細節
    if calendar_value:
        if calendar_value.get("callback") == "eventClick":
            e = calendar_value["eventClick"]["event"]  # 👈 注意這裡
            st.subheader(f"📅 {e['start']} - {e['title']}")

            # 如果 extendedProps 有帶更多資訊
            props = e.get("extendedProps", {})
            st.markdown(f"""
            - 📂 類別：**{props.get('category', '—')}**
            - ✅ 已完成：**{props.get('completed', False)}**
            """)
            
            # 編輯按鈕
            if st.button("✏️ 編輯事件"):
                st.session_state["page"] = "work_編輯事件"
                st.session_state["edit_event_id"] = props.get("event_id")
                st.rerun()

