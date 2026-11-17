from unittest.mock import AsyncMock, patch

import pytest

from app.services.url_checker import URLChecker


@pytest.mark.asyncio
async def test_url_checker_reachable():
    checker = URLChecker()

    with patch.object(
        checker,
        "_is_public_host",
        new_callable=AsyncMock,
        return_value=True,
    ), patch("httpx.AsyncClient") as mock_client:
        response = AsyncMock()
        response.status_code = 200

        client_instance = mock_client.return_value.__aenter__.return_value
        client_instance.head.return_value = response

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
