import json
import random
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.error import HTTPError
from urllib.request import urlopen, Request


class HTTPResponse:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def text(self) -> str:
        return self.body.decode()

    def json(self) -> dict:
        return json.loads(self.body.decode())


@dataclass
class RequestOptions:
    url: str
    method: str = "GET"
    headers: dict = field(default_factory=dict)
    query_params: Optional[dict] = None
    body: Optional[bytes] = None


class HTTPClient:
    MAX_5XX_RETRIES = 3
    INITIAL_RETRY_DELAY_SECONDS = 1.0

    def __init__(
        self, base_url: Optional[str] = None, base_headers: Optional[dict] = None
    ) -> None:
        self.base_url = base_url
        self.base_headers = base_headers

    def request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        query_params: Optional[dict] = None,
        body: Optional[bytes] = None,
    ) -> HTTPResponse:
        if self.base_url:
            url = self.base_url + url

        _headers = {}
        if self.base_headers:
            _headers = _headers | self.base_headers
        if headers:
            _headers = _headers | headers

        if query_params:
            url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items()])

        req = Request(
            url,
            method=method,
            headers=_headers,
            data=body,
        )

        retries = 0
        while True:
            try:
                with urlopen(req) as res:
                    return HTTPResponse(res.read())
            except HTTPError as error:
                if not self._is_retryable_5xx(error):
                    raise error

                if retries >= self.MAX_5XX_RETRIES:
                    raise error

                time.sleep(self._retry_delay_seconds(retries))
                retries += 1

    def _is_retryable_5xx(self, error: HTTPError) -> bool:
        return 500 <= error.code <= 599

    def _retry_delay_seconds(self, retries: int) -> float:
        base_delay = self.INITIAL_RETRY_DELAY_SECONDS * (2**retries)
        return random.uniform(0, base_delay)

    def get(
        self,
        url: str,
        headers: Optional[dict] = None,
        query_params: Optional[dict] = None,
        body: Optional[bytes] = None,
    ) -> HTTPResponse:
        return self.request(
            url, method="GET", headers=headers, query_params=query_params, body=body
        )

    def post(
        self,
        url: str,
        headers: Optional[dict] = None,
        query_params: Optional[dict] = None,
        body: Optional[bytes] = None,
    ) -> HTTPResponse:
        return self.request(
            url, method="POST", headers=headers, query_params=query_params, body=body
        )
