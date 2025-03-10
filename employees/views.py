from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee
from .forms import EmployeeForm
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from orders.models import Order
from django.db.models import Q



# Helper function to check if the user is an admin
def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin, login_url='login')
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})

@user_passes_test(is_admin, login_url='login')
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)  # Don't save yet
            employee.created_by = request.user  # Set the currently logged-in user
            employee.save()  # Save the employee
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_add.html', {'form': form})

@user_passes_test(is_admin, login_url='login')
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_edit.html', {'form': form, 'employee': employee})

@user_passes_test(is_admin, login_url='login')
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

def employee_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the employee using name and password
        try:
            employee = Employee.objects.get(name=username)  # Get employee by name
            if check_password(password, employee.password):  # Verify password
                # Store the employee ID in the session to track the logged-in employee
                request.session['employee_id'] = employee.employee_id
                request.session['employee_area'] = employee.area.area
                
                messages.success(request, "Login successful")
                return redirect('employee_dashboard')  # Redirect to the employee dashboard
            else:
                messages.error(request, "Invalid password")  # If password doesn't match
        except Employee.DoesNotExist:
            messages.error(request, "Employee not found")  # If no employee matches the name

    return render(request, 'employees/employee_login.html')


def employee_dashboard(request):
    # Check if the employee is logged in
    employee_id = request.session.get('employee_id')
    if not employee_id:
        messages.error(request, "You must be logged in to access the dashboard.")
        return redirect('employee_login')

    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        messages.error(request, "Employee not found.")
        return redirect('employee_login')

    # Pass the manage_order_type to the template
    context = {
        'employee': employee,
        'manage_order_type': employee.manage_order_type,
    }
    return render(request, 'employees/employee_dashboard.html', context)


def employee_logout(request):
    logout(request)
    return redirect('employee_login')  # Redirect to login page after logout

def manage_orders(request):
    # Fetch the employee area from the session
    employee_id = request.session.get('employee_id')
    employee = Employee.objects.get(employee_id=employee_id)
    employee_area = request.session.get('employee_area')
    print(employee_area)
    if not employee_area:
        # Handle missing employee area
        messages.error(request, "No area is assigned to the employee.")
        return redirect('employee_dashboard')

    # Fetch orders that match the employee area and are Pending
    orders = Order.objects.filter(
        Q(shipping_details__area=employee_area),  # Match area
        Q(status='Pending') | Q(status='Shipping')  # Include both 'Pending' and 'Shipping' statuses
    ).select_related('shipping_details')
    
    context = {
        'orders': orders,
        'employee_area': employee_area,
        'manage_order_type': employee.manage_order_type,
    }

    return render(request, 'employees/employee_task.html', context)

def subscription_orders(request):
    # Fetch the employee area from the session
    employee_id = request.session.get('employee_id')
    employee = Employee.objects.get(employee_id=employee_id)
    employee_area = request.session.get('employee_area')
    print(employee_area)
    if not employee_area:
        # Handle missing employee area  
        messages.error(request, "No area is assigned to the employee.")
        return redirect('employee_dashboard')

    # Fetch orders that match the employee area and are Pending
    orders = Order.objects.filter(
        Q(shipping_details__area=employee_area),  # Match area
        Q(status='Pending') | Q(status='Shipping')  # Include both 'Pending' and 'Shipping' statuses
    ).select_related('shipping_details')
    
    context = {
        'orders': orders,
        'employee_area': employee_area,
        'manage_order_type': employee.manage_order_type,
    }

    return render(request, 'employees/subscription_task.html', context)
