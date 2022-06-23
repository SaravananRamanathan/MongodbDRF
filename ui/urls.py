"""
paths to select for respective views
"""
from django.urls import path
from . import views
#starting page path with ""
urlpatterns = [
    path("",views.home, name="home"),#home page
]
