import os
import streamlit as st
import requests
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd

# ==============================
# Neo4j 接続設定
# ==============================
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "takashi2468")

def get_driver():
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )

driver = get_driver()

# ===============================
# リレーション定義
# ===============================
RELATION_RULES = {
    "Question": {
        "Problem": "ABOUT",
        "Cause": "CAUSED_BY",
        "Action": "RESOLVED_BY",
        "Explanation": "EXPLAINED_BY",
        "Request": "REQUESTS"
    },
    "Problem": {
        "Cause": "HAS_CAUSE",
        "Action": "HAS_ACTION",
        "Explanation": "HAS_EXPLANATION",
        "Software": "BELONGS_TO"
    },
    "Cause": {
        "Action": "RESOLVED_BY"
    },
    "Request": {
        "Problem": "REQUESTS"
    }
}

LABELS = [
    "Question",
    "Problem",
    "Cause",
    "Action",
    "Explanation",
    "Request",
    "Software"
]

# =========================================
# 共通関数
# =========================================

def search_nodes(label, keyword):

    if not keyword.strip():
        return []

    query = f"""
    MATCH (n:{label})
    WHERE any(k IN keys(n)
        WHERE n[k] IS NOT NULL
        AND toLower(toString(n[k])) CONTAINS toLower($keyword))
    RETURN n
    LIMIT 50
    """

    with driver.session() as session:
        result = session.run(query, keyword=keyword)
        return [record["n"] for record in result]


def create_node(label, properties):

    if label == "Question":
        query = """
        WITH randomUUID() AS uid
        CREATE (n:Question {
            uuid: uid,
            question_key: "Q-" + substring(uid,0,8)
        })
        SET n += $props
        RETURN n
        """
    else:
        query = f"""
        CREATE (n:{label} {{
            uuid: randomUUID()
        }})
        SET n += $props
        RETURN n
        """

    with driver.session() as session:
        result = session.run(query, props=properties)
        record = result.single()
        return record["n"] if record else None


def update_node(uuid, properties):

    with driver.session() as session:

        set_clauses = []
        remove_clauses = []

        for key, value in properties.items():

            if key == "uuid":
                continue

            if value == "" or value is None:
                remove_clauses.append(f"n.{key}")
            else:
                set_clauses.append(f"n.{key} = ${key}")

        query = "MATCH (n {uuid:$uuid}) "

        if set_clauses:
            query += "SET " + ", ".join(set_clauses) + " "

        if remove_clauses:
            query += "REMOVE " + ", ".join(remove_clauses)

        params = {"uuid": uuid}

        for k, v in properties.items():
            if v not in ["", None] and k != "uuid":
                params[k] = v

        session.run(query, params)


def delete_node(uuid):

    with driver.session() as session:
        session.run("""
        MATCH (n {uuid:$uuid})
        DETACH DELETE n
        """, uuid=uuid)


def search_relations(label):

    query = f"""
    MATCH (a:{label})-[r]->(b)
    RETURN a.title AS from_title,
           type(r) AS rel,
           b.title AS to_title,
           a.uuid AS from_uuid,
           b.uuid AS to_uuid
    LIMIT 50
    """

    with driver.session() as session:
        return session.run(query).data()


def count_nodes():

    query = """
    MATCH (n)
    RETURN labels(n)[0] AS label, count(*) AS count
    """

    with driver.session() as session:
        return session.run(query).data()


def find_isolated_nodes():

    query = """
    MATCH (n)
    WHERE NOT (n)--()
    RETURN n
    LIMIT 50
    """

    with driver.session() as session:
        return [r["n"] for r in session.run(query)]


def find_duplicate_titles():

    query = """
    MATCH (n)
    WHERE n.title IS NOT NULL
    WITH n.title AS title, collect(n) AS nodes, count(*) AS cnt
    WHERE cnt > 1
    RETURN title, cnt
    """

    with driver.session() as session:
        return session.run(query).data()


def show_graph():

    query = """
    MATCH (a)-[r]->(b)
    RETURN a,r,b
    LIMIT 50
    """

    node_map = {}
    edges = []

    with driver.session() as session:

        result = session.run(query)

        for record in result:

            a = record["a"]
            b = record["b"]
            r = record["r"]

            node_map[a["uuid"]] = Node(
                id=a["uuid"],
                label=a.get("title", "node")
            )

            node_map[b["uuid"]] = Node(
                id=b["uuid"],
                label=b.get("title", "node")
            )

            edges.append(
                Edge(
                    source=a["uuid"],
                    target=b["uuid"],
                    label=r.type
                )
            )

    config = Config(
        width=900,
        height=600,
        directed=True
    )

    agraph(nodes=list(node_map.values()), edges=edges, config=config)


# ===============================
# UI
# ===============================

st.set_page_config(page_title="Neo4j Form", layout="wide")
st.title("Neo4j データ登録フォーム")


# ===============================
# 管理タブ
# ===============================

def admin_tab():

    st.header("管理者")

    mode = st.radio(
        "作業を選択",
        [
            "ノード作成",
            "ノード管理",
            "リレーション作成",
            "リレーション削除",
            "データ管理"
        ],
        horizontal=True
    )

    # ------------------
    # ノード作成
    # ------------------

    if mode == "ノード作成":

        label = st.selectbox("ラベル", LABELS)

        title = st.text_input("title")
        description = st.text_area("description")

        if st.button("作成"):

            props = {
                "title": title,
                "description": description
            }

            create_node(label, props)

            st.success("作成しました")

    # ------------------
    # ノード管理
    # ------------------

    if mode == "ノード管理":

        label = st.selectbox("検索ラベル", LABELS)

        kw = st.text_input("検索")

        results = search_nodes(label, kw) if kw else []

        st.write(f"検索結果 {len(results)} 件")

        if results:

            options = {
                f"{n.get('title','No title')} ({n['uuid'][:6]})": n
                for n in results
            }

            selected = st.selectbox("ノード選択", list(options.keys()))

            node = options[selected]

            title = st.text_input("title", node.get("title",""))
            desc = st.text_area("description", node.get("description",""))

            if st.button("更新"):

                update_node(node["uuid"], {
                    "title": title,
                    "description": desc
                })

                st.success("更新しました")

            if st.button("削除"):

                delete_node(node["uuid"])

                st.success("削除しました")

    # ------------------
    # リレーション削除
    # ------------------

    if mode == "リレーション削除":

        label = st.selectbox("ラベル", LABELS)

        relations = search_relations(label)

        st.write(f"{len(relations)} 件")

        if relations:

            options = {
                f"{r['from_title']} -[{r['rel']}]-> {r['to_title']}": r
                for r in relations
            }

            selected = st.selectbox("削除対象", list(options.keys()))

            r = options[selected]

            if st.button("削除"):

                with driver.session() as session:

                    session.run("""
                    MATCH (a {uuid:$a})-[rel]->(b {uuid:$b})
                    DELETE rel
                    """, a=r["from_uuid"], b=r["to_uuid"])

                st.success("削除しました")

    # ------------------
    # データ管理
    # ------------------

    if mode == "データ管理":

        st.subheader("ノード数")

        counts = count_nodes()

        for c in counts:
            st.write(f"{c['label']} : {c['count']}")

        st.subheader("孤立ノード")

        iso = find_isolated_nodes()

        st.write(len(iso), "件")

        st.subheader("重複タイトル")

        dup = find_duplicate_titles()

        st.write(dup)


# ===============================
# グラフ
# ===============================

def graph_tab():

    st.subheader("Graph表示")

    if st.button("グラフ描画"):
        show_graph()


# ===============================
# タブ
# ===============================

t1, t2, t3 = st.tabs(["一般ユーザー", "管理者", "グラフ"])

with t2:
    admin_tab()

with t3:
    graph_tab()
