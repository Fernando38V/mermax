from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import generic
import re

from usuarios.decorators import login_required_api
from usuarios.wrappers import ApiError, api_get, api_post, api_patch, api_delete


# ======================================================
# Configuración de los 8 catálogos administrables
# 'auto_codigo_prefijo' va a nivel del catálogo (no dentro de
# 'campos'); solo se agrega a los catálogos cuyo código es
# secuencial sin significado propio (COMP-01, EST-05, REC-01).
# Los semánticos (causas-raiz, tipos-merma) NO lo llevan.
# ======================================================
CATALOGOS = {
    'lineas': {
        'nombre': 'Líneas de Producción',
        'endpoint': '/catalogos/lineas/',
        'pk_field': 'num',
        'usa_activo': False,
        'campo_estado': 'estado_linea',
        'valor_inactivo': 'INACTIVA',
        'campos': [
            {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
            {'name': 'descripcion', 'label': 'Descripción', 'type': 'text'},
            {'name': 'numero_linea', 'label': 'Número de línea', 'type': 'number', 'required': True},
            {'name': 'area', 'label': 'Área', 'type': 'select', 'endpoint': '/catalogos/lookup/areas/',
             'value_key': 'codigo', 'label_key': 'nombre', 'required': True},
            {'name': 'estado_linea', 'label': 'Estado', 'type': 'select', 'endpoint': '/catalogos/lookup/estados-linea/',
             'value_key': 'codigo', 'label_key': 'nombre', 'required': True},
        ],
        'columnas': [('nombre', 'Nombre'), ('numero_linea', 'No.'), ('area_nombre', 'Área'), ('estado_nombre', 'Estado')],
    },
    'componentes': {
        'nombre': 'Componentes',
        'endpoint': '/catalogos/componentes/',
        'pk_field': 'codigo',
        'usa_activo': True,
        'auto_codigo_prefijo': 'COMP',
        'auto_codigo_padding': 2,
        'campos': [
            {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True, 'solo_creacion': True, 'auto': True},
            {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
            {'name': 'costo', 'label': 'Costo unitario', 'type': 'number', 'step': '0.01', 'required': True},
            {'name': 'descripcion', 'label': 'Descripción', 'type': 'text'},
            {'name': 'tipo', 'label': 'Tipo', 'type': 'text'},
        ],
        'columnas': [('codigo', 'Código'), ('nombre', 'Nombre'), ('costo', 'Costo'), ('tipo', 'Tipo'), ('activo', 'Activo')],
    },
    'proveedores': {
        'nombre': 'Proveedores',
        'endpoint': '/catalogos/proveedores/',
        'pk_field': 'codigo',
        'usa_activo': True,
        'campos': [
            {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True, 'solo_creacion': True},
            {'name': 'nombre', 'label': 'Nombre / Razón social', 'type': 'text', 'required': True},
            {'name': 'correo', 'label': 'Correo', 'type': 'text', 'required': True},
            {'name': 'telefono', 'label': 'Teléfono', 'type': 'text'},
            {'name': 'direccion_calle', 'label': 'Calle', 'type': 'text'},
            {'name': 'direccion_numero', 'label': 'Número', 'type': 'text'},
            {'name': 'direccion_colonia', 'label': 'Colonia', 'type': 'text'},
            {'name': 'rfc', 'label': 'RFC', 'type': 'text'},
        ],
        'columnas': [('codigo', 'Código'), ('nombre', 'Nombre'), ('correo', 'Correo'), ('telefono', 'Teléfono'), ('activo', 'Activo')],
    },
    'estaciones': {
        'nombre': 'Estaciones de Trabajo',
        'endpoint': '/catalogos/estaciones/',
        'pk_field': 'codigo',
        'usa_activo': True,
        'auto_codigo_prefijo': 'EST',
        'auto_codigo_padding': 2,
        'campos': [
            {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True, 'solo_creacion': True, 'auto': True},
            {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
            {'name': 'etapa', 'label': 'Etapa', 'type': 'text'},
            {'name': 'linea_produccion', 'label': 'Línea de producción', 'type': 'select', 'endpoint': '/catalogos/lineas/',
             'value_key': 'num', 'label_key': 'nombre', 'required': True},
        ],
        'columnas': [('codigo', 'Código'), ('nombre', 'Nombre'), ('etapa', 'Etapa'), ('linea_nombre', 'Línea'), ('activo', 'Activo')],
    },
    'causas-raiz': {
        'nombre': 'Causas Raíz',
        'endpoint': '/catalogos/causas-raiz/',
        'pk_field': 'codigo',
        'usa_activo': True,
        'campos': [
            {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True, 'solo_creacion': True},
            {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
            {'name': 'descripcion', 'label': 'Descripción', 'type': 'text'},
        ],
        'columnas': [('codigo', 'Código'), ('nombre', 'Nombre'), ('descripcion', 'Descripción'), ('activo', 'Activo')],
    },
    'tipos-merma': {
        'nombre': 'Tipos de Merma',
        'endpoint': '/catalogos/tipos-merma/',
        'pk_field': 'codigo',
        'usa_activo': True,
        'campos': [
            {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True, 'solo_creacion': True},
            {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
            {'name': 'descripcion', 'label': 'Descripción', 'type': 'text'},
        ],
        'columnas': [('codigo', 'Código'), ('nombre', 'Nombre'), ('descripcion', 'Descripción'), ('activo', 'Activo')],
    },
    'empresas-recicladoras': {
        'nombre': 'Empresas Recicladoras',
        'endpoint': '/catalogos/empresas-recicladoras/',
        'pk_field': 'codigo',
        'usa_activo': True,
        'auto_codigo_prefijo': 'REC',
        'auto_codigo_padding': 2,
        'campos': [
            {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True, 'solo_creacion': True, 'auto': True},
            {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
            {'name': 'telefono', 'label': 'Teléfono', 'type': 'text'},
            {'name': 'correo', 'label': 'Correo', 'type': 'text'},
        ],
        'columnas': [('codigo', 'Código'), ('nombre', 'Nombre'), ('telefono', 'Teléfono'), ('correo', 'Correo'), ('activo', 'Activo')],
    },
    'metodos-destruccion': {
        'nombre': 'Métodos de Destrucción',
        'endpoint': '/catalogos/metodos-destruccion/',
        'pk_field': 'codigo',
        'usa_activo': True,
        'auto_codigo_prefijo': 'MET',
        'auto_codigo_padding': 2,
        'campos': [
            {'name': 'codigo', 'label': 'Código', 'type': 'text', 'required': True, 'solo_creacion': True},
            {'name': 'nombre', 'label': 'Nombre', 'type': 'text', 'required': True},
            {'name': 'descripcion', 'label': 'Descripción', 'type': 'text'},
        ],
        'columnas': [('codigo', 'Código'), ('nombre', 'Nombre'), ('descripcion', 'Descripción'), ('activo', 'Activo')],
    },
}

def _traducir_errores(errores):
    """Traduce los mensajes de validación más comunes que DRF genera en inglés."""
    if not isinstance(errores, dict):
        return errores
    traducidos = {}
    for campo, mensajes in errores.items():
        lista = mensajes if isinstance(mensajes, list) else [mensajes]
        nuevos = []
        for m in lista:
            texto = str(m)
            baja = texto.lower()
            if 'already exists' in baja:
                texto = 'Ya existe un registro con este mismo valor.'
            elif 'may not be blank' in baja or 'this field is required' in baja:
                texto = 'Este campo es obligatorio.'
            elif 'a valid number' in baja:
                texto = 'Debe ser un número válido.'
            elif 'no more than' in baja:
                match = re.search(r'no more than (\d+) characters', baja)
                if match:
                    texto = f'No puede tener más de {match.group(1)} caracteres.'
            nuevos.append(texto)
        traducidos[campo] = nuevos
    return traducidos

@method_decorator(login_required_api, name='dispatch')
class IndiceCatalogos(generic.View):
    def get(self, request):
        return render(request, 'administrador/catalogos_indice.html', {'catalogos': CATALOGOS})


@method_decorator(login_required_api, name='dispatch')
class ListCatalogo(generic.View):
    template_name = 'administrador/catalogo_list.html'

    def get(self, request, slug):
        token = request.session.get('api_token')
        config = CATALOGOS[slug]

        params = {}
        busqueda = request.GET.get('q', '').strip()
        if busqueda:
            params['search'] = busqueda
        activo = request.GET.get('activo')
        if activo:
            params['activo'] = activo

        try:
            respuesta = api_get(config['endpoint'], token=token, params=params)
        except ApiError:
            respuesta = []

        registros = respuesta.get('results', []) if isinstance(respuesta, dict) else respuesta

        campo_estado = config.get('campo_estado')
        valor_inactivo = config.get('valor_inactivo')
        for r in registros:
            if config.get('usa_activo'):
                r['inactivo_calc'] = not r.get('activo', True)
            elif campo_estado:
                r['inactivo_calc'] = r.get(campo_estado) == valor_inactivo
            else:
                r['inactivo_calc'] = False

        return render(request, self.template_name, {
            'slug': slug,
            'config': config,
            'registros': registros,
            'busqueda': busqueda,
            'activo_filtro': activo,
        })


@method_decorator(login_required_api, name='dispatch')
class FormCatalogo(generic.View):
    template_name = 'administrador/catalogo_form.html'

    def get(self, request, slug, pk=None):
        token = request.session.get('api_token')
        config = CATALOGOS[slug]

        valores = {}
        if pk:
            try:
                valores = api_get(f"{config['endpoint']}{pk}/", token=token)
            except ApiError:
                messages.error(request, 'No se encontró el registro.')
                return redirect('administrador:catalogo_list', slug=slug)
        elif config.get('auto_codigo_prefijo'):
            valores = {'codigo': self._siguiente_codigo(config, token)}

        return render(request, self.template_name, self._contexto(config, slug, pk, valores, {}, token))

    def _siguiente_codigo(self, config, token):
        prefijo = config['auto_codigo_prefijo']
        padding = config.get('auto_codigo_padding', 2)
        try:
            registros = api_get(config['endpoint'], token=token)
            lista = registros.get('results', []) if isinstance(registros, dict) else registros
        except ApiError:
            lista = []

        ultimo = 0
        for r in lista:
            codigo = r.get('codigo', '')
            if codigo.startswith(prefijo + '-'):
                sufijo = codigo[len(prefijo) + 1:]
                if sufijo.isdigit():
                    ultimo = max(ultimo, int(sufijo))
        return f"{prefijo}-{ultimo + 1:0{padding}d}"

    def post(self, request, slug, pk=None):
        token = request.session.get('api_token')
        config = CATALOGOS[slug]

        payload = {}
        for campo in config['campos']:
            if pk and campo.get('solo_creacion'):
                continue
            valor = request.POST.get(campo['name'], '').strip()
            if valor != '':
                payload[campo['name']] = valor

        # El código autogenerado sí se manda al crear (aunque el input
        # esté readonly, el navegador lo incluye en el POST igual)
        if not pk and config.get('auto_codigo_prefijo'):
            payload['codigo'] = request.POST.get('codigo', '').strip()

        try:
            if pk:
                api_patch(f"{config['endpoint']}{pk}/", payload, token=token)
                messages.success(request, 'Registro actualizado correctamente.')
            else:
                api_post(config['endpoint'], payload, token=token)
                messages.success(request, 'Registro creado correctamente.')
            return redirect('administrador:catalogo_list', slug=slug)
        except ApiError as e:
            errores = e.detail if isinstance(e.detail, dict) else {'error': [str(e.detail)]}
            errores = _traducir_errores(errores)
            return render(request, self.template_name, self._contexto(config, slug, pk, request.POST, errores, token))

    def _contexto(self, config, slug, pk, valores, errores, token):
        campos_render = []
        for campo in config['campos']:
            campo_ctx = dict(campo)
            if campo['type'] == 'select':
                try:
                    opciones = api_get(campo['endpoint'], token=token)
                    campo_ctx['opciones'] = opciones.get('results', []) if isinstance(opciones, dict) else opciones
                except ApiError:
                    campo_ctx['opciones'] = []
            campos_render.append(campo_ctx)

        return {
            'slug': slug,
            'config': config,
            'pk': pk,
            'campos': campos_render,
            'valores': valores,
            'errores': errores,
        }


@method_decorator(login_required_api, name='dispatch')
class BajaCatalogo(generic.View):
    def post(self, request, slug, pk):
        token = request.session.get('api_token')
        config = CATALOGOS[slug]
        try:
            api_delete(f"{config['endpoint']}{pk}/", token=token)
            messages.success(request, 'Registro dado de baja. Su historial se conserva.')
        except ApiError as e:
            messages.error(request, str(e.detail))
        return redirect('administrador:catalogo_list', slug=slug)


@method_decorator(login_required_api, name='dispatch')
class ReactivarCatalogo(generic.View):
    """Vuelve a poner 'activo=True' (o el estado equivalente en líneas)."""
    def post(self, request, slug, pk):
        token = request.session.get('api_token')
        config = CATALOGOS[slug]

        if config.get('usa_activo'):
            payload = {'activo': 'true'}
        else:
            # Caso especial: líneas no usa 'activo', usa 'estado_linea'.
            # Verifica primero el código real de "activa" en tu catálogo
            # de estados (GET /api/catalogos/lookup/estados-linea/).
            payload = {'estado_linea': config.get('valor_activo', 'ACTIVA')}

        try:
            api_patch(f"{config['endpoint']}{pk}/", payload, token=token)
            messages.success(request, 'Registro reactivado correctamente.')
        except ApiError as e:
            messages.error(request, str(e.detail))
        return redirect('administrador:catalogo_list', slug=slug)