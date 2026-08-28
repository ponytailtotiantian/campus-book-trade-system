from django.contrib.auth.hashers import check_password

from apps.accounts.models import User


class UserModelBackend:
    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        if not user.is_active or not check_password(password, user.password_hash):
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
