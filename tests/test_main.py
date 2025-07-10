import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_flag_happy_path():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/", params={"q": "Canada"})
        assert resp.status_code == 200
        assert "Canada" in resp.text
        assert "flagcdn.com/ca.svg" in resp.text


@pytest.mark.asyncio
async def test_flag_error_path():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/", params={"q": "Atlantis"})
        assert resp.status_code == 200
        assert "not found" in resp.text.lower()
