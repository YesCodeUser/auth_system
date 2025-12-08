from rest_framework import permissions


class MyBasePermission(permissions.BasePermission):
    permission_code = None

    def has_permission(self, request, view):
        from users.models import RolePermission

        return RolePermission.objects.filter(
            role__userrole__user=request.user,
            permission__code=self.permission_code
        ).exists()


class CanViewSelf(MyBasePermission):
    permission_code = 'self.view'
                                                      

class CanEditSelf(MyBasePermission):
    permission_code = 'self.edit'


class CanDeleteSelf(MyBasePermission):
    permission_code = 'self.delete'
