from django.shortcuts import render

# Create your views here.

from rest_framework import permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from .authentication import UsuarioTokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from auditoria.services import AuditoriaSqlMixin

from .models import Token
from usuarios import serializers, models
from usuarios.permissions import EsAdministrador

class LoginView(APIView):
    """POST /api/usuarios/login/  {"username": "...", "password": "..."}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data['usuario']

        token, _ = Token.objects.get_or_create(usuario=usuario)

        return Response({
            'token': token.key,
            'usuario': serializers.UsuarioPerfilSerializer(usuario).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """POST /api/usuarios/logout/  -> requiere Authorization: Token <key>"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(usuario=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """GET /api/usuarios/me/  -> requiere Authorization: Token <key>"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(serializers.UsuarioPerfilSerializer(request.user).data)

# ======================================================
# Usuario View Service — RF-43 a RF-46: exclusivo Administrador
# ======================================================

class ListUsuarioAPIView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        queryset = models.Usuario.objects.all()
        data = serializers.ListUsuarioSerializer(queryset, many=True).data
        return Response(data)

class CreateUsuarioAPIView(AuditoriaSqlMixin, generics.CreateAPIView):
    permission_classes = [EsAdministrador]
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.CreateUsuarioSerializer

class DetailUsuarioAPIView(generics.RetrieveAPIView):
    permission_classes = [EsAdministrador]
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.DetailUsuarioSerializer

class UpdateUsuarioAPIView(AuditoriaSqlMixin, generics.UpdateAPIView):
    permission_classes = [EsAdministrador]
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.UpdateUsuarioSerializer
    
# ======================================================
# Empleados View Service — igualmente exclusivo Administrador
# ======================================================

class ListEmpleadoAPIView(APIView):
    permission_classes = [EsAdministrador]

    def get(self, request):
        queryset = models.Empleado.objects.all()
        data = serializers.ListEmpleadoSerializer(queryset, many=True).data
        return Response(data)

class CreateEmpleadoAPIView(AuditoriaSqlMixin, generics.CreateAPIView):
    permission_classes = [EsAdministrador]
    queryset = models.Empleado.objects.all()
    serializer_class = serializers.CreateEmpleadoSerializer

class DetailEmpleadoAPIView(generics.RetrieveAPIView):
    permission_classes = [EsAdministrador]
    queryset = models.Empleado.objects.all()
    serializer_class = serializers.DetailEmpleadoSerializer

class UpdateEmpleadoAPIView(AuditoriaSqlMixin, generics.UpdateAPIView):
    permission_classes = [EsAdministrador]
    queryset = models.Empleado.objects.all()
    serializer_class = serializers.UpdateEmpleadoSerializer
    
"""
Vista de agregación para el dashboard del rol ADMIN.
Se apoya en usuarios.models.Usuario, auditoria.models.BitacoraAuditoria,
reportes.models.AlertaGenerada y los catálogos con bandera 'activo'.
"""
from datetime import date, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.models import Usuario
from auditoria.models import BitacoraAuditoria
from reportes.models import AlertaGenerada
from catalogos.models import (
    TipoMerma, CausaRaiz, Componente, Proveedor,
    EstacionTrabajo, EmpresaRecicladora, MetodoDestruccion,
)

# Los 7 catálogos que tienen bandera 'activo' (ver nota en all_models.md).
CATALOGOS_CON_ACTIVO = [
    TipoMerma, CausaRaiz, Componente, Proveedor,
    EstacionTrabajo, EmpresaRecicladora, MetodoDestruccion,
]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_admin(request):
    hoy = date.today()
    hace_6_dias = hoy - timedelta(days=6)

    usuarios_activos = Usuario.objects.filter(activo=True).count()

    # Suma de ítems activos entre los catálogos con bandera 'activo'.
    catalogos_activos = sum(
        modelo.objects.filter(activo=True).count() for modelo in CATALOGOS_CON_ACTIVO
    )

    eventos_bitacora_hoy = BitacoraAuditoria.objects.filter(fecha_hora__date=hoy).count()

    # Líneas de producción distintas con al menos una alerta ACTIVA.
    alertas_criticas = (
        AlertaGenerada.objects
        .filter(estado_alerta_id='ACTIVA')
        .values('umbral_alerta__linea_produccion')
        .distinct()
        .count()
    )

    # ---- Actividad en bitácora, últimos 7 días (rellenando ceros) ----
    bitacora_qs = (
        BitacoraAuditoria.objects
        .filter(fecha_hora__date__gte=hace_6_dias)
        .annotate(dia=TruncDate('fecha_hora'))
        .values('dia')
        .annotate(eventos=Count('num'))
        .order_by('dia')
    )
    eventos_por_dia = {row['dia']: row['eventos'] for row in bitacora_qs}
    bitacora_por_dia = []
    for i in range(7):
        d = hace_6_dias + timedelta(days=i)
        bitacora_por_dia.append({'fecha': d.isoformat(), 'eventos': eventos_por_dia.get(d, 0)})

    # ---- Usuarios activos por rol ----
    usuarios_por_rol_qs = (
        Usuario.objects.filter(activo=True)
        .values('rol__nombre')
        .annotate(cantidad=Count('num'))
        .order_by('-cantidad')
    )
    usuarios_por_rol = [
        {'rol_nombre': row['rol__nombre'], 'cantidad': row['cantidad']}
        for row in usuarios_por_rol_qs
    ]

    return Response({
        'resumen': {
            'usuarios_activos': usuarios_activos,
            'catalogos_activos': catalogos_activos,
            'eventos_bitacora_hoy': eventos_bitacora_hoy,
            'alertas_criticas': alertas_criticas,
        },
        'bitacora_por_dia': bitacora_por_dia,
        'usuarios_por_rol': usuarios_por_rol,
    })
    
# Mi Perfil

@api_view(['GET'])
@authentication_classes([UsuarioTokenAuthentication])
@permission_classes([IsAuthenticated])
def mi_perfil(request):
    
    serializer = serializers.MiPerfilSerializer(request.user)
    return Response(serializer.data)