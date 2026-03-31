from corejunkie_app.security import hash_password, make_session_token, parse_session_token, verify_password


def test_password_hash_and_verify():
    hashed = hash_password("supersecure")
    assert verify_password("supersecure", hashed)
    assert not verify_password("wrongpass", hashed)


def test_session_round_trip():
    token = make_session_token(42)
    assert parse_session_token(token) == 42
