import streamlit as st
import pandas as pd
import time
from st_aggrid import AgGrid, GridOptionsBuilder
from db import connect_sql   # ✅ 用你專案的共用連線 function


def drink_category_page():
    st.title("📂 分類管理")

    # 1️⃣ 讀取現有分類 (只顯示未刪除)
    conn = connect_sql()
    all_df = pd.read_sql("""
        SELECT c.id, c.name, c.parent_id, p.name AS parent_name, c.weight, c.is_deleted
        FROM drink_category c
        LEFT JOIN drink_category p ON c.parent_id = p.id
        WHERE c.is_deleted = FALSE
        ORDER BY c.id
    """, conn)
    conn.close()

    # st.subheader("分類總表")
    # st.dataframe(all_df[["id", "name", "parent_name", "weight"]], use_container_width=True)


    def show_category_tree(df, parent_id=None, level=0, parent_weight=1):
        if parent_id is None:
            children = df[df["parent_id"].isnull() | (df["parent_id"] == 0)]
        else:
            children = df[df["parent_id"] == parent_id]

        for _, row in children.iterrows():
            # 計算「當前累積權重」
            total_weight = parent_weight * row["weight"]

            sub_children = df[df["parent_id"] == row["id"]]

            if not sub_children.empty:
                with st.expander("　" * level + f"{row['name']} 分數 : {total_weight} ", expanded=False):
                    show_category_tree(df, parent_id=row["id"], level=level+1, parent_weight=total_weight)
            else:
                st.write("　" * level + f"- {row['name']} 分數 : {total_weight} ")


    # 使用方式
    st.subheader("📂 分類樹狀顯示")
    show_category_tree(all_df)



    st.divider()

    # ======================================================
    # 2️⃣ 新增分類
    # ======================================================
    st.subheader("➕ 新增分類")

    # 找出 drink 的 id
    drink_row = all_df[(all_df["name"] == "drink") & (all_df["parent_id"].isna())]
    drink_id = int(drink_row["id"].iloc[0]) if not drink_row.empty else None

    # 只保留 water、drink、以及 drink 的子分類
    options_parent = all_df[all_df["parent_id"].isna()]["name"].tolist()  # water, drink
    if drink_id is not None:
        options_parent += all_df[all_df["parent_id"] == drink_id]["name"].tolist()  # drink 底下的


    with st.form("add_category_form", clear_on_submit=True):
        new_name = st.text_input("分類名稱", placeholder="例如：大水壺、綠茶、7-11")
        
        parent_sel = st.selectbox("父分類", options=options_parent)
        if parent_sel == "(無父分類)":
            parent_id_sel = None
        else:
            parent_id_sel = int(all_df.loc[all_df["name"] == parent_sel, "id"].iloc[0]) 
            
        weight = st.number_input("權重 (預設=1)", min_value=0.0, value=1.0, step=0.5)

        submitted = st.form_submit_button("新增分類")
        if submitted:
            conn = connect_sql()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO drink_category (name, parent_id, weight)
                VALUES (%s, %s, %s)
            """, (new_name, parent_id_sel, weight))
            conn.commit()
            conn.close()
            st.success(f"✅ 已新增分類：{new_name}")
            time.sleep(0.5)
            st.rerun()

    st.divider()

    
    # ======================================================
    # 3️⃣ 修改分類權重（雙層選擇）
    # ======================================================
    st.subheader("⚖ 修改分類權重")

    if all_df.empty:
        st.info("目前沒有分類可以修改")
    else:
        # 上層選單（保護：加 None）
        options_parent = [None] + all_df[all_df["parent_id"].isna()]["name"].tolist()
        if drink_id is not None:
            options_parent += all_df[all_df["parent_id"] == drink_id]["name"].tolist()

        parent_sel = st.selectbox(
            "上層分類",
            options=options_parent,
            format_func=lambda x: "請選擇" if x is None else x,
            key="modify_weight_parent"  # 用 key 避免和上面衝突
        )

        if parent_sel is None:
            st.info("⚠ 請先選擇上層分類")
        else:
            parent_id_sel = int(all_df.loc[all_df["name"] == parent_sel, "id"].iloc[0])
            children = all_df[all_df["parent_id"] == parent_id_sel]

            if children.empty:
                st.info(f"「{parent_sel}」沒有子分類可以修改權重")
            else:
                child_sel = st.selectbox("子分類", options=children["name"].tolist())

                current_weight = float(all_df.loc[all_df["name"] == child_sel, "weight"].iloc[0])
                new_weight = st.number_input("新的權重", min_value=0.0, value=current_weight, step=0.5)

                if st.button("更新權重", use_container_width=True):
                    child_id_sel = int(all_df.loc[all_df["name"] == child_sel, "id"].iloc[0])
                    conn = connect_sql()
                    cur = conn.cursor()
                    cur.execute("UPDATE drink_category SET weight = %s WHERE id = %s", (new_weight, child_id_sel))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ 已更新 {child_sel} 的權重：{current_weight} → {new_weight}")
                    time.sleep(0.5)
                    st.rerun()





    # ======================================================
    # 4️⃣ 刪除分類（雙層選擇）
    # ====================================================
    st.divider()
    st.subheader("🗑 刪除分類")

    # 上層選單
    options_parent = [None] + all_df[all_df["parent_id"].isna()]["name"].tolist()
    if drink_id is not None:
        options_parent += all_df[all_df["parent_id"] == drink_id]["name"].tolist()

    parent_sel = st.selectbox(
        "上層分類",
        options=options_parent,
        format_func=lambda x: "請選擇" if x is None else x,
        key="delete_parent"  # 用 key 避免和下面衝突
    )

    if parent_sel and parent_sel != "請選擇":
        parent_id_sel = int(all_df.loc[all_df["name"] == parent_sel, "id"].iloc[0])
        children = all_df[all_df["parent_id"] == parent_id_sel]

        if not children.empty:
            child_options = [None] + children["name"].tolist()
            child_sel = st.selectbox(
                "子分類",
                options=child_options,
                format_func=lambda x: "請選擇" if x is None else x,
                key="delete_child"  # 用 key 避免和上面衝突
            )

            if child_sel not in (None, "請選擇"):
                # 1️⃣ 先設定刪除目標
                if st.button(f"刪除 {child_sel}"):
                    st.session_state.remove_category_target = child_sel

                # 2️⃣ 確認刪除
                if st.session_state.get("remove_category_target") is not None:
                    target_name = st.session_state.remove_category_target
                    st.warning(f"⚠️ 確定要刪除 {target_name} 嗎？（此動作無法復原）")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ 確定刪除"):
                            child_id_sel = int(all_df.loc[all_df["name"] == target_name, "id"].iloc[0])
                            conn = connect_sql()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE drink_category SET is_deleted = TRUE WHERE id = %s", (child_id_sel,))
                            conn.commit()
                            conn.close()
                            st.success(f"🗑️ 已刪除分類 {target_name}")
                            st.session_state.remove_category_target = None
                            st.rerun()

                    with col2:
                        if st.button("❌ 取消刪除"):
                            st.session_state.remove_category_target = None
                            st.info("已取消刪除")
                            time.sleep(0.5)
                            st.rerun()
        else:
            st.info(f"「{parent_sel}」沒有子分類")
    else:
        st.info("請先選擇上層分類")
