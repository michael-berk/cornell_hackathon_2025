import re

def clean_query(query: str):
    """Remove special characters and extra spaces."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", query).strip()
