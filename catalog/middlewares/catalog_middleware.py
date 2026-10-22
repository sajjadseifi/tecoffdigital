"""
Active Catalog Middleware
--------------------------------------------------

Purpose:
Resolve the active catalog for the current request and
attach related membership information.

Adds the following attributes to request:

request.catalog
request.catalog_member
request.catalog_role
request.catalog_is_owner

This removes the need to manually fetch catalog context
in every view.
"""

from django.shortcuts import redirect
from catalog.entities import Catalog, CatalogMember


class ActiveCatalogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Default values
        request.catalog = None
        request.catalog_member = None
        request.catalog_role = None
        request.catalog_is_owner = False

        # Skip for anonymous users
        if not request or request.user and not request.user.is_authenticated:
            return self.get_response(request)

        catalog_id = request.session.get("active_catalog")

        if catalog_id:

            try:

                catalog = Catalog.objects.get(id=catalog_id)

                request.catalog = catalog

                # Owner check
                if catalog.owner_id == request.user.id:
                    request.catalog_is_owner = True
                    request.catalog_role = "owner"

                else:

                    member = CatalogMember.objects.filter(
                        catalog_id=catalog_id,
                        user=request.user,
                        is_active=True
                    ).select_related("user").first()

                    if member:
                        request.catalog_member = member
                        request.catalog_role = member.role

            except Catalog.DoesNotExist:
                request.catalog = None

        response = self.get_response(request)
        return response
