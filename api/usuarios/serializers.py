from django.contrib.auth.hashers import check_password
from rest_framework import serializers

from .models import Usuario


class LoginSerializer(serializers.Serializer):
    """
    Valida username + password contra la tabla usuario.
    OJO: requiere que 'contrasena' ya esté guardada con un hash de Django
    (make_password), no en texto plano. Ver nota en views.py sobre cómo
    sembrar el primer usuario de prueba.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            usuario = Usuario.objects.select_related('rol', 'empleado').get(username=username)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError('Usuario o contraseña incorrectos')

        if not check_password(password, usuario.contrasena):
            raise serializers.ValidationError('Usuario o contraseña incorrectos')

        attrs['usuario'] = usuario
        return attrs


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """Datos del usuario autenticado, para /me/ y para la respuesta de login."""
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ('num', 'username', 'correo', 'rol', 'rol_nombre', 'empleado', 'nombre_completo')

    def get_nombre_completo(self, obj):
        partes = [obj.empleado.nombre, obj.empleado.primer_apellido, obj.empleado.segundo_apellido]
        return ' '.join(p for p in partes if p)