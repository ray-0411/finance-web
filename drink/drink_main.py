import streamlit as st
import pandas as pd
import datetime
from db import connect_sql

def drink_insert_page():
    st.title("🥤 新增飲用紀錄")

    # 讀取未刪除的分類
    conn = connect_sql()
    cat_df = pd.read_sql("""
        SELECT id, name, parent_id, weight, is_deleted
        FROM drink_category
        WHERE is_deleted = FALSE
        ORDER BY id
    """, conn)
    conn.close()

    if cat_df.empty:
        st.info("目前沒有可用的分類，請先到『分類管理』新增。")
        return

    # ===== 工具：找某分類的根節點名稱（water 或 drink） =====
    parent_map = {int(r.id): r.parent_id for _, r in cat_df.iterrows()}
    name_map   = {int(r.id): r.name      for _, r in cat_df.iterrows()}

    def get_root_name(cat_id: int) -> str:
        cur = cat_id
        # 一直往上找 parent，直到 parent_id 為空
        while pd.notna(parent_map.get(cur)):
            cur = int(parent_map[cur])
        return name_map.get(cur, "")

    # 葉節點 = 沒有被任何人當作 parent_id 的分類
    non_leaf_parent_ids = set(int(x) for x in cat_df["parent_id"].dropna().unique())
    leaf_df = cat_df[~cat_df["id"].isin(non_leaf_parent_ids)].copy()

    # 依 root_name 分群，之後可用 type 過濾
    leaf_df["root_name"] = leaf_df["id"].apply(lambda cid: get_root_name(int(cid)))

    with st.form("add_drink_form", clear_on_submit=True):
        # 1) 基本欄位
        drink_date = st.date_input("日期", datetime.date.today())
        drink_time = st.time_input("時間", datetime.datetime.now().time())
        amount     = st.number_input("數量", min_value=0.0, value=1.0, step=0.1)

        # 2) 類型選單（你指定要保留）
        drink_type = st.selectbox("類型 (type)", ["water", "drink"])

        # 3) 分類選單（只顯示屬於該 type 的葉節點）
        choices_df = leaf_df[leaf_df["root_name"] == drink_type]
        if choices_df.empty:
            st.warning(f"目前 {drink_type} 底下沒有可選的分類（葉節點）。請先到『分類管理』新增。")
            category_name = None
        else:
            category_name = st.selectbox(
                "分類（葉節點）",
                options=choices_df["name"].tolist(),
                help="只列出該類型底下的最末層分類（例如：大水壺、7-11 綠茶）"
            )

        note = st.text_input("備註（可選）", placeholder="例如：運動後補水")

        submitted = st.form_submit_button("✅ 新增紀錄")
        if submitted:
            if category_name is None:
                st.error("請先建立對應類型的分類（葉節點）。")
                return

            # 找到 category_id
            category_id = int(cat_df.loc[cat_df["name"] == category_name, "id"].iloc[0])

            # 寫入 DB（包含 type 欄位）
            conn = connect_sql()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO drink_main (drink_date, drink_time, amount, type, note, category_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (drink_date, drink_time, amount, drink_type, note, category_id))
            conn.commit()
            conn.close()

            st.success(f"✅ 已新增：{drink_date} {drink_time}｜{drink_type}｜{category_name}｜數量 {amount}")
            st.rerun()
