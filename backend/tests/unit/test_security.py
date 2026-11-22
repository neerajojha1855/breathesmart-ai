from app.core.security import (
    generate_csrf_token,
    generate_session_token,
    get_cookie_settings,
    hash_token,
    verify_csrf_token,
    verify_token_hash,
)


def test_session_token_entropy_and_format():
    t1 = generate_session_token()
    t2 = generate_session_token()
    assert t1 != t2
    assert len(t1) >= 40

def test_token_hashing_and_verification():
    token = generate_session_token()
    h = hash_token(token)
    assert len(h) == 64
    assert verify_token_hash(token, h) is True
    assert verify_token_hash("tampered_token", h) is False


def test_csrf_generation_and_validation():
    csrf = generate_csrf_token()
    assert len(csrf) == 64
    assert verify_csrf_token(csrf, csrf) is True
    assert verify_csrf_token(csrf, "wrong_token") is False
    assert verify_csrf_token(None, csrf) is False
    assert verify_csrf_token(csrf, None) is False


def test_cookie_settings():
    cookie_cfg = get_cookie_settings()
    assert cookie_cfg["httponly"] is True
    assert cookie_cfg["samesite"] == "lax"
    assert "max_age" in cookie_cfg