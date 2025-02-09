OPENAI_API_KEY = "XXX"
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit UI
st.set_page_config(page_title="ChatGPT Multi-Turn Chat", layout="wide")
st.title("💬 OpenAI Multi-Turn Chatbot")
st.write("Type a message and press Enter to chat!")

# Store chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! How can I help?"}]

# Display chat history dynamically
chat_placeholder = st.container()
with chat_placeholder:
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

# Function to evaluate user input
def evaluate_user_response(user_message, assistant_message):
    """Evaluate the user's response and provide feedback."""
    rubric = """
    Evaluate the user's response based on:
    - **Accuracy**: Does it correctly apply principles?
    - **Depth**: Is the reasoning comprehensive?
    - **Clarity**: Is the response structured and easy to follow?
    - **Terminology**: Are key terms used properly?

    Provide feedback with a score (1-10) for each category and explain your reasoning.
    """
    prompt = f"""
    User Message: {user_message}
    Assistant Message: {assistant_message}

    {rubric}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Replace with your preferred model
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content

# Function to generate a follow-up question
def generate_follow_up(user_message, evaluation):
    """Generate a follow-up question based on the evaluation."""
    prompt = f"""
    User Message: {user_message}
    Evaluation: {evaluation}

    Generate a follow-up question based on the evaluation:
    - If the user's response is strong, ask a harder question.
    - If the user's response is weak, ask a clarifying or easier question.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Replace with your preferred model
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content

# User input
if prompt := st.chat_input("Type your message..."):
    # Add user's message to chat history and display it
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with chat_placeholder:
        st.chat_message("user").write(prompt)

    # Generate assistant's initial reply
    with st.spinner("Thinking..."):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",  # Replace with your preferred model
                messages=st.session_state["messages"]
            )
            assistant_reply = completion.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
            with chat_placeholder:
                st.chat_message("assistant").write(assistant_reply)

            # Evaluate the user's response
            evaluation = evaluate_user_response(prompt, assistant_reply)
            st.session_state["messages"].append({"role": "assistant", "content": evaluation})
            with chat_placeholder:
                st.chat_message("assistant").write(f"Feedback:\n{evaluation}")

            # Generate a follow-up question
            follow_up = generate_follow_up(prompt, evaluation)
            st.session_state["messages"].append({"role": "assistant", "content": follow_up})
            with chat_placeholder:
                st.chat_message("assistant").write(f"Follow-Up Question:\n{follow_up}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
