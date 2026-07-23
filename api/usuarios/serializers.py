from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from .models import Usuario, Empleado


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

# ======================================================
# Serializers del modulo de Usuarios
# ======================================================

class ListUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "num",
            "username",
            "correo",
            "empleado",
            "rol",
            "activo",
        ]
        

class CreateUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "username",
            "correo",
            "contrasena",
            "empleado",
            "rol",
            "activo",
        ]
        
        extra_kwargs = {
            "contrasena": {"write_only": True}
        }
    
    def create(self, validated_data):
        validated_data["contrasena"] = make_password(
            validated_data["contrasena"]
        )
        return Usuario.objects.create(**validated_data)
        
class DetailUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "num",
            "username",
            "correo",
            "empleado",
            "rol",
            "activo",
        ]
        
class UpdateUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "correo",
            "contrasena",
            "rol",
            "activo",
        ]
        
        extra_kwargs = {
            "contrasena": {
                "required": False,
                "write_only": True
            }
        }
        
    def update(self, instance, validated_data):
        password = validated_data.pop("contrasena", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.contrasena = make_password(password)
        instance.save()
        return instance

# ======================================================
# Serializers del modulo de Empleados
# ======================================================

class ListEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            "nombre",
            "primer_apellido",
            "segundo_apellido",
            "fecha_nacimiento",
            "fecha_ingreso",
            "area",
            "activo",
        ]

class CreateEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            "nombre",
            "primer_apellido",
            "segundo_apellido",
            "fecha_nacimiento",
            "fecha_ingreso",
            "area",
            "activo",
        ]
        
class DetailEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            "numero",
            "nombre",
            "primer_apellido",
            "segundo_apellido",
            "fecha_nacimiento",
            "fecha_ingreso",
            "area",
            "activo",
        ]
        
class UpdateEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            "nombre",
            "primer_apellido",
            "segundo_apellido",
            "fecha_nacimiento",
            "fecha_ingreso",
            "area",
            "activo",
        ]
