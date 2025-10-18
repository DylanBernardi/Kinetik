from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

# Dynamically retrieve your custom model
Usuario = get_user_model()


class EmailBackend(ModelBackend):
    """
    Allows users to log in using their email address.
    It uses the 'username' argument (which will contain the email from the view)
    to search the 'email' field in the database.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # The 'username' variable here contains the input from the email field
        if not username:
            return None

        try:
            # 1. Lookup the user by their email address (case-insensitive lookup)
            user = Usuario.objects.get(email__iexact=username)
        except Usuario.DoesNotExist:
            return None

        # 2. Check the password hash securely
        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        """Required by the ModelBackend interface."""
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
