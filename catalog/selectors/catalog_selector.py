from django.db.models import Prefetch
from catalog.models import Catalog, Category, Item


def get_catalog_by_slug(slug):

    return (
        Catalog.objects
        .filter(slug=slug, is_active=True)
        .prefetch_related(
            Prefetch(
                "categories",
                queryset=Category.objects.filter(is_active=True).prefetch_related("items")
            )
        )
        .first()
    )
