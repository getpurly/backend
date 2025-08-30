from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        from purly.approval.models import Approval

        if request.user.is_staff or request.user.is_superuser:
            return True

        if isinstance(obj, Approval):
            return obj.approver_id == request.user.id  # type: ignore

        return obj.owner_id == request.user.id


class IsAdminOrReadOnlyAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )
