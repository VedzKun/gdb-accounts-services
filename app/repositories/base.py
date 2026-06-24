"""
Generic Base Repository
Module 7: Generics
"""

from typing import TypeVar, Generic, List, Dict, Any

# Bug (M07-Bug-01): TypeVar constraint mismatch.
# T is restricted to str and int, but repositories manage complex structures (dicts/objects).
# This causes mypy type-checking to fail. Trainees should remove the constraint or bind it properly.
# TODO: [M07-Bug-01] BUG: Static type checkers are complaining about constraint violations here when we use dictionaries or models.
T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Generic base repository for db operations."""
    
    def __init__(self):
        self._items: List[T] = []

    def add(self, item: T) -> None:
        """Add item to repository."""
        self._items.append(item)

    def get_all(self) -> List[T]:
        """Get all items."""
        return self._items
