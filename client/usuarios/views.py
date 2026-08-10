# Create your views here.

from django.shortcuts import redirect, render
from django.contrib import messages

from .wrappers import ApiError, api_post, api_get
from .decorators import login_required_api

def login_view(request):
    if request.session.get('api_token'):
        return redirect('usuarios:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            data = api_post('/usuarios/login/', {'username': username, 'password': password})
        except ApiError as e:
            mensaje = e.detail.get('non_field_errors', ['Usuario o contraseña incorrectos'])[0] if isinstance(e.detail, dict) else str(e.detail)
            messages.error(request, mensaje)
            return render(request, 'usuarios/login.html')

        # Guardamos el token y los datos del usuario en la sesión del
        # frontend. request.session usa el backend de sesiones de Django
        # (por default, en la BD del propio proyecto frontend).
        request.session['api_token'] = data['token']
        request.session['usuario'] = data['usuario']
        return redirect('usuarios:dashboard')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    token = request.session.get('api_token')
    if token:
        try:
            api_post('/usuarios/logout/', token=token)
        except ApiError:
            pass  # aunque el backend falle, igual cerramos la sesión local

    request.session.flush()
    return redirect('usuarios:login')

# Un endpoint de agregación por app, cada uno debe regresar ya el JSON
# con la forma exacta que espera el partial correspondiente (ver
# dashboard_partials/README_integracion.md). Así esta vista no tiene
# que transformar nada, solo pasar el dict de largo.
_DASHBOARD_ENDPOINT_POR_ROL = {
    'SUPER': '/mermas/dashboard-supervisor/',
    'ALMAC': '/mermas/dashboard-almacen/',
    'CALID': '/inspecciones/dashboard/',
    'ADMIN': '/usuarios/dashboard/',
}
 
 
@login_required_api
def dashboard_view(request):
    usuario = request.session.get('usuario')
    token = request.session.get('api_token')
 
    dash = {}
    endpoint = _DASHBOARD_ENDPOINT_POR_ROL.get(usuario.get('rol'))
 
    if endpoint:
        try:
            dash = api_get(endpoint, token=token)
        except ApiError:
            # No tronamos el dashboard si el agregado falla o el
            # endpoint todavía no existe en el backend; los partials
            # ya están protegidos para renderizar vacío con dash={}.
            messages.warning(request, 'No se pudieron cargar los indicadores del panel.')
 
    return render(request, 'dashboard/dashboard.html', {
        'usuario': usuario,
        'dash': dash,
    })
 
@login_required_api
def mi_perfil(request):
    token = request.session.get('api_token')
    
    try:
        perfil = api_get('/usuarios/mi-perfil/', token=token)
    except ApiError as e:
        messages.error(request, 'No se pudieron cargar los datos del perfil.')
        return redirect('usuarios:dashboard')
    
    return render(request, 'usuarios/mi_perfil.html', {
        'perfil': perfil,
    })
