# Company Employee Portal — Enterprise REST API Platform

## Project Overview

The Company Employee Portal REST API is a production-grade backend application built using Django REST Framework (DRF) and PostgreSQL. It has been completely refactored from a simple views-based application into an **Enterprise Standard Architecture**. 

The architecture strictly decouples business logic from HTTP handling by implementing a **Service Layer** and a **Repository (Data Access) Layer**. It features API versioning, standardized API response formats, global exception handling, an audit logging system, query optimization, caching, and rate limiting (throttling) to prevent abuse.

---

## Enterprise Features Implemented

* **Service-Oriented Architecture:** Business logic is moved entirely out of views into `EmployeeService`, `DepartmentService`, and `UserService`.
* **Repository Pattern:** Database interactions (ORM queries) are isolated in Repository classes with advanced query optimization (`select_related`, `prefetch_related`, `only`).
* **Nested Serializers:** Complex relationships (e.g., Department with nested Employees, Employee with nested Manager details) handled natively.
* **Standard API Responses:** Every endpoint uniformly returns `{ "success": true/false, "message": "...", "data": {} }`.
* **Global Exception Handler:** Custom DRF exception handler catches all validation, authentication, permission, and server errors to ensure they follow the standard error response format.
* **API Versioning:** Clear separation of endpoints via `/api/v1/...` and `/api/v2/...` URLs.
* **API Throttling & Caching:** Prevents brute-forcing (10/min for login) and general abuse (100/min for users). Heavy read endpoints are cached for 5 minutes.
* **Django Signals & Audit Logging:** Uses `post_save`, `post_delete`, and auth signals to track every `CREATE`, `UPDATE`, `DELETE`, `LOGIN`, and `LOGOUT` action automatically inside a dedicated `audit_logs` table.
* **JWT Authentication:** Secure token-based authentication featuring token blacklisting upon logout.
* **Role-Based Access Control (RBAC):** Custom permissions (`IsAdmin`, `IsHROrAdmin`, `IsManagerOrAbove`).

---

## Technologies Used

* Python 3.14
* Django 6.0
* Django REST Framework
* PostgreSQL
* Simple JWT (with token blacklisting)
* Postman
* Git & GitHub

---

## Project Structure

```text
company_portal/
│
├── api/
│   ├── exceptions/      # Global Exception Handler
│   ├── permissions/     # Role-Based Custom Permissions
│   ├── repositories/    # Database Data Access Layer
│   ├── responses/       # Standard Success/Error Response Classes
│   ├── serializers/     # Request/Response Validation & Formatting
│   ├── services/        # Core Business Logic Layer
│   ├── throttling/      # API Rate Limiting Classes
│   ├── urls/            # V1 & V2 URL Routing Configurations
│   └── views/           # Thin HTTP Handlers (Delegates to Services)
│
├── audit_logs/          # Django App for Tracking System Events
├── employees/           # Django Web App Models & UI
├── accounts/            # Custom User Models & Auth
├── company_portal/      # Main Django Settings & Config
└── requirements.txt
```

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd company_portal
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin (Superuser)

```bash
python manage.py createsuperuser
```

### 5. Run the Project

```bash
python manage.py runserver
```

---

## API Endpoints Overview

*Note: All APIs (except Login/Refresh) require a JWT Bearer Token in the Authorization header.*

### Authentication (V1)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login/` | JWT Login (Returns Access & Refresh) |
| POST | `/api/v1/auth/refresh/` | Refresh Access Token |
| POST | `/api/v1/auth/logout/` | Blacklist Refresh Token |

### Departments (V1)
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/v1/departments/` | List or Create Departments |
| GET/PUT/DELETE | `/api/v1/departments/{id}/` | Retrieve, Update, or Delete |
| GET | `/api/v1/departments/{id}/employees/` | Get Department with nested Employees |

### Employees (V1)
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/v1/employees/` | List (Cached) or Create Employees |
| GET/PUT/DELETE | `/api/v1/employees/{id}/` | Retrieve, Update, or Delete |

### Employees (V2 - Expanded View)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v2/employees/` | List with full nested Department & Manager details |

### Audit Logs (V1 - Admin Only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/audit-logs/` | List all system events (Supports filtering) |

---

## Git Workflow (Standard Operating Procedure)

For daily tasks, use the single-repository feature branch workflow:

```bash
# 1. Update your local development branch
git checkout development
git pull origin development

# 2. Create a feature branch for the task
git checkout -b feature/advanced-drf

# 3. Commit your logical work
git add .
git commit -m "feat: implement service layer architecture"
git commit -m "feat: add nested serializers"
# ...etc

# 4. Push to remote and open a Pull Request
git push -u origin feature/advanced-drf
```

---

## Author

**Rauthrao Akhil**
GitHub: https://github.com/Akhil8374
