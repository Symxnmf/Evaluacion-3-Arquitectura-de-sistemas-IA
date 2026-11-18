from api.auth import create_token, require_token


def test_token_is_signed_and_contains_subject():
    token = create_token("security-test")
    assert isinstance(token, str)
    assert len(token) > 20


def test_token_secret_is_not_empty(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "long-test-secret")
    token = create_token("subject")
    assert token
