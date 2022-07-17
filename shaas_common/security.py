import hmac
import hashlib


def get_hash(token: str, data):
    secret_key = hmac.new(
        key=token.encode(encoding="utf-8"),
        msg=b"WebAppData",
        digestmod=hashlib.sha256
    )

    return hmac.new(
        key=secret_key.digest(),
        msg=str(data).encode(),
        digestmod=hashlib.sha256
    ).hexdigest()


def is_valid(token, user_id, timestamp, expected) -> bool:
    hash = get_hash(token, f"{timestamp}{user_id}")
    return expected == hash