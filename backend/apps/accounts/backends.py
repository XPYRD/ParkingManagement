from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class GroupOnlyPermissionBackend(ModelBackend):
    """只通过用户组和超级管理员判定权限，不读取用户直授权限。"""

    def _get_user_permissions(self, user_obj):
        return Permission.objects.none()
