from django import forms
from .models import Employee
from django.contrib.admin.widgets import AdminDateWidget


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'phone_number', 'date_of_birth', 'address', 'area', 'salary']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
