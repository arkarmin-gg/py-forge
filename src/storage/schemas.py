from dataclasses import dataclass


@dataclass(frozen=True)
class StoredObject:
    """The result of a successful upload: the canonical key (persist this) and a
    resolved public URL (derived, for convenience — do not persist)."""

    key: str
    url: str | None
