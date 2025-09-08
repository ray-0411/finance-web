import streamlit as st
import pandas as pd

from db import connect_sql_work 

priority_colors = {
    5: "red",
    4: "orange",
    3: "black",
    2: "green",
    1: "blue"
}

def get_tasks():
    conn = connect_sql_work()
    df = pd.read_sql("""
        SELECT m.id, m.event_id, e.title, e.time, e.expire, e.priority, m.occur_date, m.is_completed, c.name AS category_name
        FROM main m
        JOIN events e ON m.event_id = e.id
        JOIN category c ON e.category_id = c.id
        WHERE m.is_stop = FALSE
            AND NOT (m.occur_date < CURRENT_DATE AND e.expire = TRUE AND m.is_completed = TRUE)
            AND NOT (m.occur_date < CURRENT_DATE AND e.expire = FALSE)
        ORDER BY m.occur_date ASC, e.priority DESC
    """, conn)
    conn.close()
    return df

def update_task_status(task_id, status):
    conn = connect_sql_work()
    cursor = conn.cursor()
    cursor.execute("UPDATE main SET is_completed = %s WHERE id = %s", (status, task_id))
    conn.commit()
    conn.close()

def work_page():
    st.markdown(
        """
        <style>
        /* 控制每一列 row 高度一致 */
        div[data-testid="stHorizontalBlock"] {
            align-items: center;   /* ⭐ 垂直置中 */
        }
        /* 控制 checkbox 放大 & 垂直對齊 */
        div[data-testid="stCheckbox"] label {
            display: flex;
            align-items: center;
        }
        div[data-testid="stCheckbox"] input[type="checkbox"] {
            transform: scale(1.5);
            margin-right: 6px;
        }
        /* 控制按鈕大小和垂直對齊 */
        div[data-testid="stButton"] button {
            height: 40px;
            margin: auto;
            display: flex;
            align-items: center;
            justify-content: center;
            transform: translateY(8px);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    
    st.title("📋 待辦事項")

    tasks = get_tasks()
    if tasks.empty:
        st.info("目前沒有事件")
        return

    grouped = tasks.groupby("occur_date")

    for occur_date, group in grouped:
        
        # 日期字串處理
        dt = pd.to_datetime(occur_date)
        weekday_map = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]
        date_str = dt.strftime("%Y/%m/%d")
        weekday_str = weekday_map[dt.weekday()]  # weekday(): 0=星期一, 6=星期日

        # 顯示
        st.markdown(f"### {date_str} {weekday_str}")

        for _, row in group.iterrows():
            # 顯示文字
            if row['time']:
                text = row['time'] + "&nbsp;&nbsp;" + row['title']
            else:
                text = row['title']

            color = priority_colors.get(row['priority'], "black")
            
            if row['is_completed']:
                text_html = f"<span style='color:{color}; font-size:24px'><s>{text}</s></span>"
            else:
                text_html = f"<span style='color:{color}; font-size:24px'>{text}</span>"

            col1, col2, col3, col4 = st.columns([0.05, 0.65, 0.2, 0.1])

            with col1:
                checked = st.checkbox("", value=bool(row['is_completed']), key=f"task_{row['id']}")

            with col2:
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; height:100%; font-size:24px; color:{color};">
                        {'<s>' + text + '</s>' if row['is_completed'] else text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"<div style='font-size:18px; font-weight:bold; text-align:center;'>📂 {row['category_name']}</div>",
                    unsafe_allow_html=True
                )
            
            with col4:
                if st.button("✏️", key=f"edit_{row['id']}"):
                    st.session_state["page"] = "編輯事件"
                    st.session_state["edit_event_id"] = row["event_id"]
                    st.rerun()

            if checked != bool(row['is_completed']):
                update_task_status(row['id'], checked)
                st.rerun()