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