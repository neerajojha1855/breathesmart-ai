"""Integration tests for versioned REST API endpoints."""

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_health_endpoints():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_locations_search_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/api/v1/locations/search?q=London")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert "latitude" in data[0]
            assert "longitude" in data[0]


@pytest.mark.asyncio
async def test_air_quality_current_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get(
            "/api/v1/air-quality/current?latitude=28.6139&longitude=77.2090"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "aqi" in data
        assert "pollutants" in data
        assert "pm2_5" in data["pollutants"]


@pytest.mark.asyncio
async def test_recommendations_indoor_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get(
            "/api/v1/recommendations/indoor?latitude=28.6139&longitude=77.2090"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "ventilation" in data
        assert "purification" in data
        assert "cooking_safety_checklist" in data


@pytest.mark.asyncio
async def test_sustainability_compare_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "baseline_mode": "petrol_car",
            "alternative_mode": "metro_train",
            "distance_km": 12.5,
            "trips_per_week": 10,
        }
        resp = await ac.post("/api/v1/sustainability/compare", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["weekly_co2e_saved_kg"] > 0
        assert "trees_equivalent_annual" in data


@pytest.mark.asyncio
async def test_assistant_chat_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        payload = {
            "message": "What is the recommended ventilation time for today?",
            "history": [],
        }
        resp = await ac.post("/api/v1/assistant/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data
        assert "suggested_followups" in data
