import streamlit as st
import pandas as pd
from db import connect_sql

def show_category_page():
    st.title("📂 財務分類總表")

    conn = connect_sql()
    df = pd.read_sql("""
        SELECT 
            c.id,
            c.name,
            c.sort_order,
            p.name AS parent_name,
            gp.name AS grand_name,
            c.is_deleted,
            c.type
        FROM finance_category c
        LEFT JOIN finance_category p  ON c.parent_id = p.id
        LEFT JOIN finance_category gp ON p.parent_id = gp.id
        WHERE c.is_deleted = FALSE
        ORDER BY COALESCE(gp.sort_order, p.sort_order, c.sort_order), c.sort_order, c.id;
    """, conn)
    conn.close()

    if df.empty:
        st.info("目前沒有分類")
        return

    # 組合階層名稱
    def build_path(row):
        parts = []
        if pd.notna(row["grand_name"]):
            parts.append(row["grand_name"])
        if pd.notna(row["parent_name"]):
            parts.append(row["parent_name"])
        parts.append(row["name"])
        return " / ".join(parts)

    df["分類路徑"] = df.apply(build_path, axis=1)

    df_show = df[["id", "分類路徑", "sort_order", "type"]].rename(columns={
        "id": "ID",
        "sort_order": "排序",
        "type": "類型"
    })

    st.dataframe(df_show, use_container_width=True)
