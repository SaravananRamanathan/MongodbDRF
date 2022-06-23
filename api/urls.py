"""
api views
"""
from django.urls import path,include,re_path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

#all api endpoints are -user specific.
urlpatterns = [
    #signUp
    path("signUp",views.signUp.as_view()),

    #logIn
    path("signIn",views.signIn.as_view()),

    #user
    path("user",views.userView.as_view()),

    #signOut
    path("signOut",views.signOut.as_view()),

    #get all product 
    path("getAllProduct/",views.getAllProduct.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)