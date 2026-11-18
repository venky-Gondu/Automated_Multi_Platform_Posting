import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit

import httpx

from app.schemas.response import URLCheckResult


class URLChecker:

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    async def _is_public_host(self, hostname: str) -> bool:
        try:
            try:
                addresses = [ipaddress.ip_address(hostname)]
            except ValueError:
                records = await asyncio.to_thread(
                    socket.getaddrinfo,
                    hostname,
                    None,
                    type=socket.SOCK_STREAM
                )
                addresses = [
                    ipaddress.ip_address(record[4][0])
                    for record in records
                ]

            return bool(addresses) and all(
                address.is_global for address in addresses
            )

        except (OSError, ValueError):
            return False

    async def check(self, url: str) -> URLCheckResult:
        try:
            parsed_url = urlsplit(url)
            hostname = parsed_url.hostname
        except ValueError:
            return URLCheckResult(
                url=url,
                status="unreachable",
                warning="URL is invalid.",
            )

        if (
            parsed_url.scheme not in {"http", "https"}
            or not hostname
            or not await self._is_public_host(hostname)
        ):
            return URLCheckResult(
                url=url,
                status="unreachable",
                warning="URL is invalid or does not resolve to a public address.",
            )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=False,
            ) as client:
                response = await client.head(url)

                if response.status_code in (405, 501):
                    async with client.stream("GET", url) as response:
                        pass

                if 200 <= response.status_code < 400:
                    return URLCheckResult(
                        url=url,
                        status="reachable",
                        warning=None,
                    )

                return URLCheckResult(
                    url=url,
                    status="unreachable",
                    warning=f"URL returned HTTP {response.status_code}.",
                )

        except httpx.TimeoutException:
            return URLCheckResult(
                url=url,
                status="unknown",
                warning="URL availability check timed out.",
            )
        except httpx.InvalidURL:
            return URLCheckResult(
                url=url,
                status="unknown",
                warning="Invalid URL.",
            )
        except httpx.RequestError:
            return URLCheckResult(
                url=url,
                status="unknown",
                warning="Unable to connect to the URL.",
            )
