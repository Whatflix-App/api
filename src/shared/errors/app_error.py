from dataclasses import dataclass


@dataclass
class AppError(Exception):
    code: str
    message: str
    retryable: bool = False
    status_code: int = 400
