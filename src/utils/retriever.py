import re

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def clean_query(query: str):
    """Remove special characters and extra spaces."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", query).strip()


def load_retriever(persist_directory: str):
    return FAISS.load_local(
        persist_directory,
        OpenAIEmbeddings(),
        allow_dangerous_deserialization=True,
    ).as_retriever()
