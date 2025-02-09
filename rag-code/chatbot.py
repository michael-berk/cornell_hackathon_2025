OPENAI_API_KEY = "XXX"  # Replace with your OpenAI key
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit UI
st.set_page_config(page_title="ChatGPT Demo", layout="wide")
st.title("💬 OpenAI Chatbot with Turn-Based Updates")
st.write("Type a message and press Enter to chat!")

# Store chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! How can I help?"}]

# Display chat history dynamically
chat_placeholder = st.container()
with chat_placeholder:
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    # Add user's message to chat history and display it
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with chat_placeholder:
        st.chat_message("user").write(prompt)

    # Generate assistant's reply
    with st.spinner("Thinking..."):
        try:
            # Call OpenAI API
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Replace with your preferred model
                messages=st.session_state["messages"]
            )
            # Extract assistant's reply
            reply = completion.choices[0].message.content
            # Add reply to chat history and display it
            st.session_state["messages"].append({"role": "assistant", "content": reply})
            with chat_placeholder:
                st.chat_message("assistant").write(reply)
        except Exception as e:
            st.error(f"An error occurred: {e}")
