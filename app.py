import streamlit as st

st.title("ナレッジ管理システム")

tab_user, tab_admin, tab_graph = st.tabs(
    ["一般ユーザー", "管理者", "グラフ表示"]
)

# ==================================================
# 一般ユーザー
# ==================================================
with tab_user:
    st.header("質問登録")

    title = st.text_input("タイトル")
    description = st.text_area("詳細")

    st.divider()
    st.subheader("関連付け")

    def relation_selector(label):
        st.markdown(f"### {label}")
        keyword = st.text_input(f"{label} 検索", key=label)

        # ★後でNeo4j検索結果に変わる
        dummy = [f"{label}_001", f"{label}_002", f"{label}_003"]

        return st.multiselect("候補", dummy, key=f"select_{label}")

    problems = relation_selector("Problem")
    causes = relation_selector("Cause")
    actions = relation_selector("Action")
    explanations = relation_selector("Explanation")
    requests = relation_selector("Request")

    if st.button("登録依頼"):
        st.success("登録依頼内容")
        st.json({
            "title": title,
            "description": description,
            "ABOUT": problems,
            "CAUSED_BY": causes,
            "RESOLVED_BY": actions,
            "EXPLAINED_BY": explanations,
            "REQUESTS": requests
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

