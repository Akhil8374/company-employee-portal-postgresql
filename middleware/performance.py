import logging
import time
from django.db import connection

logger = logging.getLogger("performance")


class PerformanceLoggingMiddleware:
    """
    Performance monitoring middleware.

    Logs every request at INFO level with:
    - Request URL, HTTP Method, SQL Query Count, Execution Time, User, Status Code

    If response time exceeds 500 ms, logs at WARNING level.

    NOTE: connection.queries is only populated when DEBUG=True.
    In production, use django-silk or django-debug-toolbar for profiling.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Reset query log for accurate count
        start_queries = len(connection.queries)
        start_time = time.time()

        response = self.get_response(request)

        # Calculate execution time in milliseconds
        execution_time = (time.time() - start_time) * 1000

        # SQL Queries Count (only accurate when DEBUG=True)
        sql_queries = len(connection.queries) - start_queries

        # Logged-in User
        user = (
            request.user.username
            if hasattr(request, "user") and request.user.is_authenticated
            else "Anonymous"
        )

        log_message = (
            f"URL={request.path} | "
            f"METHOD={request.method} | "
            f"USER={user} | "
            f"TIME={execution_time:.2f}ms | "
            f"SQL={sql_queries} | "
            f"STATUS={response.status_code}"
        )

        if execution_time > 500:
            # Slow request — log as WARNING to performance.log
            logger.warning(f"SLOW REQUEST | {log_message}")
        else:
            # Normal request — log at INFO level
            logger.info(log_message)

        return response
