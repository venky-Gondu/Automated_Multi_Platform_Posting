from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.url_checker import URLChecker


@pytest.mark.asyncio
async def test_url_checker_reachable():
    checker = URLChecker()

    with (
        patch.object(
            checker,
            "_is_public_host",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("app.services.url_checker.httpx.AsyncClient") as mock_client,
    ):
        response = httpx.Response(
            200,
            request=httpx.Request("HEAD", "https://example.com"),
        )

        client_instance = mock_client.return_value.__aenter__.return_value
        client_instance.head = AsyncMock(return_value=response)

        result = await checker.check("https://example.com")

        assert result.status == "reachable"
        assert result.warning is None


@pytest.mark.asyncio
async def test_url_checker_rejects_private_host():
    checker = URLChecker()

    with patch.object(
        checker,
        "_is_public_host",
        new_callable=AsyncMock,
        return_value=False,
    ):
        result = await checker.check("http://localhost")

        assert result.status == "unreachable"
        assert result.warning is not None


@pytest.mark.asyncio
async def test_url_checker_rejects_missing_hostname():
    result = await URLChecker().check("not-a-valid-url")

    assert result.status == "unreachable"
    assert result.url == "not-a-valid-url"
    assert result.warning is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [404, 500, 503])
async def test_url_checker_returns_http_error(status_code):
    checker = URLChecker()

    with (
        patch.object(
            checker,
            "_is_public_host",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("app.services.url_checker.httpx.AsyncClient") as mock_client,
    ):
        response = httpx.Response(
            status_code,
            request=httpx.Request("HEAD", "https://example.com"),
        )

        client_instance = mock_client.return_value.__aenter__.return_value
        client_instance.head = AsyncMock(return_value=response)

        result = await checker.check("https://example.com")

        assert result.status == "unreachable"
        assert result.warning == f"URL returned HTTP {status_code}."


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [405, 501])
async def test_url_checker_retries_with_get(status_code):
    checker = URLChecker()

    with (
        patch.object(
            checker,
            "_is_public_host",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("app.services.url_checker.httpx.AsyncClient") as mock_client,
    ):
        head_response = httpx.Response(
            status_code,
            request=httpx.Request("HEAD", "https://example.com"),
        )

        get_response = httpx.Response(
            200,
            request=httpx.Request("GET", "https://example.com"),
        )

        client_instance = mock_client.return_value.__aenter__.return_value
        client_instance.head = AsyncMock(return_value=head_response)

        get_stream = AsyncMock()
        get_stream.__aenter__.return_value = get_response
        get_stream.__aexit__.return_value = None
        client_instance.stream = MagicMock(return_value=get_stream)

        result = await checker.check("https://example.com")

        assert result.status == "reachable"
        assert result.warning is None
        client_instance.stream.assert_called_once_with(
            "GET",
            "https://example.com",
        )


@pytest.mark.asyncio
async def test_url_checker_times_out():
    checker = URLChecker()

    with (
        patch.object(
            checker,
            "_is_public_host",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("app.services.url_checker.httpx.AsyncClient") as mock_client,
    ):
        client_instance = mock_client.return_value.__aenter__.return_value
        client_instance.head.side_effect = httpx.TimeoutException(
            "Request timed out",
        )

        result = await checker.check("https://example.com")

        assert result.status == "unknown"
        assert result.warning == "URL availability check timed out."


@pytest.mark.asyncio
async def test_url_checker_request_error():
    checker = URLChecker()

    with (
        patch.object(
            checker,
            "_is_public_host",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("app.services.url_checker.httpx.AsyncClient") as mock_client,
    ):
        client_instance = mock_client.return_value.__aenter__.return_value
        client_instance.head.side_effect = httpx.ConnectError(
            "Unable to connect",
        )

        result = await checker.check("https://example.com")

        assert result.status == "unknown"
        assert result.warning == "Unable to connect to the URL."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "http://",
        "https://",
        "http://[::1",
    ],
)
async def test_url_checker_rejects_invalid_urls(url):
    result = await URLChecker().check(url)

    assert result.url == url
    assert result.status == "unreachable"
    assert result.warning is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("url", ["ftp://example.com", "file:///tmp/test.txt"])
async def test_url_checker_rejects_unsupported_schemes(url):
    result = await URLChecker().check(url)

    assert result.url == url
    assert result.status == "unreachable"
    assert result.warning is not None


@pytest.mark.asyncio
async def test_url_checker_handles_invalid_url_request():
    checker = URLChecker()

    with (
        patch.object(
            checker,
            "_is_public_host",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch("app.services.url_checker.httpx.AsyncClient") as mock_client,
    ):
        client_instance = mock_client.return_value.__aenter__.return_value
        client_instance.head.side_effect = httpx.InvalidURL("Invalid URL")

        result = await checker.check("https://example.com")

    assert result.status == "unknown"
    assert result.warning == "Invalid URL."

