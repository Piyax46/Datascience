import streamlit as st
from chatbot import AgnosChatbot
from recommender import SymptomRecommender
import json

st.set_page_config(page_title="Agnos AI Assistant", page_icon="🏥")

st.title("🏥 Agnos AI Assistant")

tab1, tab2 = st.tabs(["Symptom Recommender", "Health Forum Chatbot (RAG)"])

with tab1:
    st.header("Symptom Recommender")
    st.write("Recommend the next possible symptom based on historical data.")
    
    # Input
    gender = st.selectbox("Gender", ["male", "female"], index=0)
    age = st.number_input("Age", min_value=0, max_value=120, value=26)
    symptom_input = st.text_input("Enter current symptoms (comma separated)", "ท้องเสีย")
    
    if st.button("Get Recommendations"):
        current_symptoms = [s.strip() for s in symptom_input.split(',')]
        recommender = SymptomRecommender('processed_data.json')
        recommendations = recommender.recommend(current_symptoms, gender=gender, age=age)
        
        st.subheader("Recommended Symptoms:")
        for r in recommendations:
            st.write(f"- {r}")

with tab2:
    st.header("Agnos Forum Chatbot")
    st.write("Ask questions and get answers from Agnos Health Forum data.")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            chatbot = AgnosChatbot('forum_data.json')
            response = chatbot.generate_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
