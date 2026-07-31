import math
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.contrib import messages
import requests

from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get, api_post


@method_decorator(login_required_api, name='dispatch')
class AlertasInspeccion(generic.View):
    """Vista para listar las solicitudes de inspección pendientes (Alertas)."""
    template_name = 'inspecciones/alertas.html'

    def get(self, request):
        token = request.session.get('api_token')

        try:
            respuesta = api_get('/inspecciones/solicitudes/list/', token=token)
        except ApiError:
            respuesta = []

        if isinstance(respuesta, dict):
            solicitudes = respuesta.get('results', [])
        else:
            solicitudes = respuesta

        return render(request, self.template_name, {
            'solicitudes': solicitudes,
        })


@method_decorator(login_required_api, name='dispatch')
class IniciarInspeccion(generic.View):
    """
    Acción POST para cambiar el estado de la merma a 'INSPECCIO'.
    Endpoint API: /inspecciones/solicitudes/iniciar/<codigo_solicitud>/
    """

    def post(self, request, codigo_solicitud):
        token = request.session.get('api_token')
        
        endpoint = f'/inspecciones/solicitudes/iniciar/{codigo_solicitud}/'

        try:
            respuesta = api_post(endpoint, data={}, token=token)
            
            mensaje = (
                respuesta.get('mensaje', f'Inspección iniciada para {codigo_solicitud}.')
                if isinstance(respuesta, dict) else 'Inspección iniciada con éxito.'
            )
            messages.success(request, mensaje)

        except ApiError as e:
            data = getattr(e, 'data', {})
            mensaje_error = (
                data.get('error', 'No se pudo iniciar la inspección.')
                if isinstance(data, dict) else 'No se pudo iniciar la inspección.'
            )
            messages.error(request, mensaje_error)

        except requests.exceptions.ReadTimeout:
            messages.error(request, 'El servidor de la API no respondió a tiempo.')

        return redirect('inspecciones:alertas')


@method_decorator(login_required_api, name='dispatch')
class AtenderInspeccion(generic.View):
    """
    Vista y POST para emitir el Dictamen Final (RF-08, RF-09, RF-10).
    Endpoint API: /inspecciones/dictaminar/<codigo_solicitud>/
    """
    template_name = 'inspecciones/realizar_inspeccion.html'

    def get(self, request, codigo_solicitud):
        token = request.session.get('api_token')

        context = {
            'solicitud': {'codigo': codigo_solicitud},
            'proveedores': self._catalogo('/catalogos/proveedores/', token),
            'empresas_recicladoras': self._catalogo('/catalogos/empresas-recicladoras/', token),
            'metodos_destruccion': self._catalogo('/catalogos/metodos-destruccion/', token),
            'fecha_hoy': timezone.localdate(),
            'valores': {'codigo_solicitud': codigo_solicitud},
            'errores': {},
        }
        return render(request, self.template_name, context)

    def post(self, request, codigo_solicitud):
        token = request.session.get('api_token')
        endpoint = f'/inspecciones/dictaminar/{codigo_solicitud}/'

        payload = {
            'disposicion_final': request.POST.get('disposicion_final') or request.POST.get('dictamen'),
            'cantidad_ejecutada': request.POST.get('cantidad_ejecutada') or request.POST.get('cantidad_inspeccionada'),
            'observaciones': request.POST.get('observaciones', ''),
            'proveedor': request.POST.get('proveedor'),
            'motivo_rechazo': request.POST.get('motivo_rechazo'),
            'empresa_recicladora': request.POST.get('empresa_recicladora'),
            'peso_neto': request.POST.get('peso_neto'),
            'metodo_destruccion': request.POST.get('metodo_destruccion'),
            'folio_probatorio': request.POST.get('folio_probatorio'),
        }

        payload = {k: v for k, v in payload.items() if v not in (None, '')}

        try:
            respuesta = api_post(endpoint, payload, token=token)
            
            mensaje = (
                respuesta.get('mensaje', f'Dictamen registrado para {codigo_solicitud}.')
                if isinstance(respuesta, dict) else 'Dictamen emitido con éxito.'
            )
            messages.success(request, mensaje)
            return redirect('inspecciones:alertas')

        except ApiError as e:
            context = {
                'solicitud': {'codigo': codigo_solicitud},
                'proveedores': self._catalogo('/catalogos/proveedores/', token),
                'empresas_recicladoras': self._catalogo('/catalogos/empresas-recicladoras/', token),
                'metodos_destruccion': self._catalogo('/catalogos/metodos-destruccion/', token),
                'fecha_hoy': timezone.localdate(),
                'valores': request.POST,
                'errores': getattr(e, 'data', {}),
            }
            return render(request, self.template_name, context)

    def _catalogo(self, ruta, token):
        try:
            datos = api_get(ruta, token=token)
        except ApiError:
            return []
        if isinstance(datos, dict):
            return datos.get('results', [])
        return datos