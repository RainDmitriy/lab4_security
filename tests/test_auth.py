import pytest
import httpx
import os

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")

@pytest.mark.asyncio
async def test_register_success():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        payload = {"login": "sakuradata", "password": "Th3_d@rk3r_th3_n1ght_th3_br1ght3r_th3_st@rs"}
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 200
        assert "id" in response.json()

@pytest.mark.asyncio
async def test_register_duplicate_login():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        payload = {"login": "sakuradata", "password": "When_s@kura_bl0ss0ms"}
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409

@pytest.mark.asyncio
async def test_register_unprocessable_password():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        payload = {"login": "newuser", "password": "123"}  # слабый пароль
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 422
