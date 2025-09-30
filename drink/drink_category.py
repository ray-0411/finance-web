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

    def add_category(df_cat, max_depth=5):
        current_id = None
        current_name = None

        # 第一層：root
        options = df_cat[df_cat["parent_id"].isna()]
        if options.empty:
            st.error("❌ 沒有任何分類")
            return

        sel_name = st.selectbox(
            "第1層分類 (父分類選擇)",
            ["(無)"] + options["name"].tolist(),
            key="add_level1"
        )

        if sel_name != "(無)":
            current_name = sel_name
            current_id = int(options.loc[options["name"] == sel_name, "id"].iloc[0])

        # 往下展開子層
        for depth in range(2, max_depth + 1):
            if current_id is None:
                break
            sub_options = df_cat[df_cat["parent_id"] == current_id]
            if sub_options.empty:
                break

            sel_name = st.selectbox(
                f"第{depth}層分類 (父分類選擇)",
                ["(無)"] + sub_options["name"].tolist(),
                key=f"add_level{depth}"
            )

            if sel_name == "(無)":
                break  # 停在上一層，新增子分類
            else:
                current_name = sel_name
                current_id = int(sub_options.loc[sub_options["name"] == sel_name, "id"].iloc[0])

        # ====== 填寫新分類資訊 ======
        with st.form("add_category_form", clear_on_submit=True):
            new_name = st.text_input("分類名稱", placeholder="例如：大水壺、綠茶、7-11")
            weight = st.number_input("權重 (預設=1)", min_value=0.0, value=1.0, step=0.5)

            submitted = st.form_submit_button("新增分類")
            if submitted:
                conn = connect_sql()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO drink_category (name, parent_id, weight)
                    VALUES (%s, %s, %s)
                    """,
                    (new_name, current_id, weight)  # ⭐ current_id 會是父分類，None 代表 root
                )
                conn.commit()
                conn.close()
                st.success(f"✅ 已新增分類：{new_name}")
                time.sleep(0.5)
                st.rerun()


    # 使用
    add_category(all_df, max_depth=5)


    
    # ======================================================
    # 3️⃣ 修改分類權重（雙層選擇）
    # ======================================================
    def modify_category_weight(df_cat, max_depth=5):
        """
        一層一層往下選分類，選到 (無) 就代表修改上一層
        """
        current_id = None
        current_name = None

        # 第一層：root
        options = df_cat[df_cat["parent_id"].isna()]
        if options.empty:
            st.error("❌ 沒有任何分類")
            return

        sel_name = st.selectbox(
            "第1層分類",
            ["(無)"] + options["name"].tolist(),
            key="level1"
        )

        if sel_name != "(無)":
            current_name = sel_name
            current_id = int(options.loc[options["name"] == sel_name, "id"].iloc[0])
        else:
            st.info("⚠ 請先選一個分類")
            return

        # 往下展開
        for depth in range(2, max_depth + 1):
            sub_options = df_cat[df_cat["parent_id"] == current_id]
            if sub_options.empty:
                break

            sel_name = st.selectbox(
                f"第{depth}層分類",
                ["(無)"] + sub_options["name"].tolist(),
                key=f"level{depth}"
            )

            if sel_name == "(無)":
                break  # 表示要修改上一層
            else:
                current_name = sel_name
                current_id = int(sub_options.loc[sub_options["name"] == sel_name, "id"].iloc[0])

        # 顯示並修改最後選到的分類
        if current_id is not None:
            current_weight = float(df_cat.loc[df_cat["id"] == current_id, "weight"].iloc[0])
            new_weight = st.number_input(
                f"「{current_name}」的權重",
                min_value=0.0,
                value=current_weight,
                step=0.5,
                key=f"weight_final"
            )
            if st.button("更新權重", use_container_width=True):
                conn = connect_sql()
                cur = conn.cursor()
                cur.execute("UPDATE drink_category SET weight = %s WHERE id = %s", (new_weight, current_id))
                conn.commit()
                conn.close()
                st.success(f"✅ 已更新 {current_name} 的權重：{current_weight} → {new_weight}")
                time.sleep(0.5)
                st.rerun()

    st.subheader("⚖ 修改分類權重")
    modify_category_weight(all_df, max_depth=5)   # 這裡的 max_depth 可以自己調





    # ======================================================
    # 4️⃣ 刪除分類（雙層選擇）
    # ====================================================
    st.divider()
    st.subheader("🗑 刪除分類")

    def delete_category(df_cat, max_depth=5):
        current_id = None
        current_name = None

        # 第一層：root
        options = df_cat[df_cat["parent_id"].isna()]
        if options.empty:
            st.error("❌ 沒有任何分類")
            return

        sel_name = st.selectbox(
            "第1層分類",
            ["(無)"] + options["name"].tolist(),
            key="delete_level1"
        )

        if sel_name != "(無)":
            current_name = sel_name
            current_id = int(options.loc[options["name"] == sel_name, "id"].iloc[0])
        else:
            st.info("⚠ 請先選一個分類")
            return

        # 往下展開
        for depth in range(2, max_depth + 1):
            sub_options = df_cat[df_cat["parent_id"] == current_id]
            if sub_options.empty:
                break

            sel_name = st.selectbox(
                f"第{depth}層分類",
                ["(無)"] + sub_options["name"].tolist(),
                key=f"delete_level{depth}"
            )

            if sel_name == "(無)":
                break  # 表示停在上一層，刪除父分類
            else:
                current_name = sel_name
                current_id = int(sub_options.loc[sub_options["name"] == sel_name, "id"].iloc[0])

        # 執行刪除確認
        if current_id is not None:
            if st.button(f"刪除 {current_name}", key="delete_btn"):
                st.session_state.remove_category_target = current_name

            if st.session_state.get("remove_category_target") is not None:
                target_name = st.session_state.remove_category_target
                st.warning(f"⚠️ 確定要刪除 {target_name} 嗎？（此動作無法復原）")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ 確定刪除", key="delete_confirm"):
                        target_id = int(df_cat.loc[df_cat["name"] == target_name, "id"].iloc[0])
                        conn = connect_sql()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE drink_category SET is_deleted = TRUE WHERE id = %s", (target_id,))
                        conn.commit()
                        conn.close()
                        st.success(f"🗑️ 已刪除分類 {target_name}")
                        st.session_state.remove_category_target = None
                        st.rerun()

                with col2:
                    if st.button("❌ 取消刪除", key="delete_cancel"):
                        st.session_state.remove_category_target = None
                        st.info("已取消刪除")
                        time.sleep(0.5)
                        st.rerun()


    # 使用
    delete_category(all_df, max_depth=5)
