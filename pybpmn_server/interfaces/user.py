"""User interface."""

from __future__ import annotations

from typing import Any, List, Optional, Protocol


class IUserInfo(Protocol):
    """User information."""

    user_name: str
    """Unique, saved in the workflow."""

    user_groups: List[str]
    """To filter for security."""

    tenant_id: Optional[str] = None
    """Used to mark instances."""

    models_owner: Optional[str] = None
    """Used if models are not shared among tenants."""


class ISecureUser(IUserInfo):
    """User with security information."""

    def is_admin(self) -> bool:
        """Is the user an administrator?"""
        ...

    def is_system(self) -> bool:
        """Is the user a system user?"""
        ...

    def in_group(self, user_group: Any) -> bool:
        """Does the user belong to the given group?"""
        ...

    def qualify_instances(self, query: Any) -> Any:
        """Alters the query adding conditions based on security rules."""
        ...

    def qualify_items(self, query: Any) -> Any:
        """Alters the query adding conditions based on security rules."""
        ...

    def qualify_start_events(self, query: Any) -> Any:
        """Alters the query adding conditions based on security rules."""
        ...

    def qualify_delete_instances(self, query: Any) -> Any:
        """Alters the query adding conditions based on security rules."""
        ...

    def qualify_models(self, query: Any) -> Any:
        """Alters the query adding conditions based on security rules."""
        ...

    def can_modify_model(self, name: Any) -> Any:
        """Can the user modify the model?"""
        ...

    def can_delete_model(self, name: Any) -> Any:
        """Can the user delete the model?"""
        ...

    def qualify_view_items(self, query: Any) -> Any:
        """Alters the query adding conditions based on security rules."""
        ...

    def can_invoke(self, item: Any) -> Any:
        """Can the user invoke the item?"""
        ...

    def can_assign(self, item: Any) -> Any:
        """Can the user assign the item?"""
        ...

    def can_start(self, name: Any, start_node_id: Any, user: Any) -> Any:
        """Can the user start the process?"""
        ...


class IUserService(Protocol):
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
