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
