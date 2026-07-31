import math
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import generic
from django.contrib import messages
import requests

from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get, api_post


@method_decorator(login_required_api, name='dispatch')
class AlertasInspeccion(generic.View):
    """Vista para listar las solicitudes de inspección con paginación y filtros."""
    template_name = 'inspecciones/alertas.html'

    def get(self, request):
        token = request.session.get('api_token')

        estado_filtro = request.GET.get('estado', 'TODAS').strip().upper()
        busqueda = request.GET.get('q', '').strip()
        numero_pagina = request.GET.get('page', 1)

        endpoint = '/inspecciones/solicitudes/list/'
        params = []
        
        if estado_filtro and estado_filtro != 'TODAS':
            params.append(f'estado={estado_filtro}')
        if busqueda:
            params.append(f'q={busqueda}')

        if params:
            endpoint += '?' + '&'.join(params)

        try:
            respuesta = api_get(endpoint, token=token)
        except Exception:
            respuesta = []

        if isinstance(respuesta, dict):
            solicitudes_list = respuesta.get('results', [])
        elif isinstance(respuesta, list):
            solicitudes_list = respuesta
        else:
            solicitudes_list = []

        paginator = Paginator(solicitudes_list, 10)
        
        try:
            page_obj = paginator.page(numero_pagina)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'solicitudes': page_obj.object_list,
            'estado_actual': estado_filtro,
            'busqueda_actual': busqueda,
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
            data = getattr(e, 'detail', {})
            mensaje_error = (
                data.get('error', 'No se pudo iniciar la inspección.')
                if isinstance(data, dict) else 'No se pudo iniciar la inspección.'
            )
            messages.error(request, mensaje_error)

        except requests.exceptions.ReadTimeout:
            messages.error(request, 'El servidor de la API no respondió a tiempo.')

        return redirect('inspecciones:alertas')


@method_decorator(login_required_api, name='dispatch')
class DictaminarInspeccion(generic.View):
    """Pantalla de Inspecciones para dictaminar mermas (RF-08, RF-09, RF-10)."""
    template_name = 'inspecciones/dictaminar.html'

    MAPEO_DICTAMEN = {
        'RF-08': 'RTN_PROV',
        'RF-08: DEVOLUCIÓN A PROVEEDOR': 'RTN_PROV',
        'RTN_PROV': 'RTN_PROV',
        
        'RF-09': 'RECICLAJE',
        'RF-09: RECICLAJE': 'RECICLAJE',
        'RECICLAJE': 'RECICLAJE',
        
        'RF-10': 'DESTR_CTRL',
        'RF-10: DESECHO CONTROLADO': 'DESTR_CTRL',
        'DESTR_CTRL': 'DESTR_CTRL',
    }

    def get(self, request, codigo_solicitud=None):
        token = request.session.get('api_token')

        context = {
            'codigo_solicitud_param': codigo_solicitud,
            'solicitudes_pendientes': self._catalogo('/inspecciones/solicitudes/list/', token),
            'proveedores': self._catalogo('/catalogos/proveedores/', token),
            'empresas_recicladoras': self._catalogo('/catalogos/empresas-recicladoras/', token),
            'metodos_destruccion': self._catalogo('/catalogos/metodos-destruccion/', token),
            'fecha_hoy': timezone.localdate(),
            'valores': {'codigo': codigo_solicitud} if codigo_solicitud else {},
            'errores': {},
        }
        return render(request, self.template_name, context)

    def post(self, request, codigo_solicitud=None):
        token = request.session.get('api_token')
        codigo = codigo_solicitud or request.POST.get('codigo') or request.POST.get('codigo_solicitud')

        if not codigo:
            context = self._obtener_contexto_base(request, token)
            context['errores'] = {'codigo': ['Debes seleccionar una solicitud de inspección.']}
            return render(request, self.template_name, context)

        # Mapear la opción seleccionada a las claves exactas que exige la API
        raw_dictamen = str(request.POST.get('disposicion_final', '')).strip().upper()
        dictamen_clean = self.MAPEO_DICTAMEN.get(raw_dictamen, raw_dictamen)

        # Convertir peso_neto a float si está presente
        peso_neto = request.POST.get('peso_neto')
        try:
            peso_neto = float(peso_neto) if peso_neto else None
        except ValueError:
            peso_neto = None

        payload = {
            'disposicion_final': dictamen_clean,
            'cantidad_ejecutada': request.POST.get('cantidad_ejecutada') or None,
            'observaciones': request.POST.get('observaciones', ''),
            'proveedor': request.POST.get('proveedor'),
            'motivo_rechazo': request.POST.get('motivo_rechazo'),
            'empresa_recicladora': request.POST.get('empresa_recicladora'),
            'peso_neto': peso_neto,
            'metodo_destruccion': request.POST.get('metodo_destruccion'),
            'folio_probatorio': request.POST.get('folio_probatorio'),
        }

        payload_limpio = {k: v for k, v in payload.items() if v not in (None, '')}

        try:
            respuesta = api_post(f'/inspecciones/dictaminar/{codigo}/', payload_limpio, token=token)
            mensaje = respuesta.get('mensaje', 'Dictamen emitido exitosamente.') if isinstance(respuesta, dict) else 'Dictamen emitido.'
            messages.success(request, mensaje)
            return redirect('inspecciones:dictaminar_inspeccion')

        except ApiError as e:
            errores = getattr(e, 'detail', {})
            print(">>> DETALLE ERROR BACKEND:", errores)
            
            context = self._obtener_contexto_base(request, token)
            context['codigo_solicitud_param'] = codigo
            context['valores'] = request.POST
            context['errores'] = errores if isinstance(errores, dict) else {'error': str(errores)}
            return render(request, self.template_name, context)

    def _obtener_contexto_base(self, request, token):
        return {
            'solicitudes_pendientes': self._catalogo('/inspecciones/solicitudes/list/', token),
            'proveedores': self._catalogo('/catalogos/proveedores/', token),
            'empresas_recicladoras': self._catalogo('/catalogos/empresas-recicladoras/', token),
            'metodos_destruccion': self._catalogo('/catalogos/metodos-destruccion/', token),
            'fecha_hoy': timezone.localdate(),
            'valores': {},
            'errores': {},
        }

    def _catalogo(self, ruta, token):
        try:
            datos = api_get(ruta, token=token)
            return datos.get('results', []) if isinstance(datos, dict) else datos
        except ApiError:
            return []