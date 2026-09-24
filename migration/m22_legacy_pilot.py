"""Compatibility entry point for the historical M22 pilot."""

from .legacy_identity import *  # noqa: F403
from .legacy_identity import main


if __name__ == "__main__":
    raise SystemExit(main())
