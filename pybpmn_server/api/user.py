"""User interface."""

from __future__ import annotations

from typing import Any, Protocol


class UserService(Protocol):
    """User service."""

    def find_users(self, query: Any) -> Any:
        """Find users matching the query."""
        ...

    def add_user(self, user_name: Any, email: Any, password: Any, user_groups: Any) -> Any:
        """Add a user."""
        ...

    def set_password(self, user_name: Any, password: Any) -> Any:
        """Set the password for a user."""
        ...

    def install(self) -> Any:
        """Install the service."""
        ...
