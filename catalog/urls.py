from django.urls import path
from . import views
from . import controllers

app_name = "catalog"

# API Endpoints
urlpatterns = [
    
    path("catalog/create/quick/", controllers.catalog_create_quick, name="catalog_create_quick"),
    path("catalog/create/", views.create_or_update_catalog_api, name="create"),
    path("catalog/switch/<int:catalog_id>/",views.catalog_switch,name="catalog_switch"),
    # 
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/update/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    # 
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:item_id>/update/', views.item_edit, name='item_edit'),
    path('items/<int:item_id>/delete/', views.item_delete, name='item_delete'),
    # 
    path('qrcode/create/', controllers.qrcode_create, name='qrcode_create'),
    path('qrcode/<int:qrcode_id>/edit/', controllers.qrcode_edit, name='qrcode_edit'),
    path('qrcode/<int:qrcode_id>/delete/', controllers.qrcode_delete, name='qrcode_delete'),    

]

