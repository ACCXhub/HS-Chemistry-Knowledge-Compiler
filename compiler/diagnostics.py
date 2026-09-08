from __future__ import annotations

from typing import Any


def diagnostic(code: str, stage: str, message: str, **details: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "stage": stage, "message": message}
    if details:
        result["details"] = {key: details[key] for key in sorted(details)}
    return result
