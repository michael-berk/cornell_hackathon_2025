import streamlit as st
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime

# Set up the Streamlit app
st.set_page_config(page_title="User Data Form", layout="centered")

# st.markdown("""
#     <style>
#         /* Make the entire page scrollable */
#         .main .block-container {
#             max-height: 90vh;
#             overflow-y: auto;
#         }
#         /* Make the form more narrow */
#         .stTextInput, .stSlider, .stTimeInput, .stButton {
#             max-width: 50%;
#             margin: auto;
#         }
#     </style>
# """, unsafe_allow_html=True)

# Session state to store data
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "response_text" not in st.session_state:
    st.session_state.response_text = ""
if "loading" not in st.session_state:
    st.session_state.loading = False

def on_successful_submission():
    st.session_state.loading = True
    brt = boto3.client("bedrock-runtime")
    kb_client = boto3.client("bedrock-agent-runtime")

    model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    knowledge_base_id = "KXX0OZ3DZ4"
    print(f"Topic: : {topic}")
    print(f"Proficiency: : {proficiency}")
    print(f"Time Commitment: : {time_commitment}")
    readable_time = f"{time_commitment.hour} hours, {time_commitment.minute} minutes, {time_commitment.second} seconds"
    print(readable_time)
    # Format it into a readable string
    system_prompt = [""] * 6
    system_prompt[0] = f"The Hook: Write a three-sentence introduction that immediately captures the learner's attention about {topic}. The writing must be style—concise, vivid, and thought-provoking. Start with a striking fact, a rhetorical question, or a counterintuitive statement that makes the reader curious. The hook should clearly introduce the topic while setting up what the learner will explore next, with the user's proficiency at {proficiency}%. Don't include meta-level comments, just the 3 sentence hook."
    system_prompt[1] = f"""Key Concepts: Identify the *2-4 essential concepts* the learner must understand about {topic}, based on {proficiency}%.  
        - Present them as a *concise list*.
        - Each term should be *bolded, followed by a **clear, simple definition* using everyday language.  
        - Keep sentences *short and direct*.  
        - Avoid jargon and ensure accessibility."""
    system_prompt[2] = f"""One Must-Know Reading: Query the *RAG database* of top university syllabuses to find the *most essential* reading for {topic}.  
        - The reading *must be under 50 pages* and *take no more than 30 minutes* to read.  
        - It should be *beginner-friendly, engaging, and provide a solid foundational understanding*.  
        - If the learner had time for *only one reading*, this should be it."""
    system_prompt[3] = f"""Additional Readings (Three Per Week): Query the *RAG database* of top university syllabuses to find *three additional readings* that deepen the learner’s understanding of {topic}.  
        - The total reading time *must not exceed 3 hours per week*.  
        - If the learner is studying over multiple weeks, structure the readings as a *progressive learning plan*, like a fitness plan.  
        - Prioritize *clarity, engagement, and a mix of perspectives*."""
    system_prompt[4] = f"""Worked Example: Provide *one detailed worked example* that illustrates a *real-world application* of {topic}.  
        - The example should be *adapted to {proficiency}% understanding of the topic.  
        - Ensure it *demonstrates key concepts effectively*."""
    system_prompt[5] = f"""Interactive Exercises*
        Generate an *interactive exercise* based on {topic}.  
        - Ensure the exercise *helps reinforce the key concepts*.  
        - Adapt the *complexity based on {proficiency}% proficiency and {time_commitment}."""
    # system_prompt = "Write a three-sentence introduction that immediately captures the learner's attention. The writing must be style—concise, vivid, and thought-provoking. Start with a striking fact, a rhetorical question, or a counterintuitive statement that makes the reader curious. The hook should clearly introduce the topic while setting up what the learner will explore next. Don't include meta-level comments, just the 3 sentence hook"
    # try:
    #     with st.spinner("Processing... Please wait."):
    #         kb_response = kb_client.retrieve(
    #             knowledgeBaseId=knowledge_base_id,
    #             retrievalQuery={"text": system_prompt[1]},
    #             retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}}
    #         )
    #         retrieved_documents = kb_response.get("retrievalResults", [])
    #         retrieved_texts = [doc["content"]["text"] for doc in retrieved_documents if "content" in doc]
    #         # print("Retrieved Texts:", retrieved_texts)
    #         knowledge_context = "\n\n".join(retrieved_texts)
    #         full_user_message = f"Context:\n{knowledge_context}\n\nQuestion: {system_prompt}"
    #         conversation = [{"role": "user", "content": [{"text": full_user_message}]}]
    #         response = brt.converse(
    #             modelId=model_id,
    #             messages=conversation,
    #             inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9}
    #         )
    #         response_text = response["output"]["message"]["content"][0]["text"]
    #         st.session_state.response_text = response_text
    #         print("Response:", response_text)
    try:
        with st.spinner("Processing... Please wait."):

            # Create a container to hold responses
            response_container = st.container()

            responses = []
            
            for i, prompt in enumerate(system_prompt):  # Iterate through each prompt
                kb_response = kb_client.retrieve(
                    knowledgeBaseId=knowledge_base_id,
                    retrievalQuery={"text": prompt},
                    retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}}
                )
                retrieved_documents = kb_response.get("retrievalResults", [])
                retrieved_texts = [doc["content"]["text"] for doc in retrieved_documents if "content" in doc]

                # Combine retrieved texts
                knowledge_context = "\n\n".join(retrieved_texts)
                full_user_message = f"Context:\n{knowledge_context}\n\nQuestion: {prompt}"

                # Prepare conversation message
                conversation = [{"role": "user", "content": [{"text": full_user_message}]}]

                # Send to model
                response = brt.converse(
                    modelId=model_id,
                    messages=conversation,
                    inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9}
                )

                response_text = response["output"]["message"]["content"][0]["text"]
                responses.append(response_text)  # Store response

                # Append responses dynamically in the container
                with response_container:
                    st.markdown(f"**Response {i+1}:**\n\n{response_text}")
                
                # Force scroll down to the latest response
                st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

                # Also print in console for debugging
                print(f"Response {i+1}:", response_text)

            # Store responses in session state
            st.session_state.response_texts = responses


    except ClientError as e:
        print(f"ERROR: AWS Bedrock request failed. Reason: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        st.session_state.loading = False

st.title("User Data Form")

disabled = st.session_state.loading

topic = st.text_input("Topic:", disabled=disabled)
proficiency = st.slider("Proficiency Level:", min_value=0, max_value=100, value=50, disabled=disabled)
time_commitment = st.time_input("Time Commitment:", disabled=disabled)

if st.button("Submit", disabled=disabled):
    if not topic or time_commitment is None:
        st.error("All fields are required. Please fill in all the fields.")
    else:
        st.session_state.form_data = {
            "topic": topic,
            "proficiency": proficiency,
            "time_commitment": time_commitment,
        }
        on_successful_submission()
        st.success("Data saved! See the generated response below.")

if st.session_state.response_text:
    st.subheader("Generated Response:")
    st.markdown(f"""<div style='white-space: pre-wrap; word-wrap: break-word;'>{st.session_state.response_text}</div>""", unsafe_allow_html=True)
