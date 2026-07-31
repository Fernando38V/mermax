import math
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import generic
from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get, api_post


def _catalogo(ruta, token):
    try:
        datos = api_get(ruta, token=token)
    except ApiError:
        return []
    if isinstance(datos, dict):
        return datos.get('results', [])
    return datos


@method_decorator(login_required_api, name='dispatch')
class BandejaRecepcion(generic.View):
    template_name = 'recepciones/bandeja.html'
    PAGE_SIZE = 10

    def get(self, request):
        token = request.session.get('api_token')

        filtros = {'estado': 'REGISTRADA'}
        for campo in ('linea', 'tipo_merma', 'componente', 'fecha'):
            valor = request.GET.get(campo)
            if valor:
                filtros[campo] = valor

        page = request.GET.get('page', '1')
        filtros['page'] = page

        try:
            respuesta = api_get('/mermas/registro/list/', token=token, params=filtros)
        except ApiError:
            respuesta = {'results': [], 'count': 0}

        mermas = respuesta.get('results', []) if isinstance(respuesta, dict) else respuesta
        count = respuesta.get('count', 0) if isinstance(respuesta, dict) else len(mermas)

        total_paginas = max(1, math.ceil(count / self.PAGE_SIZE))
        try:
            pagina_actual = int(page)
        except ValueError:
            pagina_actual = 1

        filtros_sin_pagina = request.GET.copy()
        filtros_sin_pagina.pop('page', None)
        querystring_filtros = filtros_sin_pagina.urlencode()

        filtros_activos = any(
            request.GET.get(campo)
            for campo in ('linea', 'tipo_merma', 'componente', 'fecha')
        )

        return render(request, self.template_name, {
            'mermas': mermas,
            'lineas': _catalogo('/catalogos/lineas/', token),
            'tipos_merma': _catalogo('/catalogos/tipos-merma/', token),
            'componentes': _catalogo('/catalogos/componentes/', token),
            'filtros': request.GET,
            'pagina_actual': pagina_actual,
            'total_paginas': total_paginas,
            'rango_paginas': range(max(1, pagina_actual - 2), min(total_paginas, pagina_actual + 2) + 1),
            'querystring_filtros': querystring_filtros,
            'filtros_activos': filtros_activos,
        })


@method_decorator(login_required_api, name='dispatch')
class ConfirmarRecepcion(generic.View):
    template_name = 'recepciones/confirmar.html'

    def get(self, request, folio):
        token = request.session.get('api_token')
        try:
            detalle = api_get(f'/mermas/registro/detail/{folio}/', token=token)
        except ApiError:
            detalle = {}

        return render(request, self.template_name, {
            'folio': folio,
            'cantidad_reportada': detalle.get('cantidad'),
            'valores': {},
            'errores': {},
        })

    def post(self, request, folio):
        token = request.session.get('api_token')

        cantidad_reportada_raw = request.POST.get('cantidad_reportada')
        cantidad_recibida_raw = request.POST.get('cantidad_recibida', '').strip()
        motivo_reporte = request.POST.get('motivo_reporte', '').strip()

        try:
            reportada = float(cantidad_reportada_raw)
            recibida = float(cantidad_recibida_raw)
        except (TypeError, ValueError):
            messages.error(request, 'Cantidad inválida.')
            return render(request, self.template_name, {
                'folio': folio,
                'cantidad_reportada': cantidad_reportada_raw,
                'valores': request.POST,
                'errores': {},
            })

        if reportada == recibida:
            try:
                api_post(
                    f'/mermas/recepcion/confirmar/{folio}/',
                    {'observaciones': motivo_reporte or 'Sin observaciones'},
                    token=token,
                )
                messages.success(request, f'Recepción de {folio} confirmada. Solicitud de inspección generada.')
                return redirect('recepciones:bandeja')
            except ApiError as e:
                errores = e.detail if isinstance(e.detail, dict) else {'error': [str(e.detail)]}
                return render(request, self.template_name, {
                    'folio': folio,
                    'cantidad_reportada': cantidad_reportada_raw,
                    'valores': request.POST,
                    'errores': errores,
                })

        if not motivo_reporte:
            return render(request, self.template_name, {
                'folio': folio,
                'cantidad_reportada': cantidad_reportada_raw,
                'valores': request.POST,
                'errores': {},
                'requiere_motivo': True,
            })

        payload = {
            'cantidad_reportada': reportada,
            'cantidad_recibida': recibida,
            'motivo_reporte': motivo_reporte,
            'registro_merma': folio,
        }
        try:
            resultado = api_post('/mermas/discrepancias/create/', payload, token=token)
            messages.warning(
                request,
                f"Discrepancia {resultado.get('folio', '')} registrada. Flujo bloqueado hasta su resolución."
            )
            return redirect('recepciones:bandeja')
        except ApiError as e:
            errores = e.detail if isinstance(e.detail, dict) else {'error': [str(e.detail)]}
            return render(request, self.template_name, {
                'folio': folio,
                'cantidad_reportada': cantidad_reportada_raw,
                'valores': request.POST,
                'errores': errores,
                'requiere_motivo': True,
            })


@method_decorator(login_required_api, name='dispatch')
class DiscrepanciasAbiertas(generic.View):
    template_name = 'recepciones/discrepancias.html'

    def get(self, request):
        token = request.session.get('api_token')
        try:
            respuesta = api_get('/mermas/discrepancias/list/', token=token, params={'estado': 'ABIERTA'})
        except ApiError:
            respuesta = []

        discrepancias = respuesta.get('results', []) if isinstance(respuesta, dict) else respuesta

        # El backend solo filtra por 'estado'; reportó/fecha se filtran aquí
        reportadores = sorted({d.get('usuario_reporte_nombre') for d in discrepancias if d.get('usuario_reporte_nombre')})

        reporto = request.GET.get('reporto')
        fecha = request.GET.get('fecha')

        if reporto:
            discrepancias = [d for d in discrepancias if d.get('usuario_reporte_nombre') == reporto]
        if fecha:
            discrepancias = [d for d in discrepancias if str(d.get('fecha_reporte')) == fecha]

        filtros_activos = bool(reporto or fecha)

        return render(request, self.template_name, {
            'discrepancias': discrepancias,
            'reportadores': reportadores,
            'filtros': request.GET,
            'filtros_activos': filtros_activos,
        })


@method_decorator(login_required_api, name='dispatch')
class ResolverDiscrepancia(generic.View):
    template_name = 'recepciones/resolver.html'

    def get(self, request, folio):
        return render(request, self.template_name, {'folio': folio, 'valores': {}})

    def post(self, request, folio):
        token = request.session.get('api_token')
        motivo_resolucion = request.POST.get('motivo_resolucion', '').strip()

        try:
            api_post(
                f'/mermas/discrepancias/resolver/{folio}/',
                {'motivo_resolucion': motivo_resolucion},
                token=token,
            )
            messages.success(request, f'Discrepancia {folio} resuelta. Flujo reanudado.')
            return redirect('recepciones:discrepancias')
        except ApiError as e:
            errores = e.detail if isinstance(e.detail, dict) else {'error': [str(e.detail)]}
            mensaje = errores.get('motivo_resolucion', [str(e.detail)])[0] if isinstance(errores, dict) else str(e.detail)
            messages.error(request, mensaje)
            return render(request, self.template_name, {'folio': folio, 'valores': request.POST})