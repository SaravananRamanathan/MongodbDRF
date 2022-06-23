from django.shortcuts import render
from rest_framework import generics,permissions
from ui.models import Product
from .serializers import productSerializer
# Create your views here.

class getAllProduct(generics.ListAPIView):
    ""
    #specify a serializer class.
    serializer_class = productSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        print(f"user id: {user_id}")
        return Product.objects.filter(id=user_id)