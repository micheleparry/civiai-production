"""
URL configuration for civiai_project project.
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("CivAI is working!")

urlpatterns = [
    path('test/', test_view, name='test'),
    path('admin/', admin.site.urls),
]
