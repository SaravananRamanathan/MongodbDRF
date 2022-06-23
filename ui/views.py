from django.shortcuts import render
from rest_framework.authtoken.models import Token
def home(response):
    ""
    userId=response.user.id
    #print(response.user.is_authenticated) #test ok
    
    if response.user.is_authenticated:
        token = Token.objects.filter(user_id=userId)
        if token:
            print(f"access token: {token[0]}")
            return render(response,"ui/home.html",{"token":token[0]})
    return render(response,"ui/home.html",{})
    return render(response,"ui/home.html",{}) #test ok.

def imageHandler(response,image:str):
    ""
    print(image)
    return render(response,"ui/images.html",{})