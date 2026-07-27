"""
App: auditoria - serializers
RF-47: la bitácora es únicamente de consulta, así que sólo hay serializers
de lectura. No existe uno de escritura a propósito.
"""
from rest_framework import serializers

from .models import BitacoraAuditoria


class BitacoraSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    rol = serializers.CharField(source='usuario.rol_id', read_only=True)
    accion_nombre = serializers.SerializerMethodField()

    class Meta:
        model = BitacoraAuditoria
        fields = ('num', 'fecha_hora', 'usuario', 'usuario_nombre', 'rol',
                  'modulo', 'accion', 'accion_nombre',
                  'valor_anterior', 'valor_nuevo', 'motivo')
        read_only_fields = fields

    def get_accion_nombre(self, obj):
        return dict(BitacoraAuditoria.ACCIONES).get(obj.accion, obj.accion)