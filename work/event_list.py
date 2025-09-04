import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import time

from db import connect_sql_work


def get_events():
    conn = connect_sql_work()
    df = pd.read_sql("SELECT * FROM events ORDER BY date ASC", conn)
    conn.close()
    return df

def show_events_page():
    st.title("📅 事件列表")

    today = date.today()
    df = get_events()

    if df.empty:
        st.info("目前沒有任何事件")
        return

    # 區分「有效事件」和「過期/刪除事件」
    active_events = df[(df["stop"] == False) & (pd.to_datetime(df["date"]) >= pd.to_datetime(today))]
    expired_or_deleted = df[(df["stop"] == True) | (pd.to_datetime(df["date"]) < pd.to_datetime(today))]

    # 顯示有效事件
    st.subheader("✅ 有效事件")
    if active_events.empty:
        st.write("（沒有有效事件）")
    else:
        st.dataframe(active_events, use_container_width=True)

    # 顯示過期/停用事件
    st.subheader("🗑️ 過期或停用事件")
    if expired_or_deleted.empty:
        st.write("（沒有過期或停用事件）")
    else:
        st.dataframe(expired_or_deleted, use_container_width=True)

    st.subheader("🗑️ 停用事件")

    conn = connect_sql_work()
    df_events = pd.read_sql("SELECT id, title, date FROM events WHERE stop = FALSE ORDER BY date ASC", conn)
    conn.close()

    if "delete_event_mode" not in st.session_state:
        st.session_state.delete_event_mode = False
        st.session_state.delete_event_target = None

    if not df_events.empty:
        selected_event = st.selectbox(
            "請選擇要停用的事件",
            ["None"] + df_events.apply(lambda row: f"[{row['id']}] {row['title']} ({row['date']})", axis=1).tolist()
        )

        if selected_event != "None" and st.button(f"停用 {selected_event}"):
            st.session_state.delete_event_target = selected_event

        if st.session_state.delete_event_target is not None:
                st.warning(f"⚠️ 確定要停用 {st.session_state.delete_event_target} 嗎？")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 確定停用"):
                        delete_id = int(st.session_state.delete_event_target.split("]")[0][1:])
                        conn = connect_sql_work()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE events SET stop = TRUE WHERE id = %s", (delete_id,))
                        conn.commit()
                        conn.close()
                        st.success(f"🗑️ 已停用事件 ID {delete_id}")
                        st.session_state.delete_event_target = None
                        st.rerun()

                with col2:
                    if st.button("❌ 取消"):
                        st.session_state.delete_event_target = None
                        st.info("已取消停用")
                        time.sleep(0.5)
                        st.rerun()
    else:
        st.info("目前沒有任何事件可停用")

    st.subheader("🗑️ 刪除事件")

    conn = connect_sql_work()
    # 把所有事件都拿出來（包含停用的）
    df_events = pd.read_sql("SELECT id, title, date, stop FROM events ORDER BY date ASC", conn)
    conn.close()

    if "remove_event_target" not in st.session_state:
        st.session_state.remove_event_target = None

    if not df_events.empty:
        selected_event = st.selectbox(
            "請選擇要刪除的事件",
            ["None"] + df_events.apply(
                lambda row: f"[{row['id']}] {row['title']} ({row['date']})" + (" ✅已停用" if row['stop'] == 1 else ""),
                axis=1
            ).tolist()
        )

        if selected_event != "None" and st.button(f"刪除 {selected_event}"):
            st.session_state.remove_event_target = selected_event

        if st.session_state.remove_event_target is not None:
            st.warning(f"⚠️ 確定要刪除 {st.session_state.remove_event_target} 嗎？（此動作無法復原）")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 確定刪除"):
                    delete_id = int(st.session_state.remove_event_target.split("]")[0][1:])
                    conn = connect_sql_work()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM events WHERE id = %s", (delete_id,))
                    conn.commit()
                    conn.close()
                    st.success(f"🗑️ 已刪除事件 ID {delete_id}")
                    st.session_state.remove_event_target = None
                    st.rerun()

            with col2:
                if st.button("❌ 取消刪除"):
                    st.session_state.remove_event_target = None
                    st.info("已取消刪除")
                    time.sleep(0.5)
                    st.rerun()
