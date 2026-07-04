from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Stricter rate limit for login endpoint.
    Prevents brute-force password attacks.
    """
    scope = "login"


class StandardUserThrottle(UserRateThrottle):
    """
    Standard rate limit for authenticated API requests.
    100 requests per minute per user.
    """
    scope = "user"
