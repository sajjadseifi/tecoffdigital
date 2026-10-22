from django.contrib.admin import SimpleListFilter
from .models import Catalog

class CatalogFilter(SimpleListFilter):
    title = "کاتالوگ"
    parameter_name = "catalog"

    def lookups(self, request, model_admin):
        return [(c.id, c.title) for c in Catalog.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category__catalog__id=self.value())
        return queryset
