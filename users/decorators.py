from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(allowed_roles):
    """
    Decorator to restrict access based on user.role.
    Usage:
        @role_required(["admin", "store"])
        def my_view(...):
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # User not logged in
            if not request.user.is_authenticated:
                raise PermissionDenied("You are not logged in.")

            # Missing role attribute (fallback)
            if not hasattr(request.user, "role"):
                raise PermissionDenied("User role is not defined.")

            # Role not allowed
            if request.user.role not in allowed_roles:
                raise PermissionDenied("You do not have permission for this action.")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
