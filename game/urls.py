from django.urls import path
from . import views

app_name = 'game' 

urlpatterns = [
    # مسیر اصلی برای لندینگ بازی (مثلا: /game/)
    path('', views.game_land, name='game_land'),
    
    # مسیر برای deew (مثلا: /game/deew/)
    path('deew/', views.game_deew, name='game_deew'),
    
    # مسیر برای groot (مثلا: /game/groot/)
    path('groot/', views.game_groot, name='game_groot'),
]
