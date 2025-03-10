from django.db import models
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from authentication.models import PincodeArea  # ForeignKey to PincodeArea
from django.conf import settings
from django.shortcuts import render

class Employee(models.Model):
    ORDER_TYPE_CHOICES = [
        ('Subscription', 'Subscription Orders'),
        ('Product', 'Product Orders'),
        ('Both', 'Both Subscription and Product Orders'),  # Optional, for flexibility
    ]

    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    area = models.ForeignKey(
        PincodeArea, on_delete=models.CASCADE, related_name="employees"
    )  # Linked to PincodeArea
    date_of_birth = models.DateField()  # Date of Birth field
    joining_date = models.DateField(default=now)  # Default to current date
    salary = models.DecimalField(max_digits=10, decimal_places=2)  # Salary field
    password = models.CharField(max_length=128)  # Store hashed password
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employees"
    )  # Admin who added the employee
    manage_order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPE_CHOICES,
        default='Product',  # Default to Product Orders
        help_text="Specify if the employee manages Subscription or Product orders.",
    )

    def save(self, *args, **kwargs):
        if not self.password:
            # Generate a password using part of the name and year of DOB
            name_part = self.name[:4].lower()
            dob_year = self.date_of_birth.year
            raw_password = f"{name_part}{dob_year}"
            self.password = make_password(raw_password)  # Hash the password
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.area}"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

