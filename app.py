import streamlit as st
from domain_detector import detect_domain
from prompt import build_prompt

# Load knowledge base
def load_knowledge():
    with open("knowledge_base/ethics_docs.txt", "r") as f:
        return f.read()

knowledge = load_knowledge()

st.title("AI Ethics Chatbot")

user_input = st.text_input("Ask your question:")

if user_input:
    # Step 1: detect domain
    domain = detect_domain(user_input)

    # Step 2: simple retrieval (basic matching)
    context = ""
    for line in knowledge.split("\n"):
        if any(word in line.lower() for word in user_input.lower().split()):
            context += line + "\n"

    # Step 3: build response (no API, simulated)
    if context == "":
        context = "General AI ethics principles apply."

    response = f"""
Answer:
Based on {domain}, {context}

Explanation:
This recommendation ensures ethical AI practices like fairness and transparency.

Ethical Principle:
Fairness / Transparency
"""

    st.write(response)