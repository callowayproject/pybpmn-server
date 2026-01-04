"""
This module contains functionality to manage user security and access control within a multi-tenant environment.

It provides mechanisms to authorize user operations, check group memberships, and qualify resource queries based
on user and group-level configurations.
"""

from __future__ import annotations

import os
from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from pybpmn_server.datastore.query_translator import QueryTranslator


class UserRole(StrEnum):
    """Enumerates predefined roles for users in the system."""

    SYSTEM = "SYSTEM"
    ADMIN = "ADMIN"
    DESIGNER = "DESIGNER"


if os.environ.get("REQUIRE_AUTHENTICATION") == "false" or os.environ.get("ENFORCE_SECURITY") == "false":
    print("****Security is disabled as requested in environment****")
    BY_PASS = True
else:
    BY_PASS = False


class SecureUser(BaseModel):
    """
    Represents a secure user with access control and query qualification.

    This class manages user-specific security operations for grouping,
    privilege checks, and query handling in a controlled multi-tenant
    environment. It provides mechanisms to check user permissions, qualify
    queries based on user attributes, and authorize various operations on
    resources. This ensures that actions are performed based on both user
    and group-level configurations.
    """

    user_name: str
    """The name of the user."""

    user_groups: List[str] = Field(default_factory=list)
    """List of groups to which the user belongs."""

    models_owner: Optional[str] = None
    """The owner of the models, used for filtering and managing model access control."""

    tenant_id: Optional[str] = None
    """The tenant associated with the user, used to restrict query results to specific tenants."""

    def is_admin(self) -> bool:
        """
        Determines if the user has administrative privileges.

        This method evaluates whether the current user belongs to the administrative user
        groups. It also checks for any bypass conditions that may grant administrative
        privileges irrespective of the user's group membership.

        Returns:
            True if the user possesses administrative privileges; False otherwise.
        """
        if BY_PASS:
            return True
        return UserRole.ADMIN.value in self.user_groups or UserRole.SYSTEM.value in self.user_groups

    def is_system(self) -> bool:
        """Determines if the user is a system user."""
        if BY_PASS:
            return True
        return UserRole.SYSTEM.value in self.user_groups

    def in_group(self, user_group: str) -> bool:
        """Determines if the user belongs to the specified group."""
        if BY_PASS:
            return True
        return user_group in self.user_groups

    def qualify_instances(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Qualifies the query with user-specific criteria."""
        if BY_PASS:
            return query
        if self.tenant_id:
            query["tenantId"] = self.tenant_id

        if not self.is_admin():
            grp_query = [
                {"items.assignee": None, "items.candidateUsers": None, "items.candidateGroups": None},
                {"items.assignee": self.user_name},
                {"items.candidateUsers": self.user_name},
            ]

            grp_query.extend({"items.candidateGroups": grp} for grp in self.user_groups)

            query["$or"] = grp_query

        return query

    def qualify_items(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Qualifies the query with user-specific criteria."""
        if BY_PASS:
            return query
        return self.qualify_instances(query)

    def qualify_start_events(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Qualifies the query with user-specific criteria for start events."""
        if not self.is_admin():
            grp_query = [
                {"events.candidateUsers": None, "events.candidateGroups": None, "events.lane": None},
                {"events.candidateUsers": self.user_name},
            ]

            for grp in self.user_groups:
                grp_query.append({"events.candidateGroups": grp})
                grp_query.append({"events.lane": grp})

            query["$or"] = grp_query

        return query

    def qualify_delete_instances(self, query: Dict[str, Any]) -> Any:
        """Qualifies the query for deleting instances based on user permissions."""
        if self.is_admin():
            return self.qualify_instances(query)
        else:
            return False

    def qualify_models(self, query: Dict[str, Any]) -> Any:
        """Qualifies the query for fetching models based on user permissions."""
        if BY_PASS:
            return True
        if self.models_owner:
            query["owner"] = self.models_owner
        return query

    def can_modify_model(self, name: str) -> bool:
        """Determines if the user can modify a model."""
        return self.is_admin()

    def can_delete_model(self, name: str) -> bool:
        """Determines if the user can delete a model."""
        return self.is_admin()

    async def qualify_view_items(self, query: Dict[str, Any]) -> None:
        """Qualifies the query for viewing items based on user permissions."""
        pass

    def can_invoke(self, item: Any) -> bool:
        """Determines if the user can invoke an item."""
        if self.is_admin():
            return True
        # item can be IItemData or dict
        assignee = getattr(item, "assignee", item.get("assignee") if isinstance(item, dict) else None)
        return assignee == self.user_name

    def can_assign(self, item: Any) -> bool:
        """Determines if the user can assign an item."""
        if self.is_admin():
            return True

        assignee = getattr(item, "assignee", item.get("assignee") if isinstance(item, dict) else None)
        if assignee == self.user_name:
            return True

        query = {}
        grp_query = [
            {"items.assignee": None, "items.candidateUsers": None, "items.candidateGroups": None},
            {"items.candidateUsers": self.user_name},
        ]
        grp_query.extend({"items.candidateGroups": grp} for grp in self.user_groups)

        query["$or"] = grp_query

        trans = QueryTranslator("items")
        db_qry = trans.translate_criteria(query)
        return trans.filter_item(item, db_qry)

    async def can_start(self, name: str, start_node_id: str, user: Any) -> bool:
        """Determines if the user can start a process instance."""
        return True


SystemUser = SecureUser(user_name="system", user_groups=[UserRole.SYSTEM.value], tenant_id=None, models_owner=None)
