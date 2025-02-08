from typing import Generator

from datasets import load_dataset

N = 100
DEFAULT_METADATA_KEYS = {
    "average_rating",
    "rating_number",
    "price",
    "details",
    "parent_asin",
    "title",
    "features",
    "description",
}


def get_top_n_rows(path: str, name: str, n: int = N) -> Generator:
    """
    Retrieves the top `n` rows from a dataset.

    This is dummy method that demonstrates ingestion from a source.

    Args:
        path (str): The file path to the dataset.
        name (str): The name of the dataset.
        n (int): The number of rows to retrieve.

    Yields:
        Generator: A generator that yields the top `n` rows from the dataset.
    """
    dataset = load_dataset(path, name, streaming=True, trust_remote_code=True)["full"]

    # Sample first `n` rows
    for i, row in enumerate(dataset):
        if i == n:
            break

        yield row


def create_page_content(row: dict) -> str:
    return_value = ""
    for k in ["title", "features", "description"]:
        if value := row.get(k):
            return_value += f"{k.capitalize()}: {value}\n"
    return return_value


def create_metadata(row: dict, metadata_keys_to_keep: set = DEFAULT_METADATA_KEYS) -> str:
    return {k: v for k, v in row.items() if k in metadata_keys_to_keep and v}
