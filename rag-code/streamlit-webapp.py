import streamlit as st

# Set up the Streamlit app
st.set_page_config(page_title="User Data Form", layout="centered")

# Define pages
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Form", "Results"])

# Session state to store data
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

def on_successful_submission():
    """
    Wrapper function to be called when the user successfully submits the form.
    """
    pass

if page == "Form":
    st.title("User Data Form")
    
    # Topic Input
    topic = st.text_input("Topic:")
    
    # Proficiency Level Slider
    proficiency = st.slider("Proficiency Level:", min_value=0, max_value=100, value=50)
    
    # Time Commitment Input
    time_commitment = st.time_input("Time Commitment:")
    
    if st.button("Submit"):
        if not topic or time_commitment is None:
            st.error("All fields are required. Please fill in all the fields.")
        else:
            st.session_state.form_data = {
                "topic": topic,
                "proficiency": proficiency,
                "time_commitment": time_commitment,
            }
            on_successful_submission()
            st.success("Data saved! Navigate to the 'Results' page to view.")

elif page == "Results":
    st.title("Collected Data")
    if st.session_state.form_data:
        st.write(f"**Topic:** {st.session_state.form_data['topic']}")
        st.write(f"**Proficiency Level:** {st.session_state.form_data['proficiency']}")
        st.write(f"**Time Commitment:** {st.session_state.form_data['time_commitment']}")
    else:
        st.write("No data available. Please fill out the form first.")
