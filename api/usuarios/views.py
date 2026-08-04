from django.shortcuts import render

# Create your views here.

from rest_framework import permissions, status
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