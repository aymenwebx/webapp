from django.shortcuts import redirect
from django.urls import reverse


class UserTypeRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.user.is_authenticated and
                not request.path.startswith('/admin/') and
                request.path == reverse('course_list')):

            if request.user.user_type == 'student':
                return redirect('student_course_list')
            elif request.user.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif request.user.user_type == 'parent':
                return redirect('parent_dashboard')

        return response