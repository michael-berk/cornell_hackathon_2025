import click
import os
import mlflow

from langchain_openai import OpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from src.utils.api import resolve_openai_api_key
from src.utils.retriever import load_retriever, clean_query

# TODO: parameterize some of these with a constants file
VS_INDEX_DIRECTORY = os.path.join(os.getcwd(), "data/vs_index")


def create_chain():
    retriever = load_retriever(VS_INDEX_DIRECTORY)

    system_prompt = (
        "Return relevant products to the user query."
        "Context: {context}."
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(OpenAI(), prompt)

    return (
        RunnableLambda(lambda x: {"input": clean_query(x) if isinstance(x, str) else clean_query(x.get("input", ""))})
        | create_retrieval_chain(retriever, question_answer_chain)
    )


@click.command()
@click.option(
    "--api-key",
    required=False,
    help="Your OpenAI API key. Optional if already set as an environment variable.",
)
def log_retriever(api_key):
    resolve_openai_api_key(api_key)
    mlflow.set_experiment("RAG")

    # Create a RAG chain with simple preprocessing
    chain = create_chain()

    # Log the model
    with mlflow.start_run() as run:
        model_info = mlflow.langchain.log_model(
            chain,
            artifact_path="retrieval_qa",
            loader_fn=load_retriever,  # Preprocessing function for loading the retriever
            persist_dir=VS_INDEX_DIRECTORY,
            input_example={"input": "hi"},  # Example input for validation
            code_paths=["src"],  # Add utils for path resolution 
        )
        print(f"Model uri: {model_info.model_uri}")


if __name__ == "__main__":
    log_retriever()
