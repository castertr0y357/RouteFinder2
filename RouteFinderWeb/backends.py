from typing import Any, Optional
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

class EmailBackend(ModelBackend):
    def authenticate(self, request: Optional[HttpRequest], username: Optional[str] = None, password: Optional[str] = None, **kwargs: Any) -> Optional[AbstractBaseUser]:
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            # Check if username is an email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Fallback to standard username check
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
