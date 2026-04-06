from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# Registration Form
class UserRegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','email','password1','password2']

        widgets={
            'username':forms.TextInput(attrs={ 'class': 'user-input'}),
            'email':forms.EmailInput(attrs={'class':'email-input'}),
            'password1':forms.PasswordInput(attrs={'class':'password1-input'}),
            'password2':forms.PasswordInput(attrs={'class':'password2-input'})
        }
        
class UserLoginForm(AuthenticationForm):
    pass