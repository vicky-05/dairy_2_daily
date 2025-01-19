from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'phone_number', 'area', 'joining_date', 'salary', 'created_by')
    search_fields = ('name', 'phone_number', 'area__area')  # Use area__area for the linked PincodeArea
    list_filter = ('area', 'joining_date')
    ordering = ('-joining_date',)
