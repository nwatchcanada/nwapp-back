from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError


class NWAppPasswordlessAuthenticationBackend(ModelBackend):
    def authenticate(self, request, user_id=0, **kwargs):
        """
        Allow users to log in without password, simply knowing the `user_id`
        is suffice to be granted access to the system.
        """
        try:
            return get_user_model().objects.get(pk=user_id)
        except get_user_model().DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class NWAppEmailPasswordAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username="", password="", **kwargs):
        """
        Allow users to log in with their email address and provide application
        specific validation messages.
        """
        try:
            user = get_user_model().objects.get(email__iexact=username)

            # Users whom have not activated their account cannot access our
            # application because this is the policy we want to enforce.
            if not user.was_email_activated:
                return None

            if check_password(password, user.password):
                return user
            else:
                return None
        except get_user_model().DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None
        except Exception as e:
            return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
