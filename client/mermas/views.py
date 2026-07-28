import math
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get

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