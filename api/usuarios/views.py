from django.shortcuts import render

# Create your views here.

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Token
from .serializers import LoginSerializer, UsuarioPerfilSerializer


class LoginView(APIView):
    """POST /api/usuarios/login/  {"username": "...", "password": "..."}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data['usuario']

        # get_or_create: mismo comportamiento que rest_framework.authtoken,
        # un solo token vivo por usuario (si ya existía, se reutiliza).
        token, _ = Token.objects.get_or_create(usuario=usuario)

        return Response({
            'token': token.key,
            'usuario': UsuarioPerfilSerializer(usuario).data,
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
        return Response(UsuarioPerfilSerializer(request.user).data)