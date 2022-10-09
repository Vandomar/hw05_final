from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=HTTPStatus.FORBIDDEN):
    return render(request, 'core/403csrf.html')


def server_error(request, reason=HTTPStatus.INTERNAL_SERVER_ERROR):
    return render(request, 'core/500.html')
