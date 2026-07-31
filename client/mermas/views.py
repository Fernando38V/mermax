import math
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get, api_post, api_patch

@method_decorator(login_required_api, name='dispatch')
class ListMermas(generic.View):
    template_name = 'mermas/list_merma.html'
    PAGE_SIZE = 10

    def get(self, request):
        token = request.session.get('api_token')

        filtros = {}
        for campo in ('linea', 'tipo_merma', 'componente', 'estado', 'fecha'):
            valor = request.GET.get(campo)
            if valor:
                filtros[campo] = valor
        
        page = request.GET.get('page', '1')
        filtros['page'] = page
        
        try:
            respuesta = api_get('/mermas/registro/list/', token=token, params=filtros)
        except ApiError:
            respuesta = {'results': [], 'count': 0}

        if isinstance(respuesta, list):
            mermas = respuesta
            count = len(respuesta)
        else:
            mermas = respuesta.get('results', [])
            count = respuesta.get('count', 0)
        
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
            for campo in ('linea', 'tipo_merma', 'componente', 'estado', 'fecha')
        )
        print('filtros_activos: ', filtros_activos)
        return render(request, self.template_name, {
            'mermas': mermas,
            'lineas': self._catalogo('/catalogos/lineas/', token),
            'tipos_merma': self._catalogo('/catalogos/tipos-merma/', token),
            'componentes': self._catalogo('/catalogos/componentes/', token),
            'estados': self._catalogo('/catalogos/lookup/estados-flujo/', token),
            'filtros':request.GET,
            'pagina_actual': pagina_actual,
            'total_paginas': total_paginas,
            'rango_paginas': range(max(1, pagina_actual - 2), min(total_paginas, pagina_actual + 2) + 1),
            'querystring_filtros': querystring_filtros,
            'filtros_activos': filtros_activos,
        })

    def _catalogo(self, ruta, token):
        try:
            datos = api_get(ruta, token=token)
        except ApiError:
            return []
        if isinstance(datos, dict):
            return datos.get('results', [])
        return datos
    
@method_decorator(login_required_api, name='dispatch')
class CreateMermas(generic.View):
    template_name = 'mermas/create_merma.html'
    context = {}
    url_base = '/mermas/registro/create/'
    response = None
    
    def get(self, request):
        token = request.session.get('api_token')
        
        self.context = {
            'lineas': self._catalogo('/catalogos/lineas/', token),
            'tipos_merma': self._catalogo('/catalogos/tipos-merma/', token),
            'componentes': self._catalogo('/catalogos/componentes/', token),
            'estados': self._catalogo('/catalogos/lookup/estados-flujo/', token),
            'causa_raiz': self._catalogo('/catalogos/causas-raiz/', token),
            'fecha_hoy': timezone.localdate(),
            'valores': {},
            'errores': {},
        }
        return render(request, self.template_name, self.context)
        
    def _catalogo(self, ruta, token):
        try:
            datos = api_get(ruta, token=token)
        except ApiError:
            return []
        if isinstance(datos, dict):
            return datos.get('results', [])
        return datos
    
    def post(self, request):
        token = request.session.get('api_token')
        
        payload = {
            'cantidad': request.POST.get('cantidad'),
            'unidad': request.POST.get('unidad'),
            'descripcion': request.POST.get('descripcion'),
            'lote_material': request.POST.get('lote_material'),
            'componente': request.POST.get('componente'),
            'tipo_merma': request.POST.get('tipos_merma'),
            'causa_raiz': request.POST.get('causa_raiz'),
            'estacion_trabajo': request.POST.get('estacion'),
            'orden_produccion': request.POST.get('orden_produccion'),
        }
        
        try:
            respuesta = api_post(self.url_base, payload, token=token)
            
            return redirect('mermas:list_mermas')
            
        except ApiError as e:
            self.context = {
                'lineas': self._catalogo('/catalogos/lineas/', token),
                'tipos_merma': self._catalogo('/catalogos/tipos-merma/', token),
                'componentes': self._catalogo('/catalogos/componentes/', token),
                'estados': self._catalogo('/catalogos/lookup/estados-flujo/', token),
                'causa_raiz': self._catalogo('/catalogos/causas-raiz/', token),
                'fecha_hoy': timezone.localdate(),
                'valores': payload,
                'errores': getattr(e, 'data', {}),
            }
            
            return render(request, self.template_name, self.context)
    
@method_decorator(login_required_api, name='dispatch')
class EstacionesPorLinea(generic.View):

    def get(self, request):
        from django.http import JsonResponse

        token = request.session.get('api_token')
        linea = request.GET.get('linea')

        if not linea:
            return JsonResponse([], safe=False)

        try:
            estaciones = api_get(
                '/mermas/estaciones-por-linea/',
                token=token,
                params={'linea': linea}
            )
        except ApiError:
            return JsonResponse([], safe=False)

        if isinstance(estaciones, dict):
            estaciones = estaciones.get('results', [])

        return JsonResponse(estaciones, safe=False)


@method_decorator(login_required_api, name='dispatch')
class LotesPorComponente(generic.View):

    def get(self, request):
        from django.http import JsonResponse

        token = request.session.get('api_token')
        componente = request.GET.get('componente')

        if not componente:
            return JsonResponse([], safe=False)

        try:
            lotes = api_get(
                '/mermas/lotes-por-componente/',
                token=token,
                params={'componente': componente},
            )
        except ApiError:
            return JsonResponse([], safe=False)

        if isinstance(lotes, dict):
            lotes = lotes.get('results', [])

        return JsonResponse(lotes, safe=False)


@method_decorator(login_required_api, name='dispatch')
class OrdenesPorEstacion(generic.View):

    def get(self, request):
        from django.http import JsonResponse

        token = request.session.get('api_token')
        estacion = request.GET.get('estacion')

        if not estacion:
            return JsonResponse([], safe=False)

        try:
            ordenes = api_get(
                '/mermas/ordenes-por-estacion/',
                token=token,
                params={'estacion': estacion},
            )
        except ApiError:
            return JsonResponse([], safe=False)

        if isinstance(ordenes, dict):
            ordenes = ordenes.get('results', [])

        return JsonResponse(ordenes, safe=False)
    
class DetailMermas(generic.View):
    template_name = "mermas/detail_merma.html"
    context = {}
    url_base = '/mermas/registro/detail/'
    response = None

    def get(self, request, pk):
        token = request.session.get('api_token')
        
        self.url_base += str(pk) + '/'
        try:
            self.response = api_get(self.url_base, token=token)
        except ApiError:
            return redirect('mermas:list_mermas')
        
        self.context = {'merma': self.response}
        return render(request, self.template_name, self.context)
    
@method_decorator(login_required_api, name='dispatch')
class UpdateMermas(generic.View):
    template_name = "mermas/update_merma.html"
    url_base = '/mermas/registro/update/'
    
    def get(self, request, pk):
        token = request.session.get('api_token')
        try:
            merma = api_get(f'/mermas/registro/detail/{pk}/', token=token)
        except ApiError:
            return redirect('mermas:list_mermas')
        
        context = {
            'merma': merma,
            'tipo_merma': self._catalogo('/catalogos/tipos-merma/', token),
            'causa_raiz': self._catalogo('/catalogos/causas-raiz/', token),
            'errores': {},
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        token = request.session.get('api_token')
        payload = {
            'cantidad': request.POST.get('cantidad'),
            'tipo_merma': request.POST.get('tipo_merma'),
            'causa_raiz': request.POST.get('causa_raiz'),
        }
        try:
            api_patch(f'/mermas/registro/update/{pk}/', payload, token=token)
            return redirect('mermas:detail_mermas', pk=pk)

        except ApiError as e:
            try:
                merma = api_get(f'/mermas/registro/detail/{pk}/', token=token)
            except ApiError:
                return redirect('mermas:list_mermas')
            
            context = {
                'merma': merma, 
                'tipo_merma': self._catalogo('/catalogos/tipos-merma/', token),
                'causa_raiz': self._catalogo('/catalogos/causas-raiz/', token),
                'errores': getattr(e, 'data', {}),
            }
            return render(request, self.template_name, context)
    
    def _catalogo(self, ruta, token):
        try:
            datos = api_get(ruta, token=token)
        except ApiError:
            return []
        return datos.get('results', []) if isinstance(datos, dict) else datos