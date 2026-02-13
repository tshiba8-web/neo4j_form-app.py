import streamlit as st

# ==============================
# 共通部品
# ==============================

def init_page():
    st.set_page_config(page_title="Neo4j 登録フォーム", layout="wide")
    st.title("Neo4j データ登録")

# ==============================
# 一般ユーザー
# ==============================

def user_question_register():
    st.subheader("質問（Q）を登録")

    title = st.text_input("タイトル", key="user_q_title")
    description = st.text_area("詳細", key="user_q_desc")

    if st.button("登録", key="user_q_submit"):
        st.success("質問登録（仮）完了")


def user_relation_register():
    st.subheader("リレーションを登録")

    q_key = st.text_input("質問Key", key="user_rel_q")
    target_label = st.selectbox(
        "紐付けたいラベル",
        ["Problem", "Cause", "Action", "Explanation", "Request"],
        key="user_rel_label"
    )
    target_key = st.text_input("対象ノードKey", key="user_rel_key")

    if st.button("紐付け", key="user_rel_submit"):
        st.success("リレーション登録（仮）完了")


def user_request_register():
    st.subheader("ノード追加依頼")

    label = st.selectbox(
        "追加してほしいラベル",
        ["Problem", "Cause", "Action", "Explanation", "Request"],
        key="user_req_label"
    )
    title = st.text_input("タイトル", key="user_req_title")
    description = st.text_area("詳細", key="user_req_desc")

    if st.button("依頼送信", key="user_req_submit"):
        st.success("依頼送信完了")


def user_tab():
    st.header("一般ユーザー")

    menu = st.radio(
        "作業を選択",
        ["質問を登録", "リレーション作成", "ノード追加依頼"],
        key="user_menu"
    )

    if menu == "質問を登録":
        user_question_register()

    elif menu == "リレーション作成":
        user_relation_register()

    elif menu == "ノード追加依頼":
        user_request_register()

# ==============================
# 管理者
# ==============================

def admin_node_create():
    st.subheader("ノード追加")

    label = st.selectbox(
        "ラベル",
        ["Question", "Problem", "Cause", "Action", "Explanation", "Request"],
        key="admin_label"
    )

    title = st.text_input("タイトル", key="admin_title")
    description = st.text_area("詳細", key="admin_desc")

    if st.button("追加", key="admin_submit"):
        st.success("ノード追加（仮）完了")


def admin_relation_create():
    st.subheader("リレーション作成")

    from_key = st.text_input("FROM Key", key="admin_from")
    to_key = st.text_input("TO Key", key="admin_to")

    if st.button("作成", key="admin_rel_submit"):
        st.success("リレーション作成（仮）完了")


def admin_tab():
    st.header("管理者")

    menu = st.radio(
        "作業を選択",
        ["ノード追加", "リレーション作成"],
        key="admin_menu"
    )

    if menu == "ノード追加":
        admin_node_create()

    elif menu == "リレーション作成":
        admin_relation_create()

# ==============================
# グラフ表示
# ==============================

def graph_tab():
    st.header("グラフ表示")
    st.info("ここに将来グラフ描画が入ります")

# ==============================
# メイン
# ==============================

def main():
    init_page()

    tab_user, tab_admin, tab_graph = st.tabs(
        ["一般ユーザー", "管理者", "グラフ"]
    )

    with tab_user:
        user_tab()

    with tab_admin:
        admin_tab()

    with tab_graph:
        graph_tab()


if __name__ == "__main__":
    main()
