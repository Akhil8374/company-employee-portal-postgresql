from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


# ─────────────────────────────────────────────────────────────────────────────
# Authentication Throttles (Module 7)
# ─────────────────────────────────────────────────────────────────────────────

class LoginRateThrottle(AnonRateThrottle):
    """
    Strict rate limit for the login endpoint.
    Prevents brute-force password attacks.
    Rate: 5 requests per minute per IP (anonymous).
    """
    scope = "login"


# ─────────────────────────────────────────────────────────────────────────────
# Employee API Throttles (Module 7)
# ─────────────────────────────────────────────────────────────────────────────

class StandardUserThrottle(UserRateThrottle):
    """
    Standard rate limit for authenticated API requests.
    Rate: 100 requests per minute per user.
    """
    scope = "user"


class EmployeeRateThrottle(UserRateThrottle):
    """
    Rate limit for Employee API endpoints.
    Rate: 100 requests per minute per authenticated user.
    Used on: /api/v1/employees/
    """
    scope = "employee"


# ─────────────────────────────────────────────────────────────────────────────
# Report API Throttles (Module 7)
# ─────────────────────────────────────────────────────────────────────────────

class ReportRateThrottle(UserRateThrottle):
    """
    Strict rate limit for Report API endpoints.
    Rate: 20 requests per minute per authenticated user.
    Used on: /api/v1/reports/
    """
    scope = "report"
