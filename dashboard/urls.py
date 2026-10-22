from django.urls import path
from . import views
from website import views as website

urlpatterns = [
    path("",                                 views.dashboard_workspace,              name="dashboard"),
    path("",                                 views.dashboard_workspace,              name="dashboard_workspace"),
    # CATALOGS
    path("catalog/setting",               views.dashboard_catalog_setting,        name="dashboard_catalog_setting"),
    path("catalog/categories",               views.dashboard_categories_list,        name="dashboard_catalog_categories"),
    path("catalog/items",                    views.dashboard_items_list,             name="dashboard_catalog_items"),
    path("catalog/qr-codes",                 views.dashboard_qrcode_list,            name="dashboard_qr_codes"),
    path("catalog/wallpare",                 views.dashbaord_wallpare_list,          name="dashbaord_wallpares"),
    path("catalog/members", views.dashboard_catalog_members, name="dashboard_catalog_members"),
    
    path("palate/icons",                 views.dashboard_palate_icons_list,          name="dashboard_palate_icons"),
    # مسیر اصلی مدیریت وب‌سایت
    path('website/', website.dashboard_website, name='dashboard_website'),
    
    # مسیرهای مربوط به بخش‌ها (Sections)
    path('website/section/add/', website.dashboard_section_create, name='dashboard_section_create'),
    path('website/section/<int:pk>/edit/', website.dashboard_section_edit, name='dashboard_section_edit'),
    path('website/section/<int:pk>/delete/', website.dashboard_section_delete, name='dashboard_section_delete'),
    # مسیرهای مربوط به آیتم‌ها (Items)
    path('website/section/<int:section_id>/item/add/', website.dashboard_item_create, name='dashboard_item_create'),
    path('website/item/<int:pk>/edit/', website.dashboard_item_edit, name='dashboard_item_edit'),
    path('website/item/<int:pk>/delete/', website.dashboard_item_delete, name='dashboard_item_delete'),
    path('section/<int:pk>/toggle/', website.dashboard_section_toggle, name='dashboard_section_toggle'),

]