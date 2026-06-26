# Company Employee Portal

## Project Overview

The Company Employee Portal is a Django-based Employee Management System integrated with PostgreSQL. It allows administrators to manage employee and department information through the Django Admin Panel.

---

## Features

- PostgreSQL Database Integration
- Department Management
- Employee Management
- Django ORM Operations
- Django Admin Panel
- Employee Search
- Employee Filter by Department
- CRUD Operations (Create, Read, Update, Delete)

---

## Technologies Used

- Python 3.14
- Django
- PostgreSQL
- psycopg2-binary
- Git
- GitHub

---

## Project Structure

```
company_portal/
│
├── company_portal/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── employees/
│   ├── migrations/
│   ├── models.py
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── screenshots/
├── manage.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd company_portal
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure PostgreSQL

Update the PostgreSQL database settings in:

```
company_portal/settings.py
```

---

## Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Create Superuser

```bash
python manage.py createsuperuser
```

---

## Run the Project

```bash
python manage.py runserver
```

Open your browser:

Home Page

```
http://127.0.0.1:8000/
```

Admin Panel

```
http://127.0.0.1:8000/admin/
```

---

## Django ORM Examples

Count Employees

```python
Employee.objects.count()
```

Employees with Salary Greater Than 50000

```python
Employee.objects.filter(salary__gt=50000)
```

Employees Ordered by Salary

```python
Employee.objects.order_by("-salary")
```

---

## Database Models

### Department

- name
- description
- created_at
- updated_at

### Employee

- employee_id
- first_name
- last_name
- email
- phone
- salary
- joining_date
- designation
- department
- status
- created_at
- updated_at

---

## Screenshots

- PostgreSQL Database
- Django Admin Panel
- Employee Management
- Department Management

---

## Author

**Rauthrao Akhil**

GitHub: https://github.com/Akhil8374