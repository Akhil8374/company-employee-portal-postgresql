from rest_framework.exceptions import NotFound

from api.repositories import UserRepository


class UserService:
    """
    Business logic layer for User operations.
    """

    def __init__(self):
        self.repository = UserRepository()

    def get_user(self, pk):
        """
        Get a single user by ID.
        Raises NotFound if user doesn't exist.
        """
        user = self.repository.get_by_id(pk)
        if user is None:
            raise NotFound(f"User with id {pk} not found.")
        return user

    def get_user_by_username(self, username):
        """
        Get a single user by username.
        Raises NotFound if user doesn't exist.
        """
        user = self.repository.get_by_username(username)
        if user is None:
            raise NotFound(f"User '{username}' not found.")
        return user

    @staticmethod
    def blacklist_refresh_token(refresh_token):
        """
        Blacklist a refresh token (for logout).
        Requires rest_framework_simplejwt.token_blacklist in INSTALLED_APPS.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except TokenError:
            return False
