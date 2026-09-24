import sys
from pathlib import Path

import streamlit as st

BACKEND_DIR = Path(__file__).parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.cafe_data import CAFE_DATA
from app.services.conversation_manager import ConversationManager
from app.services.transformer_model import CafeAdvisorModel


st.set_page_config(
    page_title="CafeAI Chatbot",
    page_icon="☕",
    layout="centered",
)

st.title("CafeAI Coffee House")
st.caption("Ask about our menu, prices, ingredients, recommendations, and opening hours.")

if "manager" not in st.session_state:
    st.session_state.manager = ConversationManager()
    st.session_state.conversation_id = st.session_state.manager.create_conversation()

if "advisor" not in st.session_state:
    st.session_state.advisor = CafeAdvisorModel()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Cafe details")
    st.write(CAFE_DATA["location"])
    st.write("**Today's menu highlights**")
    for item in CAFE_DATA["menu"]:
        if item["popular"]:
            st.write(f"{item['name']} - ${item['price']:.2f}")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.manager = ConversationManager()
        st.session_state.conversation_id = st.session_state.manager.create_conversation()
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What would you like to know about the cafe?")
if prompt:
    conversation_id = st.session_state.conversation_id
    manager = st.session_state.manager
    advisor = st.session_state.advisor

    manager.add_message(conversation_id, "user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = advisor.generate_response(manager.get_messages(conversation_id))
        st.markdown(response)

    manager.add_message(conversation_id, "assistant", response)
    st.session_state.messages.append({"role": "assistant", "content": response})
