import streamlit as st

# =========================================
# 仮データ（あとでNeo4jから取得に変更）
# =========================================

ENV_OPTIONS = ["Windows11", "Windows10", "Linux"]
PROGRAM_OPTIONS = ["ss7", "dify", "neo4j"]

# key検索の代替（将来DB検索へ）
KEY_SAMPLE = {
    "Problem": ["P001", "P002"],
    "Cause": ["C001", "C002"],
    "Action": ["A001", "A002"],
    "Explanation": ["E001"],
    "Request": ["R001"],
    "Software": ["S001"]
}

# =========================================
# 共通
# =========================================

def init_page():
    st.set_page_config(page_title="Neo4j Form", layout="wide")
    st.title("Neo4j データ登録フォーム")

# =========================================
# 一般ユーザー
# =========================================

def user_register_question_and_relation():
    st.subheader("質問 + リレーション登録")

    # =====================
    # Question
    # =====================
    st.markdown("### 質問情報")
    title = st.text_input("タイトル", key="u_q_title")
    description = st.text_area("詳細", key="u_q_desc")
    env = st.selectbox("環境", ENV_OPTIONS, key="u_q_env")
    program = st.selectbox("プログラム", PROGRAM_OPTIONS, key="u_q_program")

    st.markdown("---")
    st.markdown("### リレーション指定（最大3件）")

    for i in range(3):
        st.markdown(f"## Relation {i+1}")

        # =====================
        # FROM
        # =====================
        st.markdown("### FROM")

        from_label = st.selectbox(
            "ラベル",
            ["Question"] + list(KEY_SAMPLE.keys()),
            key=f"u_from_label_{i}"
        )

        from_keyword = st.text_input(
            "検索ワード",
            key=f"u_from_kw_{i}"
        )

        if st.button("検索", key=f"u_from_search_{i}"):
            st.info("ここでNeo4j検索（将来実装）")

        from_key = st.selectbox(
            "候補",
            KEY_SAMPLE.get(from_label, ["Q_NEW"]),
            key=f"u_from_key_{i}"
        )

        st.markdown("---")

        # =====================
        # TO
        # =====================
        st.markdown("### TO")

        to_label = st.selectbox(
            "ラベル",
            list(KEY_SAMPLE.keys()),
            key=f"u_to_label_{i}"
        )

        to_keyword = st.text_input(
            "検索ワード",
            key=f"u_to_kw_{i}"
        )

        if st.button("検索", key=f"u_to_search_{i}"):
            st.info("ここでNeo4j検索（将来実装）")

        to_key = st.selectbox(
            "候補",
            KEY_SAMPLE[to_label],
            key=f"u_to_key_{i}"
        )

        st.markdown("=======")

    if st.button("登録", key="u_submit"):
        st.success("登録リクエスト送信（仮）")




def user_request_node():
    st.subheader("ノード追加依頼")

    label = st.selectbox(
        "追加希望ラベル",
        ["Problem", "Cause", "Action", "Explanation", "Request", "Software"],
        key="u_req_label"
    )

    title = st.text_input("タイトル", key="u_req_title")
    description = st.text_area("詳細", key="u_req_desc")

    # ラベル別追加項目
    if label in ["Action", "Explanation"]:
        st.text_input("入力項目", key="a_input")
        st.text_input("出力項目", key="a_output")
        st.text_input("参考", key="a_ref")

    if label == "Request":
        st.selectbox("対応状況", ["未対応", "対応中", "完了"], key="a_status")

    if label == "Software":
        st.text_input("name", key="a_name")
    
    if st.button("依頼送信", key="u_req_submit"):
        st.success("依頼送信完了")


def user_tab():
    st.header("一般ユーザー")

    menu = st.radio(
        "作業を選択",
        ["質問・リレーションの登録", "ノードの追加依頼"]
    )

    if menu == "質問・リレーションの登録":
        user_register_question_and_relation()
    else:
        user_request_node()

# =========================================
# 管理者
# =========================================

def admin_create_node():
    st.subheader("ノード作成")

    label = st.selectbox(
        "ラベル",
        ["Problem", "Cause", "Action", "Explanation", "Request", "Software"],
        key="a_label"
    )

    # 共通
    title = st.text_input("タイトル", key="a_title")
    description = st.text_area("詳細", key="a_desc")

    # ラベル別追加項目
    if label in ["Action", "Explanation"]:
        st.text_input("入力項目", key="a_input")
        st.text_input("出力項目", key="a_output")
        st.text_input("参考", key="a_ref")

    if label == "Request":
        st.selectbox("対応状況", ["未対応", "対応中", "完了"], key="a_status")

    if label == "Software":
        st.text_input("name", key="a_name")

    if st.button("作成", key="a_submit"):
        st.success("ノード作成（仮）")


def admin_create_relation():
    st.subheader("リレーション作成")

    from_key = st.text_input("FROM Key", key="a_from")
    to_key = st.text_input("TO Key", key="a_to")

    if st.button("作成", key="a_rel_submit"):
        st.success("リレーション作成（仮）")


def admin_tab():
    st.header("管理者")

    menu = st.radio(
        "作業を選択",
        ["ノード作成", "リレーション作成"]
    )

    if menu == "ノード作成":
        admin_create_node()
    else:
        admin_create_relation()

# =========================================
# グラフ
# =========================================

def graph_tab():
    st.header("グラフ表示")
    st.info("ここに可視化が入ります")

# =========================================
# main
# =========================================

def main():
    init_page()

    t1, t2, t3 = st.tabs(["一般ユーザー", "管理者", "グラフ"])

    with t1:
        user_tab()

    with t2:
        admin_tab()

    with t3:
        graph_tab()


if __name__ == "__main__":
    main()
