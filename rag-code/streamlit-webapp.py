import streamlit as st
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime
from openai import OpenAI

# OpenAI API Key
OPENAI_API_KEY = "XXX"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Streamlit App Configuration
st.set_page_config(page_title="Learning Companion", layout="wide")

# Sidebar Navigation
page = st.sidebar.selectbox("Select a Page", ["Exercise Generator", "Chatbot"])

# ==================== PAGE 1: EXERCISE GENERATOR ====================
if page == "Exercise Generator":
    st.title("📚 AI-Powered OpenSyllabus Curriculum Generator")

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

        # Get user input
        topic = st.session_state.form_data["topic"]
        proficiency = st.session_state.form_data["proficiency"]
        time_commitment = st.session_state.form_data["time_commitment"]

        system_prompt = [
            f"The Hook: Write a three-sentence introduction about {topic} for a learner with {proficiency}% proficiency. Do not include meta-level statements about what you are returning, just the 3 sentences.",
            f"Key Concepts: List 2-4 essential concepts about {topic}, ensuring clarity for {proficiency}%.",
            f"One Must-Know Reading: Find the best single short reading (under 50 pages) about {topic}. Do not explain why you cannot find a best single piece, or if you are unsure. Just list a single reading that is recommended for the topic.",
            f"Additional Readings: Suggest 3 progressive readings about {topic}, each under 3 hours per week.",
            f"Worked Example: Provide a real-world application of {topic}, adjusted for {proficiency}% proficiency.",
            f"Interactive Exercise: Generate an interactive exercise on {topic}, matching {proficiency}% skill level."
        ]

        try:
            with st.spinner("Generating content... Please wait."):

                responses = []
                response_container = st.container()

                for i, prompt in enumerate(system_prompt):
                    kb_response = kb_client.retrieve(
                        knowledgeBaseId=knowledge_base_id,
                        retrievalQuery={"text": prompt},
                        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}}
                    )
                    retrieved_documents = kb_response.get("retrievalResults", [])
                    retrieved_texts = [doc["content"]["text"] for doc in retrieved_documents if "content" in doc]
                    knowledge_context = "\n\n".join(retrieved_texts)

                    conversation = [{"role": "user", "content": [{"text": f"Context:\n{knowledge_context}\n\n{prompt}"}]}]
                    response = brt.converse(
                        modelId=model_id,
                        messages=conversation,
                        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9}
                    )
                    response_text = response["output"]["message"]["content"][0]["text"]
                    responses.append(response_text)

                    # with response_container:
                    #     st.markdown(f"**Response {i+1}:**\n\n{response_text}")
                    with response_container:
                        match i:
                            case 0:
                                label = "📢 The Hook"
                            case 1:
                                label = "📖 Key Concepts"
                            case 2:
                                label = "📚 Must-Know Reading"
                            case 3:
                                label = "📖 Additional Readings"
                            case 4:
                                label = "🔬 Worked Example"
                            case 5:
                                label = "🎯 Interactive Exercise"
                            case _:
                                label = f"Response {i+1}"  # Fallback (just in case)

                        st.markdown(f"**{label}:**\n\n{response_text}")


                st.session_state.response_texts = responses

        except ClientError as e:
            st.error(f"AWS Bedrock request failed: {e}")
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            st.session_state.loading = False

    # User Input Fields
    topic = st.text_input("Topic:")
    proficiency = st.slider("Proficiency Level:", min_value=0, max_value=100, value=50)
    time_commitment = st.time_input("Time Commitment:")

    if st.button("Generate Exercises"):
        if not topic or time_commitment is None:
            st.error("Please fill in all fields.")
        else:
            st.session_state.form_data = {
                "topic": topic,
                "proficiency": proficiency,
                "time_commitment": time_commitment,
            }
            on_successful_submission()
            st.success("Generated exercises below!")

# ==================== PAGE 2: AI CHATBOT ====================
elif page == "Chatbot":
    st.title("💬 AI Chatbot for Learning")

    # Store chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! How can I help?"}]

    # Display chat history
    chat_placeholder = st.container()
    with chat_placeholder:
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def evaluate_user_response(user_message, assistant_message):
        """Evaluate the user's response and provide feedback."""
        rubric = """
        Evaluate the user's response based on:
        - **Accuracy**: Correctness of applied principles.
        - **Depth**: Comprehensiveness of reasoning.
        - **Clarity**: Structure and readability.
        - **Terminology**: Proper use of key terms.
        Provide feedback with a score (1-10) for each category.
        """
        prompt = f"User Message: {user_message}\nAssistant Message: {assistant_message}\n{rubric}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_follow_up(user_message, evaluation):
        """Generate a follow-up question based on the evaluation."""
        prompt = f"""
        User Message: {user_message}
        Evaluation: {evaluation}
        Generate a follow-up question based on the evaluation:
        - If the response is strong, ask a harder question.
        - If weak, ask a clarifying question.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content

    # Chat Input
    if prompt := st.chat_input("Type your message..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with chat_placeholder:
            st.chat_message("user").write(prompt)

        with st.spinner("Thinking..."):
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state["messages"]
                )
                assistant_reply = completion.choices[0].message.content
                st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
                with chat_placeholder:
                    st.chat_message("assistant").write(assistant_reply)

                # Evaluate Response
                evaluation = evaluate_user_response(prompt, assistant_reply)
                st.session_state["messages"].append({"role": "assistant", "content": evaluation})
                with chat_placeholder:
                    st.chat_message("assistant").write(f"Feedback:\n{evaluation}")

                # Generate Follow-up Question
                follow_up = generate_follow_up(prompt, evaluation)
                st.session_state["messages"].append({"role": "assistant", "content": follow_up})
                with chat_placeholder:
                    st.chat_message("assistant").write(f"Follow-Up Question:\n{follow_up}")

            except Exception as e:
                st.error(f"An error occurred: {e}")

# import streamlit as st
# import boto3
# import json
# from botocore.exceptions import ClientError
# from datetime import datetime

# # Set up the Streamlit app
# st.set_page_config(page_title="The Exercise", layout="centered")

# # st.markdown(
# #     """
# #     <style>
# #         @keyframes fire {
# #             0% { text-shadow: 0px 0px 20px orange; }
# #             50% { text-shadow: 0px 0px 30px red; }
# #             100% { text-shadow: 0px 0px 20px orange; }
# #         }

# #         .fire-text {
# #             color: white;
# #             font-size: 50px;
# #             font-weight: bold;
# #             text-align: center;
# #             animation: fire 1.5s infinite alternate;
# #         }
# #     </style>

# #     <div class="fire-text">🔥 Streamlit Fire Effect 🔥</div>
# #     """,
# #     unsafe_allow_html=True
# # )


# # st.markdown("""
# #     <style>
# #         /* Make the entire page scrollable */
# #         .main .block-container {
# #             max-height: 90vh;
# #             overflow-y: auto;
# #         }
# #         /* Make the form more narrow */
# #         .stTextInput, .stSlider, .stTimeInput, .stButton {
# #             max-width: 50%;
# #             margin: auto;
# #         }
# #     </style>
# # """, unsafe_allow_html=True)

# # Session state to store data
# if "form_data" not in st.session_state:
#     st.session_state.form_data = {}
# if "response_text" not in st.session_state:
#     st.session_state.response_text = ""
# if "loading" not in st.session_state:
#     st.session_state.loading = False

# def on_successful_submission():
#     st.session_state.loading = True
#     brt = boto3.client("bedrock-runtime")
#     kb_client = boto3.client("bedrock-agent-runtime")

#     model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
#     knowledge_base_id = "KXX0OZ3DZ4"
#     print(f"Topic: : {topic}")
#     print(f"Proficiency: : {proficiency}")
#     print(f"Time Commitment: : {time_commitment}")
#     readable_time = f"{time_commitment.hour} hours, {time_commitment.minute} minutes, {time_commitment.second} seconds"
#     print(readable_time)
#     # Format it into a readable string
#     system_prompt = [""] * 6
#     system_prompt[0] = f"The Hook: Write a three-sentence introduction that immediately captures the learner's attention about {topic}. The writing must be style—concise, vivid, and thought-provoking. Start with a striking fact, a rhetorical question, or a counterintuitive statement that makes the reader curious. The hook should clearly introduce the topic while setting up what the learner will explore next, with the user's proficiency at {proficiency}%. Don't include meta-level comments, just the 3 sentence hook."
#     system_prompt[1] = f"""Key Concepts: Identify the *2-4 essential concepts* the learner must understand about {topic}, based on {proficiency}%.  
#         - Present them as a *concise list*.
#         - Each term should be *bolded, followed by a **clear, simple definition* using everyday language.  
#         - Keep sentences *short and direct*.  
#         - Avoid jargon and ensure accessibility."""
#     system_prompt[2] = f"""One Must-Know Reading: Query the *RAG database* of top university syllabuses to find the *most essential* reading for {topic}.  
#         - The reading *must be under 50 pages* and *take no more than 30 minutes* to read.  
#         - It should be *beginner-friendly, engaging, and provide a solid foundational understanding*.  
#         - If the learner had time for *only one reading*, this should be it."""
#     system_prompt[3] = f"""Additional Readings (Three Per Week): Query the *RAG database* of top university syllabuses to find *three additional readings* that deepen the learner’s understanding of {topic}.  
#         - The total reading time *must not exceed 3 hours per week*.  
#         - If the learner is studying over multiple weeks, structure the readings as a *progressive learning plan*, like a fitness plan.  
#         - Prioritize *clarity, engagement, and a mix of perspectives*."""
#     system_prompt[4] = f"""Worked Example: Provide *one detailed worked example* that illustrates a *real-world application* of {topic}.  
#         - The example should be *adapted to {proficiency}% understanding of the topic.  
#         - Ensure it *demonstrates key concepts effectively*."""
#     system_prompt[5] = f"""Interactive Exercises*
#         Generate an *interactive exercise* based on {topic}.  
#         - Ensure the exercise *helps reinforce the key concepts*.  
#         - Adapt the *complexity based on {proficiency}% proficiency and {time_commitment}."""
#     # system_prompt = "Write a three-sentence introduction that immediately captures the learner's attention. The writing must be style—concise, vivid, and thought-provoking. Start with a striking fact, a rhetorical question, or a counterintuitive statement that makes the reader curious. The hook should clearly introduce the topic while setting up what the learner will explore next. Don't include meta-level comments, just the 3 sentence hook"
#     # try:
#     #     with st.spinner("Processing... Please wait."):
#     #         kb_response = kb_client.retrieve(
#     #             knowledgeBaseId=knowledge_base_id,
#     #             retrievalQuery={"text": system_prompt[1]},
#     #             retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}}
#     #         )
#     #         retrieved_documents = kb_response.get("retrievalResults", [])
#     #         retrieved_texts = [doc["content"]["text"] for doc in retrieved_documents if "content" in doc]
#     #         # print("Retrieved Texts:", retrieved_texts)
#     #         knowledge_context = "\n\n".join(retrieved_texts)
#     #         full_user_message = f"Context:\n{knowledge_context}\n\nQuestion: {system_prompt}"
#     #         conversation = [{"role": "user", "content": [{"text": full_user_message}]}]
#     #         response = brt.converse(
#     #             modelId=model_id,
#     #             messages=conversation,
#     #             inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9}
#     #         )
#     #         response_text = response["output"]["message"]["content"][0]["text"]
#     #         st.session_state.response_text = response_text
#     #         print("Response:", response_text)
#     try:
#         with st.spinner("Processing... Please wait."):

#             # Create a container to hold responses
#             response_container = st.container()

#             responses = []
            
#             for i, prompt in enumerate(system_prompt):  # Iterate through each prompt
#                 kb_response = kb_client.retrieve(
#                     knowledgeBaseId=knowledge_base_id,
#                     retrievalQuery={"text": prompt},
#                     retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}}
#                 )
#                 retrieved_documents = kb_response.get("retrievalResults", [])
#                 retrieved_texts = [doc["content"]["text"] for doc in retrieved_documents if "content" in doc]

#                 # Combine retrieved texts
#                 knowledge_context = "\n\n".join(retrieved_texts)
#                 full_user_message = f"Context:\n{knowledge_context}\n\nQuestion: {prompt}"

#                 # Prepare conversation message
#                 conversation = [{"role": "user", "content": [{"text": full_user_message}]}]

#                 # Send to model
#                 response = brt.converse(
#                     modelId=model_id,
#                     messages=conversation,
#                     inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9}
#                 )

#                 response_text = response["output"]["message"]["content"][0]["text"]
#                 responses.append(response_text)  # Store response

#                 # Append responses dynamically in the container
#                 with response_container:
#                     st.markdown(f"**Response {i+1}:**\n\n{response_text}")
                
#                 # Force scroll down to the latest response
#                 st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

#                 # Also print in console for debugging
#                 print(f"Response {i+1}:", response_text)

#             # Store responses in session state
#             st.session_state.response_texts = responses


#     except ClientError as e:
#         print(f"ERROR: AWS Bedrock request failed. Reason: {e}")
#     except Exception as e:
#         print(f"ERROR: {e}")
#     finally:
#         st.session_state.loading = False

# st.title("")

# disabled = st.session_state.loading

# topic = st.text_input("Topic:", disabled=disabled)
# proficiency = st.slider("Proficiency Level:", min_value=0, max_value=100, value=50, disabled=disabled)
# time_commitment = st.time_input("Time Commitment:", disabled=disabled)

# if st.button("Submit", disabled=disabled):
#     if not topic or time_commitment is None:
#         st.error("All fields are required. Please fill in all the fields.")
#     else:
#         st.session_state.form_data = {
#             "topic": topic,
#             "proficiency": proficiency,
#             "time_commitment": time_commitment,
#         }
#         on_successful_submission()
#         st.success("Data saved! See the generated response below.")

# if st.session_state.response_text:
#     st.subheader("Generated Response:")
#     st.markdown(f"""<div style='white-space: pre-wrap; word-wrap: break-word;'>{st.session_state.response_text}</div>""", unsafe_allow_html=True)
