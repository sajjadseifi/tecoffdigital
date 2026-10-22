from django.shortcuts import render
from django.http import HttpResponse

def game_land(request):
    template = "game/game_land.html"
    context = {}
    return render(request, template,context)
def game_deew(request):
    template = "game/game_deew.html"
    context = {}
    return render(request, template,context)

def game_groot(request):
    template = "game/groot/groot_gland.html"
    context = {}
    return render(request, template,context)
