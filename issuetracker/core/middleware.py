"""Middleware for `core` app."""
from threading import local


_thread_locals = local()


def get_current_user():
    """Return the current user, if exist, otherwise returns None."""
    return getattr(_thread_locals, 'user', None)


def current_user_storage(get_response):
    """Return middleware that allows to get current user anywhere."""
    def middleware(request):
        _thread_locals.user = request.user
        return get_response(request)
    return middleware
