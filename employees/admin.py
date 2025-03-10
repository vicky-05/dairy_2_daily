from django.contrib import admin
from .models import Employee
from import_export.admin import ExportMixin
from django.utils.translation import gettext_lazy as _
from import_export import resources

class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee
        fields = ('employee_id', 'name', 'phone_number', 'area', 'joining_date', 'salary', 'created_by')
        export_order = ('employee_id', 'name', 'phone_number', 'area', 'joining_date', 'salary', 'created_by')
@admin.register(Employee)
class EmployeeAdmin(ExportMixin,admin.ModelAdmin):
    resource_class = EmployeeResource
    list_display = ('employee_id', 'name', 'phone_number', 'area', 'joining_date', 'salary', 'created_by')
    search_fields = ('name', 'phone_number', 'area__area')  # Use area__area for the linked PincodeArea
    list_filter = ('area', 'joining_date','salary')
    ordering = ('-joining_date',)
