from django.shortcuts import render

# Create your views here.

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from .models import Token
from usuarios import serializers, models


class LoginView(APIView):
    """POST /api/usuarios/login/  {"username": "...", "password": "..."}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data['usuario']

        # get_or_create: mismo comportamiento que rest_framework.authtoken,
        # un solo token vivo por usuario (si ya existía, se reutiliza).
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
# Usuario View Service
# ======================================================

class ListUsuarioAPIView(APIView):
    def get(self, request):
        queryset = models.Usuario.objects.all()
        data = serializers.ListUsuarioSerializer(queryset, many=True).data
        return Response(data)

class CreateUsuarioAPIView(generics.CreateAPIView):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.CreateUsuarioSerializer

class DetailUsuarioAPIView(generics.RetrieveAPIView):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.DetailUsuarioSerializer

class UpdateUsuarioAPIView(generics.UpdateAPIView):
    queryset = models.Usuario.objects.all()
    serializer_class = serializers.UpdateUsuarioSerializer
    
# ======================================================
# Empleados View Service
# ======================================================

class ListEmpleadoAPIView(APIView):
    def get(self, request):
        queryset = models.Empleado.objects.all()
        data = serializers.ListEmpleadoSerializer(queryset, many=True).data
        return Response(data)

class CreateEmpleadoAPIView(generics.CreateAPIView):
    queryset = models.Empleado.objects.all()
    serializer_class = serializers.CreateEmpleadoSerializer

class DetailEmpleadoAPIView(generics.RetrieveAPIView):
    queryset = models.Empleado.objects.all()
    serializer_class = serializers.DetailEmpleadoSerializer

class UpdateEmpleadoAPIView(generics.UpdateAPIView):
    queryset = models.Empleado.objects.all()
    serializer_class = serializers.UpdateEmpleadoSerializer
    