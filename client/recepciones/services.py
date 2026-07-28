import requests
from django.conf import settings

API_BASE = settings.API_BASE_URL  # p.ej. "http://localhost:8000/api"


class ApiError(Exception):
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"API error {status_code}: {payload}")


def _headers(request):
    token = request.session.get('api_token')
    return {'Authorization': f'Token {token}'} if token else {}


def _handle_response(response):
    if response.status_code == 401:
        raise ApiError(401, {'detail': 'Sesión expirada, vuelva a iniciar sesión.'})
    if not response.ok:
        try:
            raise ApiError(response.status_code, response.json())
        except ValueError:
            raise ApiError(response.status_code, {'detail': response.text})
    return response.json()


def listar_bandeja_recepcion(request, filtros=None):
    resp = requests.get(
        f'{API_BASE}/recepciones/bandeja/',
        headers=_headers(request), params=filtros, timeout=5,
    )
    return _handle_response(resp)


def confirmar_recepcion_feliz(request, folio_merma):
    """RF-04: cantidades coinciden. Actualiza a RECIBIDA y dispara RF-06."""
    resp = requests.post(
        f'{API_BASE}/recepciones/confirmar/',
        headers=_headers(request),
        json={'folio_merma': folio_merma},
        timeout=5,
    )
    return _handle_response(resp)


def crear_discrepancia(request, folio, cantidad_reportada, cantidad_recibida, motivo_reporte, registro_merma):
    """RF-05: cantidades NO coinciden."""
    diferencia = cantidad_reportada - cantidad_recibida
    resp = requests.post(
        f'{API_BASE}/recepciones/discrepancias/crear/',
        headers=_headers(request),
        json={
            'folio': folio,
            'cantidad_reportada': cantidad_reportada,
            'cantidad_recibida': cantidad_recibida,
            'diferencia': diferencia,
            'motivo_reporte': motivo_reporte,
            'registro_merma': registro_merma,
        },
        timeout=5,
    )
    return _handle_response(resp)


def resolver_discrepancia(request, folio_discrepancia, motivo_resolucion):
    """RF-48."""
    resp = requests.post(
        f'{API_BASE}/recepciones/discrepancias/{folio_discrepancia}/resolver/',
        headers=_headers(request),
        json={'motivo_resolucion': motivo_resolucion},
        timeout=5,
    )
    return _handle_response(resp)