"""
Pequeño wrapper sobre `requests` para hablar con el backend (puerto 8000)
desde las vistas del frontend. Centraliza headers y manejo de errores para
no repetirlo en cada vista.
"""
import requests
from django.conf import settings


class ApiError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))


def _headers(token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Token {token}'
    return headers


def _base_url():
    return settings.API_BASE_URL.rstrip('/')


def api_post(path, data=None, token=None):
    url = f'{_base_url()}{path}'
    try:
        resp = requests.post(url, json=data, headers=_headers(token), timeout=5)
    except requests.exceptions.ConnectionError:
        raise ApiError(503, 'No se pudo conectar con el servidor')

    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        raise ApiError(resp.status_code, detail)

    return resp.json() if resp.content else None


def api_get(path, token=None, params=None):
    url = f'{_base_url()}{path}'
    try:
        resp = requests.get(url, headers=_headers(token), params=params, timeout=5)
    except requests.exceptions.ConnectionError:
        raise ApiError(503, 'No se pudo conectar con el servidor')

    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        raise ApiError(resp.status_code, detail)

    return resp.json()