import json
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.error import HTTPError
from urllib.request import urlopen, Request
from datetime import datetime, timezone


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

        retires = 0

        while True:
            try:
                with urlopen(req) as res:
                    return HTTPResponse(res.read())
            except HTTPError as e:
                if retires >= 3:
                    print(e.headers)
                    raise e

                retires += 1

                epoch_utc = int(e.headers["x-ratelimit-reset"])
                wait_until = datetime.fromtimestamp(epoch_utc, timezone.utc)

                delay = (wait_until - datetime.now(timezone.utc)).total_seconds() + 2

                print(f"Rate limited {retires}, {delay}")
                if delay > 0:
                    time.sleep(delay)

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
