from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get

@method_decorator(login_required_api, name='dispatch')
class ListMermas(generic.View):
    template_name = 'mermas/list_merma.html'

    def get(self, request):
        token = request.session.get('api_token')

        try:
            mermas = api_get('/mermas/registro/list/', token=token)
        except ApiError:
            mermas = []

        return render(request, self.template_name, {
            'mermas': mermas,
            'lineas': self._catalogo('/catalogos/lineas/', token),
            'tipos_merma': self._catalogo('/catalogos/tipos-merma/', token),
            'componentes': self._catalogo('/catalogos/componentes/', token),
            'estados': self._catalogo('/catalogos/lookup/estados-flujo/', token),
        })

    def _catalogo(self, ruta, token):
        try:
            datos = api_get(ruta, token=token)
        except ApiError:
            return []
        if isinstance(datos, dict):
            return datos.get('results', [])
        return datos