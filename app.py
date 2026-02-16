import streamlit as st

# =========================================
# 仮データ（あとでNeo4jから取得に変更）
# =========================================

ENV_OPTIONS = ["Windows11", "Windows10", "Linux"]
PROGRAM_OPTIONS = ["ss7", "dify", "neo4j"]

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

st.set_page_config(page_title="Neo4j Form", layout="wide")
st.title("Neo4j データ登録フォーム最新版")

# =========================================
# 一般ユーザー
# =========================================

def user_tab():
    st.header("一般ユーザー")

    mode = st.radio(
        "作業を選択",
        ["質問・リレーションの登録", "ノードの追加依頼"],
        key="u_mode",
        horizontal=True
    )

    # ===============================
    # 質問 + Relation
    # ===============================
    if mode == "質問・リレーションの登録":

        st.subheader("質問情報")

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("タイトル", key="u_q_title")
        with col2:
            st.selectbox("環境", ENV_OPTIONS, key="u_q_env")

        col3, col4 = st.columns(2)
        with col3:
            st.text_area("詳細", key="u_q_desc")
        with col4:
            st.selectbox("プログラム", PROGRAM_OPTIONS, key="u_q_program")

        st.markdown("---")
        st.subheader("リレーション")

        for i in range(3):
            with st.expander(f"Relation {i+1}", expanded=(i == 0)):

                c1, c2 = st.columns(2)

                # FROM
                with c1:
                    st.markdown("### FROM")
                    from_label = st.selectbox(
                        "ラベル",
                        ["Question"] + list(KEY_SAMPLE.keys()),
                        key=f"u_from_label_{i}"
                    )
                    st.text_input("検索ワード", key=f"u_from_kw_{i}")
                    st.button("検索", key=f"u_from_search_{i}")
                    st.selectbox(
                        "候補",
                        KEY_SAMPLE.get(from_label, ["Q_NEW"]),
                        key=f"u_from_key_{i}"
                    )

                # TO
                with c2:
                    st.markdown("### TO")
                    to_label = st.selectbox(
                        "ラベル",
                        list(KEY_SAMPLE.keys()),
                        key=f"u_to_label_{i}"
                    )
                    st.text_input("検索ワード", key=f"u_to_kw_{i}")
                    st.button("検索", key=f"u_to_search_{i}")
                    st.selectbox(
                        "候補",
                        KEY_SAMPLE[to_label],
                        key=f"u_to_key_{i}"
                    )

        st.markdown("---")
        st.button("登録", key="u_submit")

    # ===============================
    # ノード追加依頼
    # ===============================
    else:
        st.subheader("ノード追加依頼")

        label = st.selectbox(
            "追加希望ラベル",
            ["Problem", "Cause", "Action", "Explanation", "Request", "Software"],
            key="u_req_label"
        )

        st.text_input("タイトル", key="u_req_title")
        st.text_area("詳細", key="u_req_desc")

        if label in ["Action", "Explanation"]:
            st.text_input("入力項目", key="u_req_input")
            st.text_input("出力項目", key="u_req_output")
            st.text_input("参考", key="u_req_reference")

        if label == "Request":
            st.selectbox(
                "対応状況",
                ["未対応", "対応中", "完了"],
                key="u_req_status"
            )

        if label == "Software":
            st.text_input("name", key="u_req_name")

        st.button("依頼送信", key="u_req_submit")


# =========================================
# 管理者
# =========================================

def admin_tab():
    st.header("管理者")

    mode = st.radio(
        "作業を選択",
        ["ノード作成", "リレーション作成"],
        key="a_mode",
        horizontal=True
    )

    # ===============================
    # ノード作成
    # ===============================
    if mode == "ノード作成":
        st.subheader("ノード作成")

        label = st.selectbox(
            "ラベル",
            ["Problem", "Cause", "Action", "Explanation", "Request", "Software"],
            key="a_label"
        )

        st.text_input("タイトル", key="a_title")
        st.text_area("詳細", key="a_desc")

        if label in ["Action", "Explanation"]:
            st.text_input("入力項目", key="a_input")
            st.text_input("出力項目", key="a_output")
            st.text_input("参考", key="a_reference")

        if label == "Request":
            st.selectbox(
                "対応状況",
                ["未対応", "対応中", "完了"],
                key="a_status"
            )

        if label == "Software":
            st.text_input("name", key="a_name")

        st.button("作成", key="a_submit")

    # ===============================
    # リレーション作成
    # ===============================
    else:
        st.subheader("リレーション作成")

        for i in range(3):
            with st.expander(f"Relation {i+1}", expanded=(i == 0)):

                st.selectbox(
                    "FROMラベル",
                    list(KEY_SAMPLE.keys()),
                    key=f"a_from_label_{i}"
                )
                st.text_input("FROM検索", key=f"a_from_kw_{i}")
                st.button("検索", key=f"a_from_search_{i}")
                st.selectbox(
                    "FROM候補",
                    ["sample"],
                    key=f"a_from_candidate_{i}"
                )

                st.selectbox(
                    "TOラベル",
                    list(KEY_SAMPLE.keys()),
                    key=f"a_to_label_{i}"
                )
                st.text_input("TO検索", key=f"a_to_kw_{i}")
                st.button("検索", key=f"a_to_search_{i}")
                st.selectbox(
                    "TO候補",
                    ["sample"],
                    key=f"a_to_candidate_{i}"
                )

        st.button("登録", key="a_rel_submit")


# =========================================
# グラフ
# =========================================

def graph_tab():
    st.header("グラフ表示")
    st.info("可視化エリア")


# =========================================
# タブ
# =========================================

t1, t2, t3 = st.tabs(["一般ユーザー", "管理者", "グラフ"])

with t1:
    user_tab()

with t2:
    admin_tab()

with t3:
    graph_tab()
