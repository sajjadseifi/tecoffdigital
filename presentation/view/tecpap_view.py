from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

def tecpap_index(request):
    context = {}
    return render(request, "tec/tecpap/tecpap_index.html", context, status=200)

def tecpap_form_save(request):
    pass

def tecpap_form_download(request):
    pass