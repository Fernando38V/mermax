from django.shortcuts import render

# Create your views here.

from django.contrib import messages
from django.shortcuts import redirect, render

from .wrappers import ApiError, api_post
from .decorators import login_required_api


def login_view(request):
    if request.session.get('api_token'):
        return redirect('home:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            data = api_post('/usuarios/login/', {'username': username, 'password': password})
        except ApiError as e:
            mensaje = 'Usuario o contraseña incorrectos' if e.status_code == 400 \
                else 'No se pudo conectar con el servidor. Intenta de nuevo.'
            messages.error(request, mensaje)
            return render(request, 'usuarios/login.html')

        # Guardamos el token y los datos del usuario en la sesión del
        # frontend. request.session usa el backend de sesiones de Django
        # (por default, en la BD del propio proyecto frontend).
        request.session['api_token'] = data['token']
        request.session['usuario'] = data['usuario']
        return redirect('home:dashboard')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    token = request.session.get('api_token')
    if token:
        try:
            api_post('/usuarios/logout/', token=token)
        except ApiError:
            pass  # aunque el backend falle, igual cerramos la sesión local

    request.session.flush()
    return redirect('home:login')


@login_required_api
def dashboard_view(request):
    """Vista de ejemplo para comprobar que la sesión quedó activa."""
    return render(request, 'dashboard/dashboard.html', {
        'usuario': request.session.get('usuario'),
    })
    
