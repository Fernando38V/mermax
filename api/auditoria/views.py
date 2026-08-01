"""
App: auditoria - views
RF-47 - Bitácora de auditoría del sistema.

Sólo hay endpoints GET. No existe create, update ni destroy: el RF-47 dice
que la bitácora no puede modificarse ni eliminarse, y la forma más segura de
garantizarlo es que esas operaciones no existan en la API. El modelo además
las bloquea por su cuenta, como segunda barrera.

El acceso está restringido al Administrador: la bitácora contiene el rastro
de lo que hizo cada usuario, y dejarla abierta a todos los roles convertiría
una herramienta de control en una de vigilancia entre compañeros.
"""
from datetime import datetime

from rest_framework import permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BitacoraAuditoria
from .serializers import BitacoraSerializer


class SoloAdministrador(permissions.BasePermission):
    message = 'Sólo el Administrador puede consultar la bitácora de auditoría.'

    def has_permission(self, request, view):
        return (request.user
                and request.user.is_authenticated
                and request.user.rol_id == 'ADMIN')


class BitacoraPaginacion(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'tamano'
    max_page_size = 500


class BitacoraListView(APIView):
    """
    GET /api/auditoria/bitacora/

    Filtros:
        ?usuario=2
        ?modulo=COMPONENTE
        ?accion=UPDATE
        ?desde=2026-07-01&hasta=2026-07-25
        ?pagina=2&tamano=100
    """
    permission_classes = [SoloAdministrador]

    def get(self, request):
        qs = (BitacoraAuditoria.objects
              .select_related('usuario')
              .order_by('-fecha_hora', '-num'))

        usuario = request.query_params.get('usuario')
        if usuario:
            qs = qs.filter(usuario=usuario)

        modulo = request.query_params.get('modulo')
        if modulo:
            qs = qs.filter(modulo__iexact=modulo)

        accion = request.query_params.get('accion')
        if accion:
            qs = qs.filter(accion__iexact=accion)

        for nombre, lookup in (('desde', 'fecha_hora__date__gte'),
                               ('hasta', 'fecha_hora__date__lte')):
            valor = request.query_params.get(nombre)
            if valor:
                try:
                    qs = qs.filter(**{lookup: datetime.strptime(valor, '%Y-%m-%d').date()})
                except ValueError:
                    pass

        paginador = BitacoraPaginacion()
        paginador.page_query_param = 'pagina'
        pagina = paginador.paginate_queryset(qs, request, view=self)
        return paginador.get_paginated_response(
            BitacoraSerializer(pagina, many=True).data
        )


class BitacoraDetailView(APIView):
    """GET /api/auditoria/bitacora/<num>/"""
    permission_classes = [SoloAdministrador]

    def get(self, request, num):
        registro = (BitacoraAuditoria.objects
                    .select_related('usuario')
                    .filter(num=num).first())
        if registro is None:
            return Response({'detail': 'Registro no encontrado.'}, status=404)
        return Response(BitacoraSerializer(registro).data)


class BitacoraResumenView(APIView):
    """
    GET /api/auditoria/resumen/

    Conteos por módulo, acción y usuario. Sirve para que el Administrador
    ubique rápido dónde hay más movimiento antes de ponerse a filtrar.
    """
    permission_classes = [SoloAdministrador]

    def get(self, request):
        from django.db.models import Count

        base = BitacoraAuditoria.objects.all()

        modulo = request.query_params.get('modulo')
        if modulo:
            base = base.filter(modulo__iexact=modulo)
        desde = request.query_params.get('desde')
        if desde:
            try:
                base = base.filter(fecha_hora__date__gte=datetime.strptime(desde, '%Y-%m-%d').date())
            except ValueError:
                pass
        hasta = request.query_params.get('hasta')
        if hasta:
            try:
                base = base.filter(fecha_hora__date__lte=datetime.strptime(hasta, '%Y-%m-%d').date())
            except ValueError:
                pass

        return Response({
            'total': base.count(),
            'por_modulo': list(base.values('modulo').annotate(n=Count('num')).order_by('-n')),
            'por_accion': list(base.values('accion').annotate(n=Count('num')).order_by('-n')),
            'por_usuario': list(base.values('usuario', 'usuario__username').annotate(n=Count('num')).order_by('-n')),
        })