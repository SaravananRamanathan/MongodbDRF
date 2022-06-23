from urllib import response
from django.shortcuts import render
from rest_framework import generics,permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from ui.models import Product
from .serializers import productSerializer,customUserSerializer
from userAccess.models import CustomUser
from rest_framework.exceptions import AuthenticationFailed
import jwt,datetime

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
        ""
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed("Not authenticated.")
        try:
            payload = jwt.decode(token,'byte cipher', algorithm=['HS256']) 
        except jwt.exceptions.ExpiredSignatureError:
            ""
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
    ""
    #specify a serializer class.
    serializer_class = productSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        print(f"user id: {user_id}")
        return Product.objects.filter(id=user_id)