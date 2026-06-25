from django.shortcuts import render

def home(request):
    return render(request, 'employees/home.html')

def about(request):
    return render(request, 'employees/about.html')

def contact(request):
    return render(request, 'employees/contact.html')

def employees(request):
    employee_list = [
        {"id": 1, "name": "Akhil", "department": "IT"},
        {"id": 2, "name": "Rahul", "department": "HR"},
        {"id": 3, "name": "Priya", "department": "Finance"},
    ]

    return render(
        request,
        'employees/employees.html',
        {'employees': employee_list}
    )