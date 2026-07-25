"""
Comando de desarrollo para poblar la base con registros de merma realistas.

NO forma parte del sistema entregable: es una herramienta interna para que el
dashboard del RF-12 y los reportes del RF-14 tengan volumen con que trabajar.
Con las 4 mermas semilla de mermax.sql no se alcanza a ver ninguna tendencia.

Uso:
    cd api
    python manage.py seed_demo                 # 150 mermas
    python manage.py seed_demo --mermas 400    # 400 mermas
    python manage.py seed_demo --limpiar       # borra lo generado y sale

Detalles importantes:

1. Inserta por el ORM, no por SQL directo. Eso significa que LOS TRIGGERS SE
   DISPARAN IGUAL, porque viven en la base de datos y no en Django. El
   costo_total de cada merma lo calcula el Trigger 1, no este script: por eso
   nunca se manda ese campo.

2. Respeta las dos validaciones del Trigger 1. Si no se respetan, el trigger
   lanza SIGNAL y el INSERT se rechaza:
       - el componente debe pertenecer al lote referenciado
       - la estación debe corresponder a la orden de producción
   Por eso el script arma primero un mapa componente -> lote -> estaciones ->
   órdenes leyendo lo que hay en la base, en vez de inventar combinaciones.

3. Los folios generados llevan el prefijo MRM-SEED- para poder distinguirlos
   de los reales y borrarlos después sin tocar los datos semilla.

4. Las mermas quedan repartidas entre los 5 estados del flujo, con proporciones
   parecidas a las de una planta real: la mayoría cerradas, algunas en proceso
   y pocas bloqueadas por discrepancia.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogos.models import Componente, CausaRaiz, EstacionTrabajo, TipoMerma
from mermas.models import RegistroMerma, OrdenProduccion
from recepciones.models import LoteMaterial
from usuarios.models import Usuario

PREFIJO = 'MRM-SEED-'

# Cómo se reparten los estados del flujo (deben sumar 100)
DISTRIBUCION_ESTADOS = [
    ('CERRADA', 55),
    ('INSPECCIO', 15),
    ('RECIBIDA', 15),
    ('REGISTRADA', 10),
    ('DISCREPAN', 5),
]

# Qué causa raíz es plausible para cada tipo de merma. Sin esto los datos
# salen incoherentes (por ejemplo "Daño por Manejo" causado por "Soldadura
# Fría"), y el ranking de causas del RF-12 no dice nada útil.
CAUSAS_POR_TIPO = {
    'DEF_FAB':    ['SOLD_FRIA', 'CONTAM', 'FALLA_MAQ'],
    'DAN_MANEJO': ['MANIP_INAD', 'ESD'],
    'ERR_ENSAM':  ['FALTA_PROC', 'SOLD_FRIA', 'MANIP_INAD'],
    'FALLA_COMP': ['ESD', 'FALLA_MAQ', 'CONTAM'],
    'OTROS':      ['FALTA_PROC', 'CONTAM'],
}

DESCRIPCIONES = [
    'Pieza rechazada en inspección visual de rutina.',
    'Falla detectada durante la prueba funcional de la estación.',
    'Material dañado al retirarlo del contenedor de línea.',
    'Componente fuera de especificación según el plan de control.',
    'Defecto identificado por el operador al inicio del turno.',
    'Unidad separada tras reincidencia en la misma estación.',
]


class Command(BaseCommand):
    help = 'Genera registros de merma de prueba para el dashboard y los reportes.'

    def add_arguments(self, parser):
        parser.add_argument('--mermas', type=int, default=150,
                            help='Cuántas mermas generar (default: 150)')
        parser.add_argument('--dias', type=int, default=90,
                            help='Rango de días hacia atrás para las fechas (default: 90)')
        parser.add_argument('--limpiar', action='store_true',
                            help='Borra sólo lo generado por este comando y termina')

    def handle(self, *args, **opts):
        if opts['limpiar']:
            return self._limpiar()

        total = opts['mermas']
        dias = opts['dias']

        mapa = self._construir_mapa()
        if not mapa:
            self.stderr.write(self.style.ERROR(
                'No hay combinaciones válidas de componente/lote/estación/orden.\n'
                'Reimporta mermax.sql: necesita al menos una orden por estación.'
            ))
            return

        supervisores = list(Usuario.objects.filter(rol='SUPER', activo=True))
        if not supervisores:
            self.stderr.write(self.style.ERROR('No hay usuarios con rol SUPER.'))
            return

        tipos = list(TipoMerma.objects.all())
        causas = {c.codigo: c for c in CausaRaiz.objects.all()}
        estados = self._expandir_estados()

        # Continuar el consecutivo si ya se corrió antes
        ultimo = RegistroMerma.objects.filter(folio__startswith=PREFIJO).count()

        creadas, rechazadas = 0, 0
        hoy = date.today()

        self.stdout.write(f'Generando {total} mermas...')

        for i in range(total):
            combo = random.choice(mapa)
            tipo = random.choice(tipos)
            codigo_causa = random.choice(CAUSAS_POR_TIPO.get(tipo.codigo, list(causas)))

            folio = f'{PREFIJO}{ultimo + i + 1:04d}'

            try:
                with transaction.atomic():
                    RegistroMerma.objects.create(
                        folio=folio,
                        cantidad=Decimal(random.randint(1, 12)),
                        # costo_total NO se manda: lo calcula el Trigger 1
                        fecha=hoy - timedelta(days=random.randint(0, dias)),
                        unidad='Pieza',
                        descripcion=random.choice(DESCRIPCIONES),
                        edo_flujo_merma_id=random.choice(estados),
                        usuario=random.choice(supervisores),
                        lote_material_id=combo['lote'],
                        componente_id=combo['componente'],
                        tipo_merma=tipo,
                        causa_raiz=causas.get(codigo_causa),
                        estacion_trabajo_id=combo['estacion'],
                        orden_produccion_id=combo['orden'],
                    )
                creadas += 1
            except Exception as e:
                # Si un trigger rechaza la fila, se reporta y se sigue.
                rechazadas += 1
                if rechazadas <= 3:
                    self.stderr.write(self.style.WARNING(f'  {folio}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\nCreadas: {creadas}'))
        if rechazadas:
            self.stdout.write(self.style.WARNING(f'Rechazadas por los triggers: {rechazadas}'))

        self._resumen()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _construir_mapa(self):
        """
        Arma la lista de combinaciones que el Trigger 1 va a aceptar:
        componente + lote que lo contiene + estación + orden de esa estación.

        Se lee de la base en vez de escribirse a mano, para que siga
        funcionando si el equipo agrega líneas, estaciones o lotes.
        """
        combos = []

        # Estación -> órdenes que corren en ella
        ordenes_por_estacion = {}
        for orden in OrdenProduccion.objects.all():
            ordenes_por_estacion.setdefault(orden.estacion_trabajo_id, []).append(orden.numero)

        # Cada componente se merma en las estaciones de la línea donde se usa.
        # El vínculo componente -> línea se infiere del orden del catálogo:
        # COMP-01 en la línea 1, COMP-02 en la 2, y así.
        componentes = list(Componente.objects.filter(activo=True).order_by('codigo'))
        estaciones = list(EstacionTrabajo.objects.filter(activo=True).order_by('codigo'))

        for lote in LoteMaterial.objects.select_related('componente'):
            comp = lote.componente_id
            try:
                indice_linea = componentes.index(
                    next(c for c in componentes if c.codigo == comp)
                ) + 1
            except StopIteration:
                continue

            for est in estaciones:
                if est.linea_produccion_id != indice_linea:
                    continue
                for numero_orden in ordenes_por_estacion.get(est.codigo, []):
                    combos.append({
                        'componente': comp,
                        'lote': lote.num,
                        'estacion': est.codigo,
                        'orden': numero_orden,
                    })

        return combos

    def _expandir_estados(self):
        lista = []
        for codigo, peso in DISTRIBUCION_ESTADOS:
            lista.extend([codigo] * peso)
        return lista

    def _limpiar(self):
        borradas, _ = RegistroMerma.objects.filter(folio__startswith=PREFIJO).delete()
        self.stdout.write(self.style.SUCCESS(f'Borrados {borradas} registros de prueba.'))
        self.stdout.write('Los datos semilla de mermax.sql quedaron intactos.')

    def _resumen(self):
        from django.db.models import Count, Sum

        self.stdout.write('\n--- Resumen ---')
        por_estado = (RegistroMerma.objects
                      .values('edo_flujo_merma')
                      .annotate(n=Count('folio'), costo=Sum('costo_total'))
                      .order_by('-n'))
        for fila in por_estado:
            costo = fila['costo'] or 0
            self.stdout.write(f"  {fila['edo_flujo_merma']:<12} {fila['n']:>5} mermas   ${costo:>14,.2f}")

        total = RegistroMerma.objects.aggregate(c=Sum('costo_total'))['c'] or 0
        self.stdout.write(f"\n  Costo total acumulado: ${total:,.2f}")
        self.stdout.write('  (calculado por el Trigger 1, no por este script)')