from enum import unique
from django import forms
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth.models import User
from userAccess.models import CustomUser as User
from django.core.exceptions import ValidationError




class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)#making sure we have the email to make email authetication....

    class Meta:
        model = User
        fields = ["username","email","password1","password2"]

    #making sure email is unique. or will conflict while log in via email in future...
    """
        TODO: validation tests pending.
    """
    def clean(self):
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return self.cleaned_data