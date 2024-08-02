from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.

    This permission grants read-only access to any request if the method is considered "safe"
    (e.g., GET, HEAD, OPTIONS). For methods that potentially modify resources (e.g., POST, PUT, DELETE),
    this permission checks if the user making the request is the owner of the object.

    The ownership check depends on the object having an 'owner' attribute which matches the current user.
    """
    def has_object_permission(self, request, view, obj):
        """
        Return True if the request is a safe method, or if the current user is the owner of the object.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

    def has_permission(self, request, view):
        """
        Return True if the request should be permitted for viewset actions like retrieve, update, and destroy,
        or if it's a non-viewset view and the method is safe. Also checks object-level permissions if necessary.
        """
        if hasattr(view, 'action'):
            if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
                obj = view.get_object()
                return self.has_object_permission(request, view, obj)
            return True
        else:
            if request.method in permissions.SAFE_METHODS:
                return True
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                obj = view.get_object()
                return self.has_object_permission(request, view, obj)
            return True
