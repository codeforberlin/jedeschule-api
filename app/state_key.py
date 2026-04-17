"""Validate `schools.state_key` from the database (set by jedeschule-scraper per Land)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.schemas import State


def parse_state_key_column(raw: str | None) -> Optional[State]:
    """Map stored ``state_key`` text to :class:`State`, or ``None`` if missing/invalid."""
    from app.schemas import State as StateEnum

    if raw is None:
        return None
    s = raw.strip()
    if len(s) != 2:
        return None
    try:
        return StateEnum(s)
    except ValueError:
        return None
