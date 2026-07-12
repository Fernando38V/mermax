from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def login_required_api(view_func):
    """
    Igual que @login_required de Django, pero revisa el token guardado
    en sesión (no el sistema de auth de Django, que aquí no se usa).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('api_token'):
            messages.warning(request, 'Debes iniciar sesión para continuar.')
            return redirect('home:login')
        return view_func(request, *args, **kwargs)
    return wrapper