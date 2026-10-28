from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from .models import UserRole

def farmer_required(view_func):
    """Allows access only to users with the FARMER role."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        if request.user.role != UserRole.FARMER:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """Allows access only to users with the ADMIN role or is_superuser."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return user_passes_test(lambda u: False)(view_func)(request, *args, **kwargs)
        if request.user.role != UserRole.ADMIN and not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view