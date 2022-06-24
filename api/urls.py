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

    #get the product based on id sent, if the user has access to that id.
    re_path("getAllProductById/(?P<id>\w+)$",views.getAllProductById.as_view()),

    #delete product based on id sent, if the user has access to that id.
    re_path("deleteProduct/(?P<id>\w+)$",views.deleteProduct.as_view()),

    #edit product based on id sent, if the user has access to that id.
    re_path("editProduct/(?P<id>\w+)$",views.editProduct.as_view()),

    #add new products based on used id
    path("addProduct/",views.addProduct.as_view()),

    #search products via keywords , if they have access to it.
    re_path("searchProduct/((?P<keyword>\w+)=(?P<value>\w+))?",views.searchProduct.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)