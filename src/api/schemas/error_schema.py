from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: List[ErrorDetail] = []
    timestamp: str
    path: str


def make_error(error: str, message: str, path: str, details: list = None):
    """Helper para criar resposta de erro padronizada."""
    return {
        "error": error,
        "message": message,
        "details": details or [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "path": path
    }