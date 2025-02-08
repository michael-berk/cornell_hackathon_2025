import boto3
import json
from botocore.exceptions import ClientError

# Initialize Amazon Bedrock clients
brt = boto3.client("bedrock-runtime")
kb_client = boto3.client("bedrock-agent-runtime")

# Set Model ID and Knowledge Base ID
model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
knowledge_base_id = "KXX0OZ3DZ4"  # Replace with your actual KB ID

# User query
user_message = """Write a three-sentence introduction that immediately captures the learner's attention. The writing must be as sharp and engaging as The Economist’s style—concise, vivid, and thought-provoking. Start with a striking fact, a rhetorical question, or a counterintuitive statement that makes the reader curious. The hook should clearly introduce the topic while setting up what the learner will explore next."""


try:
    # Step 1: Retrieve relevant knowledge from Knowledge Base
    kb_response = kb_client.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={"text": user_message},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 3  # Adjust number of retrieved docs
            }
        }
    )

    # Extract retrieved knowledge from KB response
    retrieved_documents = kb_response.get("retrievalResults", [])
    retrieved_texts = [doc["content"]["text"] for doc in retrieved_documents if "content" in doc]

    # Step 2: Format Retrieved Knowledge as Context
    knowledge_context = "\n\n".join(retrieved_texts)
    full_user_message = f"Context:\n{knowledge_context}\n\nQuestion: {user_message}"

    # Step 3: Invoke Claude 3.5 Sonnet with Retrieved Knowledge
    conversation = [
        {"role": "user", "content": [{"text": full_user_message}]}
    ]

    response = brt.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9}
    )

    # Extract response text
    response_text = response["output"]["message"]["content"][0]["text"]
    print("Response:", response_text)

except ClientError as e:
    print(f"ERROR: AWS Bedrock request failed. Reason: {e}")
except Exception as e:
    print(f"ERROR: {e}")
