from django import forms
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["profile_picture", "username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "readonly": True}),
            "email": forms.EmailInput(attrs={"class": "form-control", "readonly": True}),
        }
