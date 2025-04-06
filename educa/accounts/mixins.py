from django.core.exceptions import PermissionDenied

class StudentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'student':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class TeacherRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'teacher':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class ParentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'parent':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)