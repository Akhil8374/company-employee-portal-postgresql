from rest_framework.response import Response
from rest_framework import status


class SuccessResponse(Response):
    """
    Company standard success response.

    Format:
    {
        "success": true,
        "message": "...",
        "data": { ... }
    }
    """

    def __init__(
        self,
        data=None,
        message="Success",
        status_code=status.HTTP_200_OK,
        **kwargs,
    ):
        response_data = {
            "success": True,
            "message": message,
            "data": data if data is not None else {},
        }
        super().__init__(data=response_data, status=status_code, **kwargs)
