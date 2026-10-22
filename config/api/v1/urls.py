from django.urls import path
from catalog import controllers
from accounts import views as accounts
from presentation import views as presentation
from presentation.view import tqrs_view 


urlpatterns = [

    # =====================================
    # Members API
    # =====================================
    path("catalog/members/list/", controllers.api_members_list, name="api_members_list"),
    path("catalog/members/invite/", controllers.api_member_invite, name="api_member_invite"),
    path("catalog/members/<int:member_id>/update/", controllers.api_member_update, name="api_member_update"),
    path("catalog/members/<int:member_id>/delete/", controllers.api_member_delete, name="api_member_delete"),

    # =====================================
    # Invite Management
    # =====================================
    path("catalog/invites/<uuid:token>/resend/", controllers.api_invite_resend, name="api_invite_resend"),
    path("catalog/invites/<uuid:token>/cancel/", controllers.api_invite_cancel, name="api_invite_cancel"),

    # =====================================
    # Authentication API
    # =====================================
    path("auth/request-otp/", accounts.auth_otp_request, name="auth_otp_request"),
    path("auth/verify-otp/", accounts.auth_otp_verify, name="auth_otp_verify"),
    path("auth/sign-in/", accounts.auth_sign_in, name="auth_sign_in"),

    # =====================================
    # Catalog API
    # =====================================
    path("<str:catalog_slug>/", controllers.catalog_detail, name="catalog_detail"),
    path("<str:catalog_slug>/search/", controllers.api_catalog_search, name="api_catalog_search"),
    path("<str:catalog_slug>/categories/<str:category_slug>/detail/", controllers.api_category_detail, name="api_category_detail"),
    path("<str:catalog_slug>/categories/<str:category_slug>/items/", controllers.api_category_items, name="api_category_items"),
    path("<str:catalog_slug>/items/<str:item_slug>/detail/", controllers.api_item_detail, name="api_item_detail"),


    # =====================================
    # Icon Library (Teclib)
    # =====================================
    path("teclib/icons/list/", presentation.api_icons_list, name="api_list"),
    path("teclib/icons/save/", presentation.api_icon_save, name="api_save"),
    path("teclib/icons/delete/<int:icon_id>/", presentation.api_icon_delete, name="api_icon_delete"),
    path("teclib/icons/bulk-delete/", presentation.api_icon_bulk_delete, name="api_icons_bulk_delete"),

    # =====================================
    # Excel Import API
    # =====================================
    path("teclib/excel/preview/", presentation.api_preview_excel, name="api_preview_excel"),
    path("teclib/excel/save/bulk", presentation.api_bulk_save_excel, name="api_bulk_save_excel"),

    # =====================================
    # TQRS Code API
    # =====================================
    path("tqrs/generate", tqrs_view.qrcode_genarate_api, name="qrcode_generate"),
    path("tqrs/<str:hash_qrcode>/check", tqrs_view.tqrs_protocol_check_api, name="tqrs_protocol_check_api"),
    path('tqrs/check/<str:hash_qrcode>/', tqrs_view.tqrs_protocol_check_api, name='api_check'),
    path('tqrs/report-error/', tqrs_view .tqrs_report_error_api, name='api_report_error'),

]
