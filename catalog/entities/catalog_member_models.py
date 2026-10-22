import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from catalog.models import Catalog


DEFAULT_ROLE_PERMISSIONS = {

    "owner": {
        "catalog": {"edit": True, "delete": True, "manage_members": True},
        "category": {"create": True, "edit": True, "delete": True},
        "item": {"create": True, "edit": True, "delete": True, "change_price": True},
        "pricing": {"bulk_update": True}
    },

    "admin": {
        "catalog": {"edit": True, "manage_members": True},
        "category": {"create": True, "edit": True},
        "item": {"create": True, "edit": True, "change_price": True}
    },

    "editor": {
        "category": {"create": True, "edit": True},
        "item": {"create": True, "edit": True}
    },

    "support": {
        "item": {"edit": True}
    },

    "viewer": {}
}


class CatalogMember(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        EDITOR = "editor", "Editor"
        SUPPORT = "support", "Support"
        VIEWER = "viewer", "Viewer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="catalog_memberships",
        db_index=True
    )

    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="members",
        db_index=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        db_index=True
    )

    permissions = models.JSONField(default=dict)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "catalog")

        indexes = [
            models.Index(fields=["catalog", "user"]),
            models.Index(fields=["catalog", "role"]),
        ]

    def save(self, *args, **kwargs):

        if not self.permissions:
            self.permissions = DEFAULT_ROLE_PERMISSIONS.get(self.role, {})

        super().save(*args, **kwargs)

    def has_permission(self, section, action):

        return self.permissions.get(section, {}).get(action, False)


class CatalogActivity(models.Model):

    class Action(models.TextChoices):
        ITEM_CREATED = "item_created", "Item Created"
        ITEM_UPDATED = "item_updated", "Item Updated"
        ITEM_DELETED = "item_deleted", "Item Deleted"
        PRICE_CHANGED = "price_changed", "Price Changed"
        MEMBER_INVITED = "member_invited", "Member Invited"
        MEMBER_REMOVED = "member_removed", "Member Removed"

    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="activities",
        db_index=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True
    )

    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )

    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


def default_expiry():
    return timezone.now() + timedelta(days=7)


class CatalogInvite(models.Model):

    catalog = models.ForeignKey(
        Catalog,
        on_delete=models.CASCADE,
        related_name="invites",
        db_index=True
    )

    email = models.EmailField(db_index=True)

    role = models.CharField(
        max_length=20,
        choices=CatalogMember.Role.choices
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(default=default_expiry)

    class Meta:
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["token"]),
        ]
