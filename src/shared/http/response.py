def error_response(code: str, message: str, retryable: bool = False) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "retryable": retryable,
        }
    }
