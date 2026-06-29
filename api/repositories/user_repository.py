from accounts.models import User


class UserRepository:
    """
    Data access layer for User model.
    All database queries for users go through this class.
    """

    @staticmethod
    def get_by_id(pk):
        """Get a single user by primary key, or None."""
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_username(username):
        """Get a single user by username, or None."""
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email):
        """Get a single user by email, or None."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_all():
        """Get all users."""
        return User.objects.all()
