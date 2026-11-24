"""Integration tests for authenticated/session-bound CRUD endpoints:
- Profile GET and PUT
- Locations POST, GET, DELETE
- Recommendations generation with session profile context
- Feedback POST
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_session_lifecycle_and_profile_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch initial profile (auto-provisions session cookie)
        resp = await ac.get("/api/v1/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["preferred_language"] == "en"
        assert "id" in data
        assert "session_id" in data

        # Check session cookie returned
        assert "breathe_smart_session" in resp.cookies
        session_cookie = resp.cookies["breathe_smart_session"]

        # 2. Update profile with custom preferences
        update_payload = {
            "preferred_language": "es",
            "household_preferences": {"hepa_purifier": True, "room_area_sqm": 35},
            "commuting_preferences": {"primary_mode": "metro_train"},
            "indoor_environment_preferences": {"natural_ventilation": True},
            "sensitive_group_consent": True,
        }
        resp_update = await ac.put(
            "/api/v1/profile",
            json=update_payload,
            cookies={"breathe_smart_session": session_cookie},
        )
        assert resp_update.status_code == 200
        updated = resp_update.json()
        assert updated["preferred_language"] == "es"
        assert updated["household_preferences"]["room_area_sqm"] == 35
        assert updated["sensitive_group_consent"] is True


@pytest.mark.asyncio
async def test_locations_crud_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Establish session
        resp_init = await ac.get("/api/v1/profile")
        session_cookie = resp_init.cookies["breathe_smart_session"]

        # 1. Save a new location
        loc_payload = {
            "city": "Paris",
            "region": "Ile-de-France",
            "country": "France",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "is_primary": True,
        }
        resp_create = await ac.post(
            "/api/v1/locations",
            json=loc_payload,
            cookies={"breathe_smart_session": session_cookie},
        )
        assert resp_create.status_code == 201
        created_loc = resp_create.json()
        assert created_loc["city"] == "Paris"
        loc_id = created_loc["id"]

        # 2. List saved locations
        resp_list = await ac.get(
            "/api/v1/locations",
            cookies={"breathe_smart_session": session_cookie},
        )
        assert resp_list.status_code == 200
        locations = resp_list.json()
        assert len(locations) >= 1
        assert any(l["id"] == loc_id for l in locations)

        # 3. Delete location
        resp_del = await ac.delete(
            f"/api/v1/locations/{loc_id}",
            cookies={"breathe_smart_session": session_cookie},
        )
        assert resp_del.status_code == 204

        # 4. Deleting non-existent location returns 404
        resp_del_404 = await ac.delete(
            f"/api/v1/locations/{uuid.uuid4()}",
            cookies={"breathe_smart_session": session_cookie},
        )
        assert resp_del_404.status_code == 404


@pytest.mark.asyncio
async def test_feedback_submission():
    from app.db.session import AsyncSessionLocal
    from app.models.recommendation import RecommendationPlan

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp_init = await ac.get("/api/v1/profile")
        session_cookie = resp_init.cookies["breathe_smart_session"]
        session_id = uuid.UUID(resp_init.json()["session_id"])

        # Insert a valid recommendation plan for this session to satisfy the FK constraint
        rec_id = uuid.uuid4()
        async with AsyncSessionLocal() as db_session:
            plan = RecommendationPlan(
                id=rec_id,
                session_id=session_id,
                ai_model="deterministic_fallback",
                recommendation_data={"summary": "Keep windows closed during peak morning inversion."},
            )
            db_session.add(plan)
            await db_session.commit()

        feedback_payload = {
            "recommendation_id": str(rec_id),
            "rating": 5,
            "feedback": "The indoor ventilation recommendation kept our room fresh without smog entry!",
        }
        resp = await ac.post(
            "/api/v1/feedback",
            json=feedback_payload,
            cookies={"breathe_smart_session": session_cookie},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["rating"] == 5
        assert "id" in data


@pytest.mark.asyncio
async def test_recommendations_generate_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/v1/recommendations/generate?latitude=28.6139&longitude=77.2090")
        assert resp.status_code == 200
        plan = resp.json()
        assert "risk_level" in plan
        assert "recommendations" in plan
        assert len(plan["recommendations"]) >= 1
