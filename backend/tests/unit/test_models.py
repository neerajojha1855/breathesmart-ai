import uuid
from datetime import datetime, timedelta, timezone
from app.models.feedback import UserFeedback
from app.models.location import SavedLocation
from app.models.profile import UserProfile
from app.models.session import UserSession


def test_user_session_instantiation():
    now = datetime.now(timezone.utc)
    sess = UserSession(
        token_hash="a" * 64,
        expires_at=now + timedelta(days=1),
    )
    assert sess.token_hash == "a" * 64
    assert sess.expires_at > now


def test_user_profile_defaults():
    prof = UserProfile(
        session_id=uuid.uuid4(),
        preferred_language="en",
        household_preferences={"has_purifier": True},
        commuting_preferences={"primary_mode": "metro"},
        indoor_environment_preferences={"cook_fuel": "induction"},
    )
    assert prof.preferred_language == "en"
    assert prof.sensitive_group_consent is False
    assert prof.household_preferences["has_purifier"] is True


def test_feedback_rating_fields():
    fb = UserFeedback(
        session_id=uuid.uuid4(),
        recommendation_id=uuid.uuid4(),
        rating=5,
        feedback="Extremely helpful window opening schedule!",
    )
    assert fb.rating == 5
    assert "window" in (fb.feedback or "")
