from functools import partial
from math import prod
from urllib import response
from django.conf import UserSettingsHolder
from django.shortcuts import render
from rest_framework import generics,permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ui.models import Product
from .serializers import productSerializer,customUserSerializer
from userAccess.models import CustomUser
from rest_framework.exceptions import AuthenticationFailed,NotFound
import jwt,datetime
from django.db.models.deletion import ProtectedError 
from api import serializers


class signUp(APIView):
    def post(self,request):
        "allow users to sign up via api"
        serializer_class = customUserSerializer(data=request.data)
        serializer_class.is_valid(raise_exception=True)
        serializer_class.save()
        return Response(serializer_class.data)

class signIn(APIView):
    def post(self,request):
        "Allow users to sign in via api"
        email=request.data['email']
        password=request.data['password']

        user =  CustomUser.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found.")
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")
        
        payload={
            'id':user.id,
            'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat':datetime.datetime.utcnow()#created date
        }
        token = jwt.encode(payload,'byte cipher', algorithm='HS256').decode("utf-8") #byte cipher is the secret
        response =  Response()
        
        response.set_cookie(key="jwt",value=token,httponly=True)

        response.data={
            'jwt':token
        }

        return response


class userView(APIView):
    def get(self,request):
        "ping...pong!"
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Not authenticated.")
        try:
            payload = jwt.decode(token,'byte cipher', algorithm=['HS256']) 
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed("Jwt Token expired")
        
        user = CustomUser.objects.filter(id=payload['id']).first()
        serializer = customUserSerializer(user)
        return Response(serializer.data)

class signOut(APIView):
    def post(self,request):
        ""
        response = Response()
        response.delete_cookie('jwt')
        response.data={
            'message':'logged out.'
        }
        return response


class getAllProduct(generics.ListAPIView):
    "displaying all of the products of the user"
    """#dango rest api default token authentication method.
    serializer_class = productSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        print(f"user id: {user_id}")
        return Product.objects.filter(id=user_id)
    """
    serializer_class = productSerializer
    def get_queryset(self):
        token = self.request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Not authenticated.")
        try:
            payload = jwt.decode(token,'byte cipher', algorithm=['HS256']) 
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed("Jwt Token expired")
        users = CustomUser.objects.filter(id=payload['id']).first()
        serializer = customUserSerializer(users)
        product = Product.objects.filter(user_id=serializer.data['id'])
        print(product)
        
        return product#Product.objects.get(user=user)

class getAllProductById(generics.ListCreateAPIView):
    serializer_class = productSerializer
    def get_queryset(self):
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Not authenticated.")
        try:
            payload = jwt.decode(token,'byte cipher', algorithm=['HS256']) 
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed("Jwt Token expired")
        users = CustomUser.objects.filter(id=payload['id']).first()
        #print(users) #test ok
        serializer = customUserSerializer(users)
        #print(serializer.data['id'])  #test ok
        #print(self.kwargs['id'])   #test ok

        product = Product.objects.filter(user_id=serializer.data['id'],id=self.kwargs['id'])
        if not product:
            ""
            raise NotFound("You dont have access to any product with that id.")
        #print(product) #test ok!
        return product


#my custom destroy mixin.
class DestroyModelMixin(object):
    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError as e:
            return Response(status=status.HTTP_423_LOCKED, data={'detail':str(e)})
        #return Response(status=status.HTTP_204_NO_CONTENT) #this is django default...
        #custom Response return on deletion.
        return Response({'message':'Deleted Successfully'})

    def perform_destroy(self, instance):
        instance.delete()
class deleteProduct(DestroyModelMixin,generics.DestroyAPIView):
    serializer_class = productSerializer
    #lookup_url_kwarg = pk
    lookup_field="id"
    def get_queryset(self):
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Not authenticated.")
        try:
            payload = jwt.decode(token,'byte cipher', algorithm=['HS256']) 
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed("Jwt Token expired")
        users = CustomUser.objects.filter(id=payload['id']).first()
        #print(users) #test ok
        serializer = customUserSerializer(users)
        #print(serializer.data['id'])  #test ok
        #print(self.kwargs['id'])   #test ok
        product = Product.objects.filter(user_id=serializer.data['id'],id=self.kwargs['id'])
        print(product)
        if not product:
            ""
            raise NotFound("You dont have access to any product with that id.")
        #print(product) #test ok!
        #product.delete()
        response = Response()
        response.content = product
        response.data={
            'message':'Deleted successfully.'
        }
        #return response
        return product


#Custom update mixin.
class UpdateModelMixin:
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True) #default is False #making partial edits as default
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        #print(request.data['productimages'])
        for image in request.data['productimages']:
            print(image['images'])
        self.perform_update(serializer) 

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

class editProduct(UpdateModelMixin,generics.UpdateAPIView):
    serializer_class = productSerializer
    #lookup_url_kwarg = pk
    lookup_field="id"
    def get_queryset(self):
        
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Not authenticated.")
        try:
            payload = jwt.decode(token,'byte cipher', algorithm=['HS256']) 
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed("Jwt Token expired")
        users = CustomUser.objects.filter(id=payload['id']).first()
        #print(users) #test ok
        serializer = customUserSerializer(users)
        #print(serializer.data['id'])  #test ok
        #print(self.kwargs['id'])   #test ok
        product = Product.objects.filter(user_id=serializer.data['id'],id=self.kwargs['id'])
        #print(product) #test ok.
        if not product:
            ""
            raise NotFound("You dont have access to any product with that id.")

        #saved_article = get_object_or_404(Article.objects.all(), pk=pk)

        # name = self.request.data.get('name')
        # serializer = productSerializer(instance=product, name=name, partial=True)
        # if serializer.is_valid(raise_exception=True):
        #     ""
        #     return serializer

        #article_saved = serializer.save()
        #return Response({"success": "Article '{}' updated successfully".format(article_saved.title)})

        """response = Response()
        response.data={
            'message':'test message.'
        }"""
        return product