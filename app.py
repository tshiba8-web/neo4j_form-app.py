import streamlit as st
st.set_page_config(layout="wide")
st.title("ナレッジ管理システム")

tab_user, tab_admin, tab_graph = st.tabs(
    ["一般ユーザー", "管理者", "グラフ表示"]
)

# ==================================================
# 一般ユーザー
# ==================================================

# =============================
# 操作選択
# =============================
mode = st.radio(
    "操作を選択してください",
    ["Qを登録する", "ノードの登録を依頼する"]
)

st.divider()

# ============================================================
# Q 登録
# ============================================================
if mode == "Qを登録する":

    st.header("質問（Question）登録")

    title = st.text_input("タイトル")
    description = st.text_area("詳細")

    col1, col2 = st.columns(2)

    with col1:
        environment = st.selectbox(
            "使用環境",
            ["Windows11", "Windows10", "その他"]
        )

    with col2:
        program = st.selectbox(
            "プログラム",
            ["ss7", "その他"]
        )

    st.subheader("関連付けたいノードを選択")

    st.caption("検索して既存ノードを選択します（後でDB連携）")

    problem = st.multiselect("Problem")
    cause = st.multiselect("Cause")
    action = st.multiselect("Action")
    explanation = st.multiselect("Explanation")
    request = st.multiselect("Request")

    if st.button("登録"):
        st.success("登録内容（ダミー）")
        st.write({
            "title": title,
            "description": description,
            "environment": environment,
            "program": program,
            "problem": problem,
            "cause": cause,
            "action": action,
            "explanation": explanation,
            "request": request
        })


# ============================================================
# 登録依頼
# ============================================================
elif mode == "ノードの登録を依頼する":

    st.header("新規ノード登録依頼")

    label = st.selectbox(
        "作成して欲しいラベル",
        ["Problem", "Cause", "Action", "Explanation", "Request"]
    )

    title = st.text_input("タイトル")
    description = st.text_area("詳細")

    if st.button("依頼を送信"):
        st.success("依頼内容（ダミー）")
        st.write({
            "label": label,
            "title": title,
            "description": description
        })

# ==================================================
# 管理者
# ==================================================
with tab_admin:
    st.header("管理者メニュー")

    st.subheader("既存ノード検索")
    search_label = st.selectbox(
        "ラベル",
        ["Question", "Problem", "Cause", "Action", "Explanation", "Request"]
    )
    search_word = st.text_input("検索ワード")

    if st.button("検索"):
        st.info("検索結果（ダミー）")
        st.write([f"{search_label}_001", f"{search_label}_002"])

    st.divider()
    st.subheader("新規ノード作成")

    create_label = st.selectbox(
        "作成するラベル",
        ["Problem", "Cause", "Action", "Explanation", "Request"]
    )

    st.text_input("タイトル")
    st.text_area("詳細")

    if create_label in ["Action", "Explanation"]:
        st.text_input("入力項目")
        st.text_input("出力項目")
        st.text_input("参考")

    if create_label == "Request":
        st.selectbox("対応状況", ["未対応", "対応中", "完了"])

    if st.button("ノード作成"):
        st.success("作成依頼を受け付けました")

    st.divider()
    st.subheader("リレーション作成")

    st.text_input("元ノード key")
    st.selectbox(
        "リレーション",
        ["ABOUT", "CAUSED_BY", "RESOLVED_BY", "EXPLAINED_BY", "REQUESTS"]
    )
    st.text_input("接続先 key")

    if st.button("リレーション登録"):
        st.success("リレーション登録依頼を受け付けました")


# ==================================================
# グラフ表示
# ==================================================
with tab_graph:
    st.header("グラフ表示")

    key = st.text_input("question_key")

    if st.button("表示"):
        st.info("ここにグラフが表示されます（後でNeo4j連携）")

