from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOng(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_ong)


class IsAdminOngOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_admin_ong)


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_ong:
            return True
        owner = getattr(obj, "doador", None)
        return bool(owner and owner.user_id == request.user.id)
