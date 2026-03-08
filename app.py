import os
import streamlit as st
import requests
import pandas as pd

from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config

# ==============================
# Neo4j 接続
# ==============================
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://192.168.5.56:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "takashi2468")

def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

driver = get_driver()

# ==============================
# 定義
# ==============================
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

LABELS = ["Question","Problem","Cause","Action","Explanation","Request","Software"]

STATUS_COLOR = {"未対応":"red","対応中":"orange","完了":"green"}

# ==============================
# DB操作
# ==============================
def search_nodes(label, keyword):
    if not keyword:
        return []
    query = f"""
    MATCH (n:{label})
    WHERE any(k IN keys(n)
      WHERE n[k] IS NOT NULL
      AND toLower(toString(n[k])) CONTAINS toLower($kw))
    RETURN n LIMIT 50
    """
    with driver.session() as s:
        return [r["n"] for r in s.run(query, kw=keyword)]

def create_node(label, props):
    if label == "Question":
        query = """
        WITH randomUUID() AS uid
        CREATE (n:Question {
            uuid: uid,
            question_key: "Q-" + substring(uid,0,8)
        })
        SET n += $p
        RETURN n
        """
    else:
        query = f"""
        CREATE (n:{label} {{uuid: randomUUID()}})
        SET n += $p
        RETURN n
        """
    with driver.session() as s:
        rec = s.run(query, p=props).single()
        return rec["n"] if rec else None

def update_node(uuid, properties):
    set_cl = []
    remove_cl = []
    params = {"uuid": uuid}

    for k,v in properties.items():
        if k=="uuid":
            continue
        if v=="" or v is None:
            remove_cl.append(f"n.{k}")
        else:
            set_cl.append(f"n.{k} = ${k}")
            params[k] = v

    query = "MATCH (n {uuid:$uuid}) "
    if set_cl:
        query += "SET " + ", ".join(set_cl) + " "
    if remove_cl:
        query += "REMOVE " + ", ".join(remove_cl)

    with driver.session() as s:
        s.run(query, params)

def delete_node(uuid):
    with driver.session() as s:
        s.run("MATCH (n {uuid:$uuid}) DETACH DELETE n", uuid=uuid)

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
    with driver.session() as s:
        return s.run(query).data()

def count_nodes():
    query = "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count"
    with driver.session() as s:
        return s.run(query).data()

def find_isolated_nodes():
    query = "MATCH (n) WHERE NOT (n)--() RETURN n LIMIT 50"
    with driver.session() as s:
        return [r["n"] for r in s.run(query)]

def find_duplicate_titles():
    query = """
    MATCH (n)
    WHERE n.title IS NOT NULL
    WITH n.title AS title, collect(n) AS nodes, count(*) AS cnt
    WHERE cnt > 1
    RETURN title, cnt
    """
    with driver.session() as s:
        return s.run(query).data()

def show_graph():
    query = "MATCH (a)-[r]->(b) RETURN a,r,b LIMIT 50"
    node_map = {}
    edges = []

    with driver.session() as s:
        for record in s.run(query):
            a = record["a"]
            b = record["b"]
            r = record["r"]

            node_map[a["uuid"]] = Node(id=a["uuid"], label=a.get("title","node"))
            node_map[b["uuid"]] = Node(id=b["uuid"], label=b.get("title","node"))

            edges.append(Edge(source=a["uuid"], target=b["uuid"], label=r.type))

    nodes = list(node_map.values())
    config = Config(width=900, height=600, directed=True)
    agraph(nodes=nodes, edges=edges, config=config, key="agraph_main")

# ==============================
# UI
# ==============================
st.set_page_config(page_title="Neo4j Form", layout="wide")
st.title("Neo4j データ登録フォーム")

def status_badge(status):
    color = STATUS_COLOR.get(status,"gray")
    st.markdown(f"**状態:** :{color}[{status}]")

# ==============================
# 一般ユーザー
# ==============================
def user_tab():
    st.header("一般ユーザー")

    mode = st.radio(
        "作業",
        ["質問・リレーション","ノード追加依頼"],
        horizontal=True,
        key="u_mode"
    )

    if mode == "質問・リレーション":

        if "u_registered" not in st.session_state:
            st.session_state.u_registered = False

        with st.expander("質問", expanded=True):
            st.text_input("タイトル", key="u_q_title")
            st.selectbox("環境", ["Windows","Linux"], key="u_q_env")
            st.text_area("詳細", key="u_q_desc")

        with st.expander("ジャンル", expanded=True):
            with driver.session() as s:
                problems = s.run("MATCH (p:Problem) RETURN p.uuid AS uuid,p.title AS title").data()

            problem_uuid = None
            if problems:
                options = {f"{p['title']} ({p['uuid'][:6]})":p["uuid"] for p in problems}
                sel = st.selectbox("Problem", ["選択"]+list(options.keys()), key="u_p_select")
                if sel != "選択":
                    problem_uuid = options[sel]

        with st.expander("関連", expanded=False):
            second_label = st.selectbox("関連タイプ",
                ["Cause","Explanation","Request","Action"],
                key="u_second_label")
            second_kw = st.text_input("検索", key="u_second_kw")
            second_results = search_nodes(second_label, second_kw) if second_kw else []
            second_uuid = None

            if second_results:
                opts = {f"{n.get('title','No Title')} ({n['uuid'][:6]})":n["uuid"] for n in second_results}
                sel = st.selectbox("候補", list(opts.keys()), key="u_second_select")
                second_uuid = opts[sel]

        if st.button("登録", type="primary"):
            title = st.session_state.get("u_q_title")
            if not title or not problem_uuid or not second_uuid:
                st.warning("必須項目が不足")
                st.stop()

            import uuid
            q_uuid = str(uuid.uuid4())
            rel2 = RELATION_RULES["Question"].get(second_label)
            if not rel2:
                st.error("リレーション定義なし")
                return

            with driver.session() as s:
                s.run("""
                CREATE (q:Question {
                    uuid:$uuid,
                    title:$title,
                    environment:$env,
                    description:$desc
                })""",
                uuid=q_uuid, title=title,
                env=st.session_state.get("u_q_env"),
                desc=st.session_state.get("u_q_desc"))

                s.run("MATCH (q:Question{uuid:$q}), (p:Problem{uuid:$p}) MERGE (q)-[:ABOUT]->(p)",
                      q=q_uuid, p=problem_uuid)

                s.run(f"MATCH (q:Question{{uuid:$q}}), (t{{uuid:$t}}) MERGE (q)-[:{rel2}]->(t)",
                      q=q_uuid, t=second_uuid)

            st.success("登録完了")
            st.session_state.u_registered = True

    else:
        st.subheader("ノード追加依頼")
        label = st.selectbox("ラベル", LABELS, key="u_req_label")
        st.text_input("タイトル", key="u_req_title")
        st.text_area("詳細", key="u_req_desc")

        if st.button("依頼送信"):
            st.success("送信しました")

# ==============================
# 管理
# ==============================
def admin_tab():
    st.header("管理")

    mode = st.radio(
        "作業",
        ["ノード作成","ノード管理","リレーション作成","リレーション削除","データ管理"],
        horizontal=True,
        key="admin_mode"
    )

    if mode == "ノード作成":
        label = st.selectbox("ラベル", LABELS, key="admin_create_label")
        title = st.text_input("title", key="admin_create_title")
        desc = st.text_area("description", key="admin_create_desc")

        if st.button("作成"):
            create_node(label, {"title":title,"description":desc})
            st.success("作成")

    if mode == "ノード管理":
        label = st.selectbox("検索ラベル", LABELS, key="admin_search_label")
        kw = st.text_input("検索", key="admin_search_kw")
        results = search_nodes(label, kw) if kw else []
        st.write(f"結果 {len(results)} 件")

        if results:
            opts = {f"{n.get('title','No title')} ({n['uuid'][:6]})":n for n in results}
            sel = st.selectbox("編集対象", list(opts.keys()), key="admin_edit_select")
            node = opts[sel]

            title = st.text_input("title", node.get("title",""), key="admin_edit_title")
            desc = st.text_area("description", node.get("description",""), key="admin_edit_desc")

            if st.button("更新"):
                update_node(node["uuid"], {"title":title,"description":desc})
                st.success("更新")

            if st.button("削除"):
                delete_node(node["uuid"])
                st.success("削除")

    if mode == "リレーション作成":
        from_label = st.selectbox("FROM", list(RELATION_RULES.keys()), key="rel_from")
        to_label = st.selectbox("TO", list(RELATION_RULES[from_label].keys()), key="rel_to")
        rel_type = RELATION_RULES[from_label][to_label]

        kw1 = st.text_input("FROM検索", key="rel_kw1")
        from_nodes = search_nodes(from_label, kw1) if kw1 else []
        from_uuid = None

        if from_nodes:
            opts = {f"{n.get('title','')} ({n['uuid'][:6]})":n["uuid"] for n in from_nodes}
            sel = st.selectbox("FROMノード", list(opts.keys()), key="rel_from_select")
            from_uuid = opts[sel]

        kw2 = st.text_input("TO検索", key="rel_kw2")
        to_nodes = search_nodes(to_label, kw2) if kw2 else []
        to_uuid = None

        if to_nodes:
            opts = {f"{n.get('title','')} ({n['uuid'][:6]})":n["uuid"] for n in to_nodes}
            sel = st.selectbox("TOノード", list(opts.keys()), key="rel_to_select")
            to_uuid = opts[sel]

        if st.button("作成"):
            with driver.session() as s:
                s.run(f"""
                MATCH (a{{uuid:$a}}),(b{{uuid:$b}})
                MERGE (a)-[:{rel_type}]->(b)
                """, a=from_uuid, b=to_uuid)
            st.success("作成")

    if mode == "リレーション削除":
        label = st.selectbox("ラベル", LABELS, key="rel_del_label")
        relations = search_relations(label)
        st.write(f"{len(relations)} 件")

        if relations:
            opts = {f"{r['from_title']} -[{r['rel']}]-> {r['to_title']}":r for r in relations}
            sel = st.selectbox("削除対象", list(opts.keys()), key="rel_del_select")
            r = opts[sel]

            if st.button("削除"):
                with driver.session() as s:
                    s.run("""
                    MATCH (a{uuid:$a})-[rel]->(b{uuid:$b})
                    DELETE rel
                    """, a=r["from_uuid"], b=r["to_uuid"])
                st.success("削除")

    if mode == "データ管理":
        st.subheader("ノード数")
        for c in count_nodes():
            st.write(f"{c['label']} : {c['count']}")

        st.subheader("孤立")
        st.write(len(find_isolated_nodes()))

        st.subheader("重複")
        st.write(find_duplicate_titles())

# ==============================
# タブ
# ==============================
t1,t2,t3 = st.tabs(["一般ユーザー","管理","グラフ"])

with t1:
    user_tab()
with t2:
    admin_tab()
with t3:
    graph_tab()
