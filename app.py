from dotenv import load_dotenv


import streamlit as st
from langchain_openai import ChatOpenAI
import os

from pdf_converter.document_store import DocumentStore
from agents.rag_agent import RAGAgent
from agents.summarization_agent import SummarizationAgent
from agents.planner_agent import PlannerAgent
from agents.Specialized_agents.comparator_agent import ComparatorAgent
from agents.Specialized_agents.aggregator_agent import AggregatorAgent

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📚",
    layout="centered",
)

API_KEY = st.secrets.get["OPENAI_API_KEY"]
if not API_KEY:
    st.error("❌ Missing OPENAI_API_KEY in Streamlit cloud secrets")
    st.stop()


if "store" not in st.session_state:
    st.session_state.store = DocumentStore()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []


st.title("📚 AI Document Assistant")


st.subheader("📂 Upload PDF documents")

uploaded = st.file_uploader(
    "Upload one or more PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded:
    for file in uploaded:
        if file.name not in [f.name for f in st.session_state.uploaded_files]:
            st.session_state.uploaded_files.append(file)



to_delete = []
for idx, file in enumerate(st.session_state.uploaded_files):
    c1, c2 = st.columns([6, 1])
    c1.write(file.name)
    if c2.button("❌", key=f"del-{idx}"):
        to_delete.append(idx)

for idx in sorted(to_delete, reverse=True):
    st.session_state.uploaded_files.pop(idx)

if st.session_state.uploaded_files:
    if st.button("📥 Add to Knowledge Base"):
        # Only ingest new files
        new_files = [
            f for f in st.session_state.uploaded_files
            if f.name not in st.session_state.indexed_files
        ]

        if new_files:
            st.session_state.store.ingestion(new_files)
            st.session_state.indexed_files.extend([f.name for f in new_files])

        st.session_state.uploaded_files = []
        st.success("✨ Documents added successfully!")



if st.session_state.indexed_files:
    st.subheader("📁 Documents in Knowledge Base")
    for f in st.session_state.indexed_files:
        st.write(f"✔️ {f}")
else:
    st.info("Upload and index at least 1 PDF to continue.")


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=st.secrets["OPENAI_API_KEY"]
)


rag = RAGAgent(st.session_state.store, llm)
summ = SummarizationAgent(st.session_state.store, llm)
comp_agent = ComparatorAgent(st.session_state.store, llm)
aggregate = AggregatorAgent(st.session_state.store, llm)

planner = PlannerAgent(rag, summ,comp_agent,aggregate ,llm)


st.subheader("🗨️ Chat")

input_disabled = len(st.session_state.indexed_files) == 0

query = st.text_input(
    "Ask a question or request document summary",
    placeholder="Ex: Tell me about AI.pdf",
    disabled=input_disabled
)

if st.button("Send", disabled=input_disabled):
    if query.strip():
        # Save user
        st.session_state.chat_history.append({
            "role": "user",
            "content": query
        })

        # Get result
        response = planner.run(query)

        # Normalize planner results
        if isinstance(response, str):
            response = {"answer": response, "metadata": {}}

        st.session_state.chat_history.append({
            "role": "assistant",
            "answer": response.get("answer"),
            "metadata": response.get("metadata"),
        })



for msg in st.session_state.chat_history:

    # USER UI
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="
            text-align:right;
            background:	#eaeaea;
            padding:10px;
            color : black;
            width: fit-content;
            border-radius:10px;
            margin-bottom:6px;">
            <b>You:</b> {msg['content']}
        </div>
        """, unsafe_allow_html=True)
        continue

    # ASSISTANT UI
    st.markdown(f"""
    <div style="
        text-align:left;
        color:black;
        background:#F1F0F0;
        padding:10px;
        border-radius:10px;
        margin-bottom:6px;">
        <b>Bot:</b> {msg["answer"]}
    </div>
    """, unsafe_allow_html=True)

    # Metadata block
    meta = msg.get("metadata")
    if meta:
        st.markdown(f"""
        <div style="
            font-size:12px;
            background:#EEE;
            color : black;
            padding:6px;
            border-left:4px solid #00A2FF;
            border-radius:6px;
            margin-left: 18px;
            margin-bottom: 4px;">
            📄 <b>{meta['file_name']}</b><br>
            📑 Page: <b>{meta['page']}</b><br>
            🎯 Score: <b>{meta['score']:.4f}</b>
        </div>
        """, unsafe_allow_html=True)
