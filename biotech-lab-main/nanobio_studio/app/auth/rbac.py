"""
Role-Based Access Control (RBAC)

Role definitions, permission management, and access control logic.
"""

import logging
from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass


logger = logging.getLogger(__name__)


class Role(str, Enum):
    """Available roles"""
    ADMIN = "admin"
    SCIENTIST = "scientist"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(str, Enum):
    """Available permissions"""

    # Dataset operations
    DATASET_READ = "dataset:read"
    DATASET_CREATE = "dataset:create"
    DATASET_DELETE = "dataset:delete"

    # Model operations
    MODEL_READ = "model:read"
    MODEL_TRAIN = "model:train"
    MODEL_DELETE = "model:delete"
    MODEL_EXPORT = "model:export"

    # Prediction operations
    PREDICT_READ = "predict:read"
    PREDICT_CREATE = "predict:create"

    # Ranking operations
    RANK_READ = "rank:read"
    RANK_CREATE = "rank:create"

    # User management
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # System operations
    SYSTEM_ADMIN = "system:admin"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # All permissions
        Permission.DATASET_READ,
        Permission.DATASET_CREATE,
        Permission.DATASET_DELETE,
        Permission.MODEL_READ,
        Permission.MODEL_TRAIN,
        Permission.MODEL_DELETE,
        Permission.MODEL_EXPORT,
        Permission.PREDICT_READ,
        Permission.PREDICT_CREATE,
        Permission.RANK_READ,
        Permission.RANK_CREATE,
        Permission.USER_READ,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.SYSTEM_ADMIN,
    },
    Role.SCIENTIST: {
        # Can read and create, but not delete
        Permission.DATASET_READ,
        Permission.DATASET_CREATE,
        Permission.MODEL_READ,
        Permission.MODEL_TRAIN,
        Permission.MODEL_EXPORT,
        Permission.PREDICT_READ,
        Permission.PREDICT_CREATE,
        Permission.RANK_READ,
        Permission.RANK_CREATE,
    },
    Role.VIEWER: {
        # Read-only access
        Permission.DATASET_READ,
        Permission.MODEL_READ,
        Permission.PREDICT_READ,
        Permission.RANK_READ,
    },
    Role.GUEST: {
        # Very limited access
        Permission.MODEL_READ,
    },
}


@dataclass
class AccessContext:
    """Access control context"""

    user_id: str
    username: str
    roles: List[Role]
    permissions: List[Permission]

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has permission"""
        return permission in self.permissions

    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the permissions"""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all permissions"""
        return all(p in self.permissions for p in permissions)

    def has_role(self, role: Role) -> bool:
        """Check if user has role"""
        return role in self.roles

    def is_admin(self) -> bool:
        """Check if user is admin"""
        return Role.ADMIN in self.roles


class RBACManager:
    """RBAC management"""

    @staticmethod
    def get_permissions_for_roles(roles: List[Role]) -> Set[Permission]:
        """
        Get all permissions for given roles.

        Args:
            roles: List of roles

        Returns:
            Set of permissions
        """
        permissions = set()
        for role in roles:
            if role in ROLE_PERMISSIONS:
                permissions.update(ROLE_PERMISSIONS[role])
        return permissions

    @staticmethod
    def create_access_context(
        user_id: str,
        username: str,
        roles: List[Role],
    ) -> AccessContext:
        """
        Create access context for user.

        Args:
            user_id: User ID
            username: Username
            roles: User roles

        Returns:
            AccessContext
        """
        permissions = RBACManager.get_permissions_for_roles(roles)

        return AccessContext(
            user_id=user_id,
            username=username,
            roles=roles,
            permissions=list(permissions),
        )

    @staticmethod
    def require_permission(
        context: AccessContext,
        permission: Permission,
    ) -> bool:
        """
        Check if user has required permission.

        Args:
            context: Access context
            permission: Required permission

        Returns:
            True if has permission, False otherwise
        """
        return context.has_permission(permission)

    @staticmethod
    def require_any_permission(
        context: AccessContext,
        permissions: List[Permission],
    ) -> bool:
        """
        Check if user has any required permission.

        Args:
            context: Access context
            permissions: List of permissions (any one required)

        Returns:
            True if has any permission, False otherwise
        """
        return context.has_any_permission(permissions)

    @staticmethod
    def require_all_permissions(
        context: AccessContext,
        permissions: List[Permission],
    ) -> bool:
        """
        Check if user has all required permissions.

        Args:
            context: Access context
            permissions: List of permissions (all required)

        Returns:
            True if has all permissions, False otherwise
        """
        return context.has_all_permissions(permissions)


def check_permission(
    context: AccessContext,
    permission: Permission,
) -> bool:
    """Shorthand for checking single permission"""
    return RBACManager.require_permission(context, permission)


def check_any_permission(
    context: AccessContext,
    *permissions: Permission,
) -> bool:
    """Shorthand for checking any permission"""
    return RBACManager.require_any_permission(context, list(permissions))


def check_all_permissions(
    context: AccessContext,
    *permissions: Permission,
) -> bool:
    """Shorthand for checking all permissions"""
    return RBACManager.require_all_permissions(context, list(permissions))
