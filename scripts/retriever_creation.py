import click
import os
import mlflow

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_aws.retrievers import AmazonKnowledgeBasesRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.llms import Bedrock

# AWS Bedrock environment configuration
os.environ["AWS_PROFILE"] = "default"  # Your AWS CLI profile
os.environ["AWS_REGION"] = "us-west-2"  # AWS region where Bedrock is available

# Amazon Knowledge Base ID
KNOWLEDGE_BASE_ID = "your-knowledge-base-id"  # Replace with your knowledge base ID


def create_chain():
    # Configure the AWS Bedrock Retriever
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id=KNOWLEDGE_BASE_ID,
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
    )

    # System and user prompt configuration
    system_prompt = (
        "Return relevant information from the knowledge base based on the user query."
        "Context: {context}."
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # Configure Bedrock LLM
    bedrock_llm = Bedrock(
        model_id="anthropic.claude-v2",  # Replace with your desired model
        region_name="us-west-2"
    )

    # Create the question-answer chain
    question_answer_chain = create_stuff_documents_chain(bedrock_llm, prompt)

    # Combine query cleaning and retrieval chain
    return (
        RunnableLambda(lambda x: {"input": x.strip() if isinstance(x, str) else x.get("input", "").strip()})
        | create_retrieval_chain(retriever, question_answer_chain)
    )


@click.command()
def log_retriever():
    mlflow.set_experiment("RAG")  # Log experiment in MLflow

    # Define loader_fn to recreate the retriever
    def loader_fn(dir):
        return AmazonKnowledgeBasesRetriever(
            knowledge_base_id=KNOWLEDGE_BASE_ID,
            retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
        )

    # Create RAG chain with Bedrock and Amazon Knowledge Base Retriever
    chain = create_chain()

    # Log the model with the loader function
    with mlflow.start_run() as run:
        model_info = mlflow.langchain.log_model(
            chain,
            artifact_path="retrieval_qa",
            loader_fn=loader_fn,  # Provide the loader function for the retriever
            input_example={"input": "hi"},  # Example input for validation
        )
        print(f"Model URI: {model_info.model_uri}")


if __name__ == "__main__":
    log_retriever()
