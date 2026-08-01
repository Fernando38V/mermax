"""
App: usuarios - serializers

CORREGIDO 25/07: los serializers de Empleado pedían el campo
'fecha_nacimiento', que no existe en la tabla. Se reemplazó por 'edad' y
'turno', que sí existen. También se quitó 'puesto' (eliminado del modelo).
"""
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from .models import Usuario, Empleado


class LoginSerializer(serializers.Serializer):
    """
    Valida username o correo + password contra la tabla usuario.
    Requiere que 'contrasena' esté guardada con un hash de Django
    (make_password). La semilla de mermax.sql ya viene hasheada.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        identificador = attrs.get('username', '').strip()
        password = attrs.get('password')

        usuario = (
            Usuario.objects
            .select_related('rol', 'empleado')
            .filter(username__iexact=identificador)
            .first()
            or
            Usuario.objects
            .select_related('rol', 'empleado')
            .filter(correo__iexact=identificador)
            .first()
        )

        if usuario is None:
            raise serializers.ValidationError('Usuario o contraseña incorrectos')

        if not check_password(password, usuario.contrasena):
            raise serializers.ValidationError('Usuario o contraseña incorrectos')

        # RF-46: una cuenta inactiva no debe poder iniciar sesión
        if not usuario.activo:
            raise serializers.ValidationError('Esta cuenta está inactiva. Contacta al administrador.')

        if not usuario.empleado.activo:
            raise serializers.ValidationError('El empleado asociado a esta cuenta está inactivo. Contacta al administrador.')

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
        return obj.empleado.nombre_completo


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
        # Aquí es donde se resuelve el hasheo automático: cualquier usuario
        # dado de alta por la API queda con la contraseña encriptada.
        validated_data["contrasena"] = make_password(validated_data["contrasena"])
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

CAMPOS_EMPLEADO = [
    "nombre", 
    "primer_apellido", 
    "segundo_apellido", 
    "fecha_nacimiento",
    "fecha_ingreso", 
    "area", 
    "turno", 
    "activo",
]

class ListEmpleadoSerializer(serializers.ModelSerializer):
    edad = serializers.IntegerField(read_only=True)   # viene de la propiedad del modelo

    class Meta:
        model = Empleado
        fields = ["numero", "edad"] + CAMPOS_EMPLEADO

class CreateEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ["numero"] + CAMPOS_EMPLEADO
        read_only_fields = ["numero"]

class DetailEmpleadoSerializer(serializers.ModelSerializer):
    edad = serializers.IntegerField(read_only=True)   # viene de la propiedad del modelo

    class Meta:
        model = Empleado
        fields = ["numero", "edad"] + CAMPOS_EMPLEADO


class UpdateEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = CAMPOS_EMPLEADO