from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any


def _normalize(value: Any) -> Any:
    """Normalize the F2 semantic JSON domain.

    F2 intentionally admits only JSON null/bool/integer/string/list/map values.
    Floating-point values are rejected so platform/library formatting cannot become
    hash semantics. Strings and mapping keys are normalized to Unicode NFC.
    """
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, float):
        raise TypeError("floating-point values are not part of F2 canonical JSON")
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("canonical JSON map keys must be strings")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in normalized:
                raise ValueError(f"duplicate key after NFC normalization: {key!r}")
            normalized[normalized_key] = _normalize(item)
        return {key: normalized[key] for key in sorted(normalized)}
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    normalized = _normalize(value)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def write_canonical_json(path: Path, value: Any) -> str:
    data = canonical_json_bytes(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()
