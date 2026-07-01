import time
import logging

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("application")
security_logger = logging.getLogger("security")


# ══════════════════════════════════════════════════════════════
# 1. Request Logging Middleware
# ══════════════════════════════════════════════════════════════

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Logs every incoming request with:
    - URL, HTTP Method, IP Address, User, Response Time
    Writes to logs/request.log via the 'request' logger.
    """

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        start_time = getattr(request, "_start_time", None)
        duration = (time.time() - start_time) * 1000 if start_time else 0

        user = request.user if hasattr(request, "user") and request.user.is_authenticated else "Anonymous"
        ip = self._get_client_ip(request)

        request_logger = logging.getLogger("request")
        request_logger.info(
            "Method=%s | URL=%s | User=%s | IP=%s | Duration=%.2fms | Status=%s",
            request.method,
            request.get_full_path(),
            user,
            ip,
            duration,
            response.status_code,
        )

        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


# ══════════════════════════════════════════════════════════════
# 2. Response Time Middleware
# ══════════════════════════════════════════════════════════════

class ResponseTimeMiddleware(MiddlewareMixin):
    """
    Calculates request processing time.
    If response time exceeds 500ms, logs it as a WARNING.
    """

    def process_request(self, request):
        request._response_time_start = time.time()

    def process_response(self, request, response):
        start = getattr(request, "_response_time_start", None)
        if start is None:
            return response

        duration_ms = (time.time() - start) * 1000

        response["X-Response-Time"] = f"{duration_ms:.2f}ms"

        if duration_ms > 500:
            logger.warning(
                "SLOW RESPONSE: %s %s took %.2fms (threshold: 500ms)",
                request.method,
                request.get_full_path(),
                duration_ms,
            )

        return response


# ══════════════════════════════════════════════════════════════
# 3. IP Restriction Middleware
# ══════════════════════════════════════════════════════════════

class IPRestrictionMiddleware(MiddlewareMixin):
    """
    Checks incoming requests against the BlockedIP model.
    If the client IP is blocked, returns 403 Forbidden.
    """

    def process_request(self, request):
        from audit_logs.models import BlockedIP

        ip = self._get_client_ip(request)

        if BlockedIP.objects.filter(ip_address=ip).exists():
            security_logger.warning(
                "BLOCKED IP attempted access: IP=%s | URL=%s | Method=%s",
                ip,
                request.get_full_path(),
                request.method,
            )
            return HttpResponseForbidden(
                "<h1>403 Forbidden</h1>"
                "<p>Your IP address has been blocked from accessing this system.</p>"
            )

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
