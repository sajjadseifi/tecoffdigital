from django.urls import path
from . import views
from .view import tecpap_view 
from .view import tqrs_view 


urlpatterns = [
    path("", views.landing_page, name="landing"),
    # 
    path("land/dream/"      , views.tecland_dream   , name="tecland_dream"),
    path("land/book/"       , views.tecland_book     , name="tecland_book"),
    path("land/doc/"        , views.tecland_doc     , name="tecland_doc"),
    path("land/dev/"        , views.tecland_dev     , name="tecland_dev"),
    path("land/team/"       , views.tecland_team    , name="tecland_team"),
    path("land/devops/"        , views.tecland_devops     , name="tecland_devops"),
    path("land/game/"       , views.tecland_game    , name="tecland_game"),
    path("land/work/"       , views.tecland_work    , name="tecland_work"),
    path("land/job/"        , views.tecland_job     , name="tecland_job"),
    path("land/"            , views.tecland   , name="tecland"),
    path("catalogs/"        , views.catalogs        , name="catalogs"),
    path('catalogs/<str:business_type>/', views.category_catalogs_detail, name='category_catalogs_detail'),
    path("app/", views.catalogs, name="tecapp"),
    path("teapp/", views.catalogs, name="tecapp"),
    path('app/<str:business_type>/', views.category_catalogs_detail, name='tecapp_detail'),
    path('teapp/<str:business_type>/', views.category_catalogs_detail, name='tecapp_detail'),
    path('tecapp/<str:business_type>/', views.category_catalogs_detail, name='tecapp_detail'),
    path("grootapp/<str:business_type>/", views.catalogs, name="tecapp_detail"),
    path("api/catalogs/load-more/", views.catalog_load_more, name="catalog_load_more"),
    path("api/catalogs/search/", views.search_catalogs, name="catalog_search"),
    path(
        "preview/<int:catalog_id>/template/<str:template_key>/",
        views.preview_template,
        name="preview_template_base"
    ),
    path(
        "preview/<int:catalog_id>/template/<str:template_key>/<str:page_name>/",
        views.preview_template,
        name="preview_template"
    ),
    path("tqrs/", tqrs_view.tqrs_index, name="tqrs_index"),
    path("tqrs/root", tqrs_view.tqrs_root, name="tqrs_root"),
    path("tqrs/about", tqrs_view.tqrs_about, name="tqrs_about"),
    path("tqrs/tqrs_contact", tqrs_view.tqrs_contact, name="tqrs_contact"),
    path("tqrs/<str:hash_qrcode>/", tqrs_view.tqrs_protocol, name="tqrs_protocol"),
    path('tqrs/root/', tqrs_view.tqrs_root, name='tqrs_root'),
    path('tqrs/about/', tqrs_view.tqrs_about, name='tqrs_about'),
    path('tqrs/contact/', tqrs_view.tqrs_contact, name='tqrs_contact'),
    path('tqrs/soul/<str:hash_qrcode>/', tqrs_view.tqrs_protocol, name='protocol'),
    path("q/<str:catalog_slug>/", views.app_catalog, name="app_catalog_q_base"),
    path("q/<str:catalog_slug>/<str:page_name>/", views.app_catalog, name="app_catalog_q"),
    path("app/catalog/user", views.app_catalog_user, name="app_catalog_user"),
    path("app/<str:catalog_slug>/", views.app_catalog, name="app_catalog_base"),
    path("app/<str:catalog_slug>/<str:page_name>/", views.app_catalog, name="app_catalog"),
    path('tecpap/', tecpap_view.tecpap_index, name='tecpap_index'),
    path('tecpap/form/save/', tecpap_view.tecpap_form_save, name='tecpap_form_save'),
    path('tecpap/form/download/<str:form_name>/', tecpap_view.tecpap_form_download, name='tecpap_form_download'),
]
