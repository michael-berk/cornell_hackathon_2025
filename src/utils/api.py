import os
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_fixed

MAX_RETRIES: int = 3
WAIT_SECONDS: int = 2


def resolve_openai_api_key(api_key: Optional[str] = None) -> None:
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    elif not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "API key is required. Please provide it as an argument or set it as an environment variable."
        )


class APIRequestHelper:
    """
    This class facilitates
    1. Passing parameters instead of using functools.partial.
    2. Retrying API requests.
    """

    def __init__(self, base_url: str, default_headers: str = {}, default_params: str = {}):
        self.base_url = base_url
        self.default_headers = default_headers
        self.default_params = default_params

    @retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(WAIT_SECONDS))
    def request_api(
        self,
        method: str = "GET",
        headers: Optional[dict] = None,
        params_dict: Optional[dict] = None,
    ) -> requests.Response:
        if params_dict is None:
            params_dict = {}
        if headers is None:
            headers = {}

        headers = self.default_headers | headers
        params_dict = self.default_params | params_dict

        response = requests.request(method, self.base_url, headers=headers, json=params_dict)
        response.raise_for_status()
        return response
