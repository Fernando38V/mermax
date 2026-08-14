from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic

from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get


@method_decorator(login_required_api, name='dispatch')
class ConsultaLote(generic.View):
    template_name = 'trazabilidad/consulta.html'

    def get(self, request):
        token = request.session.get('api_token')
        numero_lote = request.GET.get('lote', '').strip()

        try:
            componentes = api_get('/catalogos/componentes/', token=token)
            componentes = componentes.get('results', []) if isinstance(componentes, dict) else componentes
        except ApiError:
            componentes = []

        contexto = {
            'numero_lote': numero_lote,
            'componente_seleccionado': request.GET.get('componente', ''),
            'componentes': componentes,
            'resultado': None,
            'error': None,
        }

        if numero_lote:
            if not numero_lote.isdigit() or int(numero_lote) < 1:
                contexto['error'] = 'Selecciona un lote válido de la lista.'
            else:
                try:
                    contexto['resultado'] = api_get(
                        f'/reportes/trazabilidad/lote/{numero_lote}/', token=token
                    )
                except ApiError as e:
                    mensaje = (e.detail.get('detail') if isinstance(e.detail, dict) else str(e.detail))
                    contexto['error'] = mensaje or 'No se encontró información para ese lote.'

        return render(request, self.template_name, contexto)
    
@method_decorator(login_required_api, name='dispatch')
@method_decorator(login_required_api, name='dispatch')
class TrazabilidadFolio(generic.View):
    template_name = 'trazabilidad/trazabilidad_folio.html'

    def get(self, request):
        token = request.session.get('api_token')
        folio = request.GET.get('folio', '').strip()

        contexto = {"folio_buscado": folio, "resultado": None, "error": None}

        if folio:
            try:
                contexto["resultado"] = api_get(f'/reportes/trazabilidad-folio/{folio}/', token=token)
            except ApiError as e:
                contexto["error"] = str(e)

        return render(request, self.template_name, contexto)