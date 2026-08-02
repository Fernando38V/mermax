import requests
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.wrappers import ApiError, api_post, api_get

def dashboard_kpis(request):
    """
    RF-12: Muestra el Dashboard interactivo consumiendo la API de reportes.
    Soporta filtrado opcional por fechas 'desde' y 'hasta'.
    """
    token = request.session.get('api_token')
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    
    # Construcción dinámica de parámetros para la API
    params = []
    if desde:
        params.append(f"desde={desde}")
    if hasta:
        params.append(f"hasta={hasta}")
        
    endpoint = '/reportes/dashboard/'
    if params:
        endpoint += '?' + '&'.join(params)

    try:
        respuesta = api_get(endpoint, token=token)
        kpi_data = respuesta if isinstance(respuesta, dict) else {}
    except Exception:
        kpi_data = {
            'resumen': {'eventos': 0, 'piezas_mermadas': 0, 'impacto_economico': 0, 'lineas_en_alerta': 0},
            'por_linea': [],
            'causas_raiz': []
        }
        messages.error(request, "Error de comunicación con la API de reportes para el Dashboard.")

    return render(request, 'reportes/dashboard_kpis.html', {
        'kpi_data': kpi_data,
        'desde_actual': desde,
        'hasta_actual': hasta,
    })

def lista_alertas(request):
    token = request.session.get('api_token')
    estado = request.GET.get('estado', 'ACTIVA')
    q = request.GET.get('q', '')
    
    endpoint = '/reportes/alertas/'
    if estado and estado != 'TODAS':
        endpoint += f"?estado={estado}"
        
    try:
        respuesta = api_get(endpoint, token=token)
        alertas = respuesta if isinstance(respuesta, list) else respuesta.get('results', [])
        
        if q and isinstance(alertas, list):
            alertas = [
                a for a in alertas 
                if q.lower() in str(a.get('kpi_nombre', '')).lower() 
                or q.lower() in str(a.get('linea_nombre', '')).lower()
                or q in str(a.get('num', ''))
            ]
    except Exception:
        alertas = []
        messages.error(request, "Error de comunicación con la API de reportes.")

    return render(request, 'reportes/alertas_umbral.html', {
        'alertas': alertas,
        'estado_actual': estado,
        'busqueda_actual': q,
    })

def evaluar_alertas(request):
    token = request.session.get('api_token')

    try:
        respuesta = api_post('/reportes/alertas/evaluar/', data={}, token=token)
        
        mensaje = (
            respuesta.get('mensaje', 'Evaluación de KPIs realizada con éxito.')
            if isinstance(respuesta, dict) else 'Evaluación de KPIs realizada con éxito.'
        )
        messages.success(request, mensaje)

    except ApiError as e:
        data = getattr(e, 'detail', {})
        mensaje_error = (
            data.get('error', 'No se pudo realizar la evaluación de KPIs.')
            if isinstance(data, dict) else 'No se pudo realizar la evaluación de KPIs.'
        )
        messages.error(request, mensaje_error)

    except Exception:
        messages.error(request, 'Error de conexión con el servidor de la API.')

    return redirect('reportes:alertas_umbral')

def atender_alerta(request, num):
    token = request.session.get('api_token')

    if request.method == 'POST':
        observaciones = (
            request.POST.get('observaciones') or 
            request.POST.get('observacion') or 
            request.POST.get('comentario') or 
            ''
        ).strip()
        
        if not observaciones:
            messages.error(request, "La observación es obligatoria para atender una alerta.")
            return redirect('reportes:alertas_umbral')
            
        try:
            respuesta = api_post(
                f'/reportes/alertas/{num}/atender/',
                data={'observaciones': observaciones},
                token=token
            )
            messages.success(request, f"Alerta ALT-{num} atendida correctamente.")

        except ApiError as e:
            detalle = getattr(e, 'detail', e)

            if isinstance(detalle, dict):
                primer_campo = next(iter(detalle))
                valor_error = detalle[primer_campo]
                if isinstance(valor_error, list):
                    msg_error = f"{primer_campo}: {valor_error[0]}"
                else:
                    msg_error = f"{primer_campo}: {valor_error}"
            else:
                msg_error = str(detalle)

            messages.error(request, f"No se pudo atender la alerta. ({msg_error})")

        except Exception as e:
            messages.error(request, "Error de conexión al atender la alerta.")
            
    return redirect('reportes:alertas_umbral')

def configurar_umbrales_view(request):
    token = request.session.get('api_token')

    if request.method == 'POST':
        linea_id = request.POST.get('linea_produccion')
        valor = request.POST.get('valor')
        indicador = request.POST.get('indicador_kpi', 'PCT_SCRAP')

        payload = {
            'linea_produccion': linea_id,
            'indicador_kpi': indicador,
            'valor': valor,
            'activo': True
        }

        try:
            res = api_post('/reportes/umbrales/', payload, token=token)
            if 'num' in res or 'valor' in res:
                messages.success(request, "Umbral actualizado correctamente.")
            else:
                messages.error(request, "No se pudo actualizar el umbral.")
        except Exception:
            messages.error(request, "Error de comunicación con el servidor API.")

        return redirect('reportes:configurar_umbrales')

    umbrales = api_get('/reportes/umbrales/', token=token)
    lineas = api_get('/catalogos/lineas/', token=token)

    return render(request, 'reportes/umbrales.html', {
        'umbrales': umbrales if isinstance(umbrales, list) else [],
        'lineas': lineas if isinstance(lineas, list) else [],
    })