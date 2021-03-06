from ast import match_case
from functools import partial
from math import prod
from urllib import response
from django.conf import UserSettingsHolder
from django.shortcuts import render
from rest_framework import generics,permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ui.models import Product,productImages
from .serializers import productSerializer,customUserSerializer,productCreateSerializer
from userAccess.models import CustomUser
from rest_framework.exceptions import AuthenticationFailed,NotFound,NotAcceptable
import jwt,datetime
from django.db.models.deletion import ProtectedError 
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import tempfile
import  urllib.request 
import requests
from PIL import Image
import urllib
from rest_framework.settings import APISettings,DEFAULTS,IMPORT_STRINGS
#import djangocorefilesbase.ContentFile
from django.core.files.base import ContentFile
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
        #print(request.data['productimages']) #test ok.
        
        #custom image part
        temp = productImages
        #print(temp)
        tempSerializer = self.get_serializer(instance)
        print(tempSerializer.data['id']) #test ok.
        #now getting all the images for a perticular product.
        images=temp.objects.filter(product_id=tempSerializer.data['id'])
        ourImageCount=0
        for image in images:
            "tatking the count of total images for the product."
            ourImageCount+=1
            #print(image.images)
        print(f"outImageCount={ourImageCount}") #test ok.
        sentImageCount=0
        if 'productimages' in request.data:
            for sentImage in request.data['productimages']:
                sentImageCount+=1
                #print(f"sentImage: {sentImage['images']}")
        print(f"sentImageCount={sentImageCount}")
        count=0
        if sentImageCount>0 and ourImageCount>0:
            for image in images:
                print(f"our-image: {image.images}")
                print(f"sent-image: {request.data['productimages'][count]['images']}")
                image.image_url=request.data['productimages'][count]['images']
                img_temp = tempfile.NamedTemporaryFile(delete = True)
                img_temp.write(urllib.request.urlopen(image.image_url).read())
                img_temp.flush()
                image.images.save("image.png", File(img_temp))
                image.save()
                print("image saved")
                count+=1;
                if(count>=sentImageCount):
                    break;

        #performing both product and product images update.
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

   
        """response = Response()
        response.data={
            'message':'test message.'
        }"""
        return product



#custom create model mixin
api_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS)
class CreateModelMixin:
    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):
        #custom model Creation
        token = self.request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Not authenticated.")
        try:
            payload = jwt.decode(token,'byte cipher', algorithm=['HS256']) 
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed("Jwt Token expired")
        users = CustomUser.objects.filter(id=payload['id']).first()
        #print(users) #test ok
        userserializer = customUserSerializer(users)
        user_id=userserializer.data['id']
        print(f"user id: {user_id}")
        print(f"request.data: {request.data}")
        
        #adding into request.data
        print(type(request.data)) #test ok.
        request.data["users"] = users
        print(f"updated request.data: {request.data}")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #self.perform_create(serializer)

        #custom creation of products
        if 'color' in request.data:
            "since color is optional"
            tempProduct=Product(user=users,name=request.data["name"],price=request.data["price"],color=request.data["color"])
        else:
            tempProduct=Product(user=users,name=request.data["name"],price=request.data["price"])
        tempProduct.save()

        #custom creation of product images
        if 'productimages' in request.data:
            for sentImage in request.data['productimages']:
                ""
                print(sentImage['images']) #test ok.
                image_url = sentImage['images']
                #image.image_url=request.data['productimages'][count]['images']
                img_temp = tempfile.NamedTemporaryFile(delete = True)
                img_temp.write(urllib.request.urlopen(image_url).read())
                img_temp.flush()
                #image.images.save("image.png", File(img_temp))
                #image.save()
                tempProductImage=productImages(image_url=image_url)
                tempProductImage.product=tempProduct
                tempProductImage.images.save("image.png", File(img_temp))
                tempProductImage.save()
                print("image saved.")

        headers = self.get_success_headers(serializer.data)
        return Response({'msg':'Product added succesfully'}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
class addProduct(CreateModelMixin,generics.CreateAPIView):
    "All done via custom model mixin"
    serializer_class = productCreateSerializer
    #lookup_field="id"


class searchProduct(generics.ListCreateAPIView):
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

        #self.kwargs['id'] #TODO
        keyword = self.kwargs.get('keyword','Null*&^%$')
        value = self.kwargs.get('value','Null*&^%$')
        print(keyword)
        print(type(value))
        print(value)
        posibleKeywords=['id','name','price','color']
        if keyword in posibleKeywords:
            ""
            match keyword:
                case "id":
                    ""
                    print("id case")
                    try:
                        id=int(value)
                    except:
                        raise NotAcceptable("We do not accept such values, Enter a proper id.") 
                    print(f"id={id}")
                    product = Product.objects.filter(user_id=serializer.data['id'],id=id)
                case "name":
                    ""
                    print("name case")
                    name=value
                    product = Product.objects.filter(user_id=serializer.data['id'],name=name)
                case "price":
                    ""
                    print("price case")
                    try:
                        price=int(value)
                    except:
                        raise NotAcceptable("We do not accept such values, Enter a proper price.") 
                    print(f"price={price}")
                    product = Product.objects.filter(user_id=serializer.data['id'],price=price)
                case "color":
                    ""
                    print("color case")
                    color=value
                    product = Product.objects.filter(user_id=serializer.data['id'],color=color)
        

        if not product:
            ""
            raise NotFound("Your Search result yeilded 0 products.")
        #print(product) #test ok!
        return product
