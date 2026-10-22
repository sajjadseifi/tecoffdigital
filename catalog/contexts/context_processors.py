import logging

from catalog.entities import Catalog, CatalogMember

logger = logging.getLogger(__name__)


def user_catalog_context(request):

    user = request.user
    catalog = None
    show_catalog_modal = False
    user_catalogs = []

    if user.is_authenticated:

        logger.info(f"[CATALOG_CTX] user={user.id}")

        # --- (A) ساخت لیست catalog ها ---

        owned_catalogs = (
            Catalog.objects
            .filter(owner=user)
            .only("id", "title", "logo", "owner_id")
        )

        for c in owned_catalogs:
            user_catalogs.append({
                "catalog": c,
                "role": "owner"
            })

        members = (
            CatalogMember.objects
            .filter(user=user, is_active=True)
            .select_related("catalog")
            .only(
                "role",
                "catalog__id",
                "catalog__title",
                "catalog__logo",
                "catalog__owner_id"
            )
        )

        for m in members:
            user_catalogs.append({
                "catalog": m.catalog,
                "role": m.role
            })

        logger.info(
            f"[CATALOG_CTX] total catalogs found = {len(user_catalogs)}"
        )

        # --- (B) مرتب سازی ---
        role_priority = {"owner": 1, "manager": 2, "member": 3}

        user_catalogs.sort(
            key=lambda x: (
                role_priority.get(x["role"], 9),
                x["catalog"].title
            )
        )

        # --- (C) گرفتن active catalog از session ---
        catalog_id = request.session.get("active_catalog")

        logger.info(
            f"[CATALOG_CTX] session active_catalog = {catalog_id}"
        )

        if catalog_id:
            catalog = next(
                (c["catalog"] for c in user_catalogs if c["catalog"].id == catalog_id),
                None
            )

        logger.info(
            f"[CATALOG_CTX] catalog resolved from session = {catalog}"
        )

        # --- (D) اگر session نداشت → اولین catalog ---
        if not catalog and user_catalogs:

            catalog = user_catalogs[0]["catalog"]

            request.session["active_catalog"] = catalog.id

            logger.warning(
                f"[CATALOG_CTX] session missing → auto set active_catalog={catalog.id}"
            )

        # --- (E) modal ---
        if catalog is None:
            show_catalog_modal = True
            logger.warning("[CATALOG_CTX] user has no catalog")
        else:
            if not catalog.title or catalog.title == f"'s Catalog":
                show_catalog_modal = True

        # --- (F) role ---
        if catalog:

            if catalog.owner_id == user.id:
                user.is_manager = True
                logger.info("[CATALOG_CTX] role=owner")

            else:

                member = next(
                    (m for m in members if m.catalog_id == catalog.id),
                    None
                )

                user.is_manager = (
                    member and member.role in ["manager", "owner"]
                )

                logger.info(
                    f"[CATALOG_CTX] role member={member.role if member else None}"
                )
    catalogs = Catalog.objects.none()

    if user.is_authenticated:
        catalogs = Catalog.objects.filter(owner=user)

    return {
        "catalogs":catalogs,
        "user_catalog": catalog,
        "user_catalogs": user_catalogs,
        "show_catalog_modal": show_catalog_modal,
        'user_authed':user.is_authenticated
    }
