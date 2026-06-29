from rest_framework.response import Response
from rest_framework import status


class ErrorResponse(Response):
    """
    Company standard error response.

    Format:
    {
        "success": false,
        "message": "...",
        "errors": { ... }
    }
    """

    def __init__(
        self,
        message="Something went wrong",
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
        **kwargs,
    ):
        response_data = {
            "success": False,
            "message": message,
            "errors": errors if errors is not None else {},
        }
        super().__init__(data=response_data, status=status_code, **kwargs)
