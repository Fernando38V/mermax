"""
Comando de management: seed_catalogos

Amplía los catálogos de Empleados/Usuarios, Proveedores, Empresas
Recicladoras y Métodos de Destrucción con datos de variedad para la demo.

NO borra nada existente. Usa get_or_create por nombre, así que si lo
corres dos veces por error no duplica registros.

Uso:
    cd api
    python manage.py seed_catalogos

Colócalo en: api/catalogos/management/commands/seed_catalogos.py
(crea las carpetas management/ y management/commands/ con un
__init__.py vacío en cada una si no existen, igual que ya tienes
en mermas/management/commands/seed_demo.py)
"""
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from catalogos.models import Area, EmpresaRecicladora, MetodoDestruccion, Proveedor
from usuarios.models import Empleado, Usuario


def siguiente_codigo(modelo, prefijo):
    """Genera PREFIJO-SNN (<=10 caracteres, el campo codigo es CharField(max_length=10))."""
    existentes = modelo.objects.filter(codigo__startswith=f'{prefijo}-S').count()
    return f'{prefijo}-S{existentes + 1:02d}'


PROVEEDORES = [
    "Componentes Ópticos del Pacífico",
    "Suministros Electrónicos Baja California",
    "Grupo Industrial Delfín",
    "Manufacturas ElectroNorte",
    "Proveedora TecnoBaja",
    "Insumos Electrónicos Fronterizos",
]

RECICLADORAS = [
    "Recicladora Verde Tijuana",
    "EcoRecicla Baja",
    "Recursos Sustentables del Norte",
]

METODOS_DESTRUCCION = [
    ("Trituración mecánica certificada", "Fragmentación física del componente hasta hacerlo irreconocible e inutilizable."),
    ("Incineración controlada", "Destrucción térmica en instalación autorizada con control de emisiones."),
    ("Desmantelamiento manual certificado", "Separación manual de componentes bajo supervisión, con acta de destrucción."),
]

# (nombre, primer_apellido, segundo_apellido, rol_id, username)
EMPLEADOS_USUARIOS = [
    ("Laura",    "Hernández", "Soto",     "SUPER", "laura"),
    ("Miguel",   "Torres",    "Vega",     "SUPER", "miguel"),
    ("Patricia", "Gómez",     "Ruiz",     "ALMAC", "patricia"),
    ("Roberto",  "Salinas",   "Peña",     "ALMAC", "roberto"),
    ("Carla",    "Mendoza",   "Ríos",     "CALID", "carla"),
    ("Iván",     "Castillo",  "Duarte",   "CALID", "ivan"),
]

PASSWORD_DEMO = "123"  # mismo password que ya usan todos los usuarios de prueba

# Confirmado directo en mermax.sql: estos son los codigo reales de AREA.
AREA_POR_ROL = {
    "SUPER": "ARE-PROD",
    "ALMAC": "ARE-ALM",
    "CALID": "ARE-QA",
    "ADMIN": "ARE-ADM",
}


class Command(BaseCommand):
    help = "Amplía catálogos de proveedores, recicladoras, métodos de destrucción y personal para la demo."

    def handle(self, *args, **options):
        areas_disponibles = {a.codigo: a for a in Area.objects.all()}
        area_fallback = Area.objects.first()
        if area_fallback is None:
            self.stdout.write(self.style.ERROR(
                "No hay ninguna Área registrada — necesito al menos una para crear Empleados. Abortando esa parte."
            ))

        with transaction.atomic():
            # ---- Proveedores ----
            creados = 0
            for nombre in PROVEEDORES:
                _, fue_creado = Proveedor.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        "codigo": siguiente_codigo(Proveedor, "PRV"),
                        "correo": f"contacto@{nombre.lower().replace(' ', '')[:20]}.com",
                        "telefono": "6641234567",
                        "activo": True,
                    },
                )
                creados += fue_creado
            self.stdout.write(self.style.SUCCESS(f"Proveedores: {creados} nuevos creados."))

            # ---- Empresas recicladoras ----
            creados = 0
            for nombre in RECICLADORAS:
                _, fue_creado = EmpresaRecicladora.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        "codigo": siguiente_codigo(EmpresaRecicladora, "REC"),
                        "correo": f"contacto@{nombre.lower().replace(' ', '')[:20]}.com",
                        "telefono": "6647654321",
                        "activo": True,
                    },
                )
                creados += fue_creado
            self.stdout.write(self.style.SUCCESS(f"Empresas recicladoras: {creados} nuevas creadas."))

            # ---- Métodos de destrucción ----
            creados = 0
            for nombre, descripcion in METODOS_DESTRUCCION:
                _, fue_creado = MetodoDestruccion.objects.get_or_create(
                    nombre=nombre,
                    defaults={
                        "codigo": siguiente_codigo(MetodoDestruccion, "MET"),
                        "descripcion": descripcion,
                        "activo": True,
                    },
                )
                creados += fue_creado
            self.stdout.write(self.style.SUCCESS(f"Métodos de destrucción: {creados} nuevos creados."))

        # ---- Empleados + Usuarios ----
        # Van en su PROPIA transacción, separada de los catálogos de arriba:
        # así, si algo falla aquí, lo que ya se guardó en proveedores/
        # recicladoras/métodos no se pierde con un rollback.
        if area_fallback is not None:
            # Los triggers de bitácora (tg_bitacora_ins_empleado / ..._usuario)
            # EXIGEN esta variable de sesión antes de insertar en EMPLEADO o
            # USUARIO, si no, bloquean el INSERT con SIGNAL. Se usa el primer
            # Administrador activo como "usuario que hizo el alta" para la
            # bitácora; si no hay ninguno, cae a cualquier usuario existente.
            actor = Usuario.objects.filter(rol_id='ADMIN', activo=True).first() or Usuario.objects.first()
            if actor is None:
                self.stdout.write(self.style.ERROR(
                    "No hay ningún Usuario existente para usar como responsable de la bitácora. "
                    "Corre primero seed_demo o asegúrate de tener al menos un usuario base. Abortando Empleados/Usuarios."
                ))
                return

            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("SET @usuario_actual = %s", [actor.num])

                creados = 0
                for nombre, apellido1, apellido2, rol_id, username in EMPLEADOS_USUARIOS:
                    if Usuario.objects.filter(username=username).exists():
                        continue
                    area_del_rol = areas_disponibles.get(AREA_POR_ROL.get(rol_id), area_fallback)
                    empleado = Empleado.objects.create(
                        nombre=nombre,
                        primer_apellido=apellido1,
                        segundo_apellido=apellido2,
                        area=area_del_rol,
                        activo=True,
                    )
                    Usuario.objects.create(
                        username=username,
                        correo=f"{username}@mermax.com",
                        contrasena=make_password(PASSWORD_DEMO),
                        empleado=empleado,
                        rol_id=rol_id,
                        activo=True,
                    )
                    creados += 1
            self.stdout.write(self.style.SUCCESS(
                f"Empleados/Usuarios: {creados} nuevos creados (password para todos: '{PASSWORD_DEMO}')."
            ))

        self.stdout.write(self.style.SUCCESS("Listo."))