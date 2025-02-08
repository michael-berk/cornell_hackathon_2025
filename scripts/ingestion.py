import concurrent.futures
import os
from typing import Callable

import click
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.utils.api import APIRequestHelper, resolve_openai_api_key
from src.utils.ingestion import create_metadata, create_page_content, get_top_n_rows

# TODO: parameterize some of these with a constants file
VS_INDEX_DIRECTORY = os.path.join(os.getcwd(), "data/vs_index")
DATASET_NAME = "McAuley-Lab/Amazon-Reviews-2023"
SPLIT_NAME = "raw_meta_Amazon_Fashion"
N = 100

EMBEDDING_MODEL = "text-embedding-3-small"


def _create_embedding_callable() -> Callable:
    api_request_helper = APIRequestHelper(
        base_url="https://api.openai.com/v1/embeddings",
        default_headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        default_params={"model": EMBEDDING_MODEL},
    )

    # Define function to parallelize
    def _get_embedings(input_text: str) -> list:
        response = api_request_helper.request_api(method="POST", params_dict={"input": input_text})
        data = response.json().get("data", [])
        if not data:
            raise ValueError(f"No embeddings returned for input: {input_text}")
        return data[0]["embedding"]

    return _get_embedings


@click.command()
@click.option(
    "--api-key",
    required=False,
    help="Your OpenAI API key. Optional if already set as an environment variable.",
)
@click.option(
    "--ingestion_method",
    required=False,
    help="Method run API calls. The include `single_machine`, `spark`, and `batch_api`.",
)
def run_ingestion(api_key, ingestion_method):
    # Step 1: Validate
    resolve_openai_api_key(api_key)

    if ingestion_method not in {"single_machine", "spark", "batch_api"}:
        raise ValueError(
            "Invalid ingestion method. Please choose from `single_machine`, `spark`, and `batch_api`."
        )

    # Step 2: Get text to embed
    # TODO: this would be replaced with a database read
    dataset = list(get_top_n_rows(DATASET_NAME, SPLIT_NAME, N))
    texts = [create_page_content(row) for row in dataset]

    # Step 3: Calculate embeddings
    embedding_callable = _create_embedding_callable()

    if ingestion_method == "single_machine":
        with concurrent.futures.ThreadPoolExecutor() as executor:
            embeddings = list(executor.map(embedding_callable, texts))  # Already flat

    else:
        # TODO
        raise NotImplementedError(
            "Ingestion method not implemented. See ~/.archive/api_calls.ipynb for example implemenetations."
        )

    # Step 3: Parse metadata
    metadata = [create_metadata(row) for row in dataset]

    # Step 4: Write to a vector store index
    db = FAISS.from_embeddings(
        text_embeddings=list(zip(texts, embeddings)),
        embedding=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        metadatas=metadata
    )


    if not os.path.exists(VS_INDEX_DIRECTORY):
        os.makedirs(VS_INDEX_DIRECTORY)
    db.save_local(VS_INDEX_DIRECTORY)


if __name__ == "__main__":
    run_ingestion()
