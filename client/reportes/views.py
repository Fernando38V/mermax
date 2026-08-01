import requests
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from usuarios.wrappers import ApiError, api_post, api_get

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