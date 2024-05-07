import streamlit as st
from linkedin_posts_scrapper import fetch_posts, make_post_data
from bytewax.testing import run_main
from flow import build as build_flow
import time
import os
from utils.embedding import EmbeddingModelSingleton, CrossEncoderModelSingleton
from utils.qdrant import build_qdrant_client
from utils.retriever import QdrantVectorDBRetriever

st.set_page_config(page_title="🎯 Real Time Linkedin Content Quest")
st.title("🎯 Real Time Linkedin Content Quest")
number_of_results_want = st.sidebar.slider("Number of results that you want to retrieve.",0,10,3)

def basic_prerequisites():
    linkedin_email = st.text_input("LinkedIn Email Address")
    linkedin_password = st.text_input("LinkedIn Password", type="password")
    linkedin_username_account = st.text_input(
        "Type in the username of the profile whose posts you'd like to get."
    )
    need_data = st.button("🧲 Fetch Details")
    if need_data:
        warn = st.warning(
            "Please keep in mind that this feature fetches data directly from LinkedIn. It might open LinkedIn in your web browser. Please avoid closing the browser while using this feature."
        )
        time.sleep(2)
        if not linkedin_email:
            st.warning("Please enter your linkedin email address for login!", icon="⚠")
        elif not linkedin_password:
            st.warning("Please enter your linkedin password for login!", icon="⚠")
        elif not linkedin_username_account:
            st.warning(
                "Please enter the linkedin username from which you want to fetch the posts!",
                icon="⚠",
            )
        else:
            account_posts_url = f"https://www.linkedin.com/in/{linkedin_username_account}/recent-activity/all/"
            all_posts = fetch_posts(
                linkedin_email, linkedin_password, account_posts_url
            )
            make_post_data(all_posts, linkedin_username_account)
            warn.empty()
            warn = st.success("Success! All posts retrieved.")
            return linkedin_username_account


def migrate_data_to_vectordb(username):
    warn = st.toast(
        "Hold on tight! We're moving data to a new system (VectorDB) to improve performance. We'll be back soon. ",
        icon="🚀",
    )
    if username:
        data_source_path = [f"data/{username}_data.json"]
    else:
        data_source_path = [f"data/{p}" for p in os.listdir("data")]
    flow = build_flow(in_memory=False, data_source_path=data_source_path)
    run_main(flow)
    warn.empty()
    warn = st.toast("We're all set! Data transfer to VectorDB is finished.", icon="🎊")


def get_insights_from_posts():
    with st.form("my_form"):
        query = st.text_area(
            "✨ Spark a Search:",
            f"",
        )
        submitted = st.form_submit_button("Submit Query")
        if submitted:
            embedding_model = EmbeddingModelSingleton()
            cross_encode_model = CrossEncoderModelSingleton()
            qdrant_client = build_qdrant_client()
            vectordb_retriever = QdrantVectorDBRetriever(
                embedding_model=embedding_model,
                cross_encoder_model=cross_encode_model,
                vector_db_client=qdrant_client,
            )
            # st.toast("Query Seach is in Progress. Please wait...", icon="⏳")
            with  st.spinner("⏳Query Search is in Progress. Please wait..."):
                retrieved_results = vectordb_retriever.search(
                    query, limit=number_of_results_want, return_all=True
                )
            st.toast("Query Search is completed. You can now view the results.", icon="⌛")
            for index, post in enumerate(retrieved_results["posts"]):
                with st.expander(f"📌 Result-{index+1}"):
                    st.subheader(f"PostID: {post.post_id}")
                    st.markdown(f"**Post Owner**: {post.post_owner}")
                    st.markdown(f"**Source**: {post.source}")
                    st.markdown(f"**Similarity Score**: {post.score}")
                    st.caption("Raw Text of Post:-")
                    st.write(f"{post.full_raw_text}")


if __name__ == "__main__":
    username = None
    with st.expander("💡 Unlock LinkedIn Insights"):
        username = basic_prerequisites()
    with st.expander("🛠️ Data Ingestion to VectorDB"):
        migrate_data = st.button("🔨 Data Ingestion")
        if migrate_data:
            migrate_data_to_vectordb(username)
    get_insights_from_posts()
