# api/urls.py

from django.urls import path
from catalog import controllers
from accounts import views as accounts
from presentation import views as presentation

urlpatterns = [
    path("catalog/members/list/", controllers.api_members_list, name="api_members_list"),
    path("catalog/members/invite/", controllers.api_member_invite, name="api_member_invite"),
    path("catalog/members/<int:member_id>/update/", controllers.api_member_update, name="api_member_update"),
    path("catalog/members/<int:member_id>/delete/", controllers.api_member_delete, name="api_member_delete"),

    path("catalog/invites/<uuid:token>/resend/", controllers.api_invite_resend, name="api_invite_resend"),
    path("catalog/invites/<uuid:token>/cancel/", controllers.api_invite_cancel, name="api_invite_cancel"),

    path("auth/request-otp/", accounts.auth_otp_request, name="auth_otp_request"),
    path("auth/verify-otp/", accounts.auth_otp_verify, name="auth_otp_verify"),
    path("auth/sign-in/", accounts.auth_sign_in, name="auth_sign_in"),

    path("<str:catalog_slug>/", controllers.catalog_detail, name="catalog_detail"),
    path("<str:catalog_slug>/search/", controllers.api_catalog_search, name="api_catalog_search"),
    path("<str:catalog_slug>/categories/<str:category_slug>/detail/", controllers.api_category_detail, name="api_category_detail"),
    path("<str:catalog_slug>/categories/<str:category_slug>/items/", controllers.api_category_items, name="api_category_items"),
    path("<str:catalog_slug>/items/<str:item_slug>/detail/", controllers.api_item_detail, name="api_item_detail"),

    path("teclib/icons/list/", presentation.api_icons_list, name="api_list"),
    path("teclib/icons/save/", presentation.api_icon_save, name="api_save"),
    path("teclib/icons/delete/<int:icon_id>/", presentation.api_icon_delete, name="api_icon_delete"),
    path("teclib/icons/bulk-delete/", presentation.api_icon_bulk_delete, name="api_icons_bulk_delete"),

    path("teclib/excel/preview/", presentation.api_preview_excel, name="api_preview_excel"),
    path("teclib/excel/save/bulk", presentation.api_bulk_save_excel, name="api_bulk_save_excel"),

]
