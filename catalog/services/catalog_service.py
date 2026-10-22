from django.utils.text import slugify
from catalog.models import Catalog, Category, Item
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity
)
from django.db.models import Q
from catalog.models import Catalog



class CatalogService:
    def __init__(self, user):
        self.user = user

    def search_catalogs(query):

        if not query:
            return Catalog.objects.none()

        vector = (
            SearchVector("title", weight="A") +
            SearchVector("business_type", weight="A") +
            SearchVector("tagline", weight="A") +
            SearchVector("description", weight="B") +
            SearchVector("about", weight="B") +
            SearchVector("services", weight="B") +
            SearchVector("address", weight="C")
        )

        search_query = SearchQuery(query)

        qs = (
            Catalog.objects
            .filter(is_active=True, is_public=True)
            .annotate(
                rank=SearchRank(vector, search_query),
                similarity=
                    TrigramSimilarity("title", query) +
                    TrigramSimilarity("business_type", query) +
                    TrigramSimilarity("description", query)
            )
            .filter(
                Q(rank__gte=0.1) |
                Q(similarity__gt=0.2) |
                Q(title__icontains=query) |
                Q(business_type__icontains=query)
            )
            .order_by("-rank", "-similarity", "-is_featured", "-views")
            .distinct()
        )

        return qs

    @staticmethod
    def search_similar(query_text, limit=20):

        if not query_text:
            return Catalog.objects.none()

        query_text = query_text.strip('%')  # نرمال کردن ورودی

        # جستجو با LIKE
        qs = (
            Catalog.objects
            .filter(is_active=True, is_public=True)
            .filter(
                Q(title__icontains=query_text) |
                Q(business_type__icontains=query_text) |
                Q(tagline__icontains=query_text) |
                Q(description__icontains=query_text) |
                Q(about__icontains=query_text) |
                Q(services__icontains=query_text) |
                Q(address__icontains=query_text)
            )
            .order_by('-is_featured', '-views')  # مرتب‌سازی بر اساس ویژگی‌ها
            .distinct()[:limit]  # محدود کردن به ۲۰ نتیجه
        )

        return qs

    @staticmethod
    def get_singleton_catalog(user):
        if not user or not user.is_authenticated:
            return None

        service = CatalogService(user)
        catalog = service.get_catalog() 

        return catalog
    
    def get_catalog(self):
        """
        فقط کاتالوگ کاربر را واکشی می‌کند.
        اگر نبود، None برمی‌گرداند و چیزی نمی‌سازد.
        """
        try:
            return Catalog.objects.filter(owner=self.user).first()
        except Catalog.DoesNotExist:
            return None

    @staticmethod
    def get_catalog_by_id(catalog_id):
        try:
            return Catalog.objects.filter(id=catalog_id).first()
        except Catalog.DoesNotExist:
            return None

    @staticmethod
    def get_catalog_by_slug(slug):
        try:
            return Catalog.objects.filter(slug=slug).first()
        except Catalog.DoesNotExist:
            return None

    def get_user_catalogs(self):
        return Catalog.objects.filter(owner=self.user)

    def create_category(self, catalog, title, description="", image=None, order=0, is_active=True):
        slug = slugify(title)
        category = Category.objects.create(
            catalog=catalog,
            title=title,
            slug=slug,
            description=description,
            image=image,
            order=order,
            is_active=is_active,
        )
        return category

    def get_category_by_slug(self, catalog, slug):
        try:
            return Category.objects.get(catalog=catalog, slug=slug)
        except Category.DoesNotExist:
            return None
        

    def list_categories(self, catalog):
        return catalog.categories.filter(is_active=True).order_by("order", "title")

    def create_item(
        self,
        category,
        title,
        description="",
        image=None,
        price=None,
        discount_price=None,
        sku="",
        stock=0,
        is_available=True,
        is_featured=False,
        order=0,
    ):
        slug = slugify(title)
        item = Item.objects.create(
            category=category,
            title=title,
            slug=slug,
            description=description,
            image=image,
            price=price,
            discount_price=discount_price,
            sku=sku,
            stock=stock,
            is_available=is_available,
            is_featured=is_featured,
            order=order,
        )
        return item

    def get_item_by_slug(self, category, slug):
        try:
            return Item.objects.get(category=category, slug=slug)
        except Item.DoesNotExist:
            return None

    def list_items(self, category):
        return category.items.filter(is_available=True).order_by("order", "title")
