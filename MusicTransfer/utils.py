import time


def add_token_expiry_time(token_dict: dict) -> dict:
    token_dict["expires_at"] = token_dict["expires_in"] + int(time.time())
    return token_dict


def token_expired(token_dict: dict) -> bool:
    return token_dict["expires_at"] <= time.time()
