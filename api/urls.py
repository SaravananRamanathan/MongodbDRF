"""
api views
"""
from django.urls import path,include,re_path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

#all api endpoints are -user specific.
urlpatterns = [
    #get all product 
    #path("getAllProduct/",views.getAllProduct),#view method
    path("getAllProduct/",views.getAllProduct.as_view()),#class based view method
]

urlpatterns = format_suffix_patterns(urlpatterns)