"""
Comando de desarrollo para poblar la base con datos de merma coherentes.

NO forma parte del sistema entregable: es una herramienta interna para que el
dashboard del RF-12, los reportes del RF-14 y el módulo de inspecciones tengan
volumen con que trabajar.

Uso:
    cd api
    python manage.py seed_demo                 # 200 mermas
    python manage.py seed_demo --mermas 400
    python manage.py seed_demo --limpiar       # borra lo generado y sale

--------------------------------------------------------------------------
QUÉ HACE DISTINTO A UN INSERT MASIVO
--------------------------------------------------------------------------
No asigna los estados del flujo a mano. RECORRE EL FLUJO REAL, igual que lo
haría un usuario en la aplicación, y deja que los triggers hagan su trabajo:

    1. Inserta la merma en estado REGISTRADA
       -> el Trigger 1 valida componente/lote y estación/orden, y calcula
          costo_total. El script nunca manda ese campo.

    2. Para las que van a quedar bloqueadas, inserta una DISCREPANCIA real
       -> el Trigger 3 valida la cantidad reportada, recalcula la diferencia
          en el servidor y cambia el folio a DISCREPAN.

    3. Para las demás, hace UPDATE del estado a RECIBIDA
       -> el Trigger 2 genera solo la SOLICITUD_INSPECCION, porque el folio
          está limpio.

    4. Las que se cierran avanzan a INSPECCIO y luego a CERRADA, se marca su
       solicitud como ATENDIDA y se crea el REGISTRO_DISPOSICION con su tabla
       satélite según el dictamen (RF-08, RF-09 o RF-10).

La versión anterior escribía los estados directamente. Eso dejaba folios en
DISCREPAN sin ninguna discrepancia que los respaldara, y mermas en RECIBIDA
sin solicitud de inspección: números que cuadran en el dashboard pero que se
contradicen en cuanto alguien cruza dos tablas.

--------------------------------------------------------------------------
CALIBRACIÓN DEL VOLUMEN
--------------------------------------------------------------------------
Las cantidades por evento y el reparto por línea están calibrados para que el
% de scrap caiga en el rango real de una planta (1-3%), y para que el semáforo
del RF-12 muestre líneas en verde y en rojo en lugar de todas iguales:

    Línea 3 (Panel LED)  ~3.4%  -> rebasa su umbral de 3.0%, sale en ROJO
    Línea 1 (Tarjetas)   ~1.3%  -> muy por debajo de su umbral de 2.5%, VERDE
    Líneas 2, 4 y 5      ~2.2%
    Total de planta      ~2.3%  -> dentro del rango real de una planta

Si cambias las órdenes de producción en mermax.sql, revisa estos pesos.
"""
import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogos.models import (
    Almacen, CausaRaiz, Componente, EmpresaRecicladora,
    EstacionTrabajo, MetodoDestruccion, TipoMerma,
)
from inspecciones.models import (
    DisposicionDesecho, DisposicionDevolucion, DisposicionReciclaje,
    RegistroDisposicion, SolicitudInspeccion,
)
from mermas.models import OrdenProduccion, RegistroMerma, TurnoOrden
from recepciones.models import Discrepancia, LoteMaterial
from usuarios.models import Usuario

# Prefijos: permiten distinguir lo generado de los datos semilla de mermax.sql
# y borrarlo después sin tocarlos.
P_MERMA = 'MRM-SEED-'
P_DISCREPANCIA = 'DSC-SEED-'
P_DISPOSICION = 'DSP-SEED-'
P_DEVOLUCION = 'DEV-SEED-'
P_RECICLAJE = 'RCJ-SEED-'
P_DESECHO = 'DES-SEED-'

# Hasta dónde avanza cada merma en el flujo (debe sumar 100)
DISTRIBUCION_ESTADOS = [
    ('CERRADA', 55),     # ciclo completo, con dictamen de disposición final
    ('INSPECCIO', 15),   # recibida y en manos del Ingeniero de Calidad
    ('RECIBIDA', 15),    # recibida en almacén, esperando inspección
    ('REGISTRADA', 10),  # apenas capturada por el supervisor
    ('DISCREPAN', 5),    # bloqueada por discrepancia en la recepción
]

# Cuánta merma aporta cada línea. Ver la nota de calibración de arriba.
PESO_POR_LINEA = {1: 12, 2: 19, 3: 32, 4: 19, 5: 18}

# Piezas por evento. La mayoría de las mermas son de 1 o 2 piezas; los eventos
# grandes existen pero son raros.
CANTIDADES = [1, 2, 3, 4, 5]
PESO_CANTIDADES = [35, 28, 20, 12, 5]

# Qué causa raíz es plausible para cada tipo de merma. Sin esto el ranking de
# causas del RF-12 sale con combinaciones sin sentido.
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

MOTIVOS_DISCREPANCIA = [
    'Faltante respecto a lo reportado por la línea.',
    'Una pieza no llegó al contenedor de scrap.',
    'Diferencia detectada en el conteo físico de recepción.',
    'Material incompleto al momento de la entrega.',
]


class Command(BaseCommand):
    help = 'Genera datos de merma recorriendo el flujo real, para que los triggers los completen.'

    def add_arguments(self, parser):
        parser.add_argument('--mermas', type=int, default=200,
                            help='Cuántas mermas generar (default: 200)')
        parser.add_argument('--dias', type=int, default=80,
                            help='Rango de días hacia atrás para las fechas (default: 80)')
        parser.add_argument('--limpiar', action='store_true',
                            help='Borra sólo lo generado por este comando y termina')

    # ==================================================================
    def handle(self, *args, **opts):
        if opts['limpiar']:
            return self._limpiar()

        self.total = opts['mermas']
        self.dias = opts['dias']
        self.hoy = date.today()

        combos = self._construir_combos()
        if not combos:
            self.stderr.write(self.style.ERROR(
                'No hay combinaciones válidas de componente/lote/estación/orden.\n'
                'Reimporta mermax.sql: necesita una orden de producción por estación.'
            ))
            return

        if not self._cargar_referencias():
            return

        estados = []
        for codigo, peso in DISTRIBUCION_ESTADOS:
            estados.extend([codigo] * peso)

        lineas = list(PESO_POR_LINEA.keys())
        pesos_lineas = [PESO_POR_LINEA[l] for l in lineas]

        consecutivo = RegistroMerma.objects.filter(folio__startswith=P_MERMA).count()

        contadores = {'mermas': 0, 'discrepancias': 0, 'solicitudes': 0,
                      'disposiciones': 0, 'rechazadas': 0}

        self.stdout.write(f'Generando {self.total} mermas recorriendo el flujo completo...')

        for i in range(self.total):
            linea = random.choices(lineas, weights=pesos_lineas)[0]
            disponibles = combos.get(linea)
            if not disponibles:
                continue

            n = consecutivo + i + 1
            try:
                with transaction.atomic():
                    self._procesar_una(
                        n=n,
                        combo=random.choice(disponibles),
                        estado_objetivo=random.choice(estados),
                        contadores=contadores,
                    )
            except Exception as e:
                contadores['rechazadas'] += 1
                if contadores['rechazadas'] <= 3:
                    self.stderr.write(self.style.WARNING(f'  {P_MERMA}{n:04d}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f"\nMermas creadas:            {contadores['mermas']}"
        ))
        self.stdout.write(
            f"Discrepancias insertadas:  {contadores['discrepancias']}  (bloquearon su folio via Trigger 3)"
        )
        self.stdout.write(
            f"Solicitudes generadas:     {contadores['solicitudes']}  (las creo el Trigger 2, no el script)"
        )
        self.stdout.write(
            f"Dictamenes de disposicion: {contadores['disposiciones']}"
        )
        if contadores['rechazadas']:
            self.stdout.write(self.style.WARNING(
                f"Rechazadas por los triggers: {contadores['rechazadas']}"
            ))

        self._resumen()

    # ==================================================================
    # El recorrido del flujo
    # ==================================================================
    def _procesar_una(self, n, combo, estado_objetivo, contadores):
        folio = f'{P_MERMA}{n:04d}'
        tipo = random.choice(self.tipos)
        codigo_causa = random.choice(CAUSAS_POR_TIPO.get(tipo.codigo, list(self.causas)))
        cantidad = Decimal(random.choices(CANTIDADES, weights=PESO_CANTIDADES)[0])
        fecha_merma = self.hoy - timedelta(days=random.randint(3, self.dias))

        # ---- PASO 1: el Supervisor registra la merma (RF-02) -----------
        # No se manda costo_total: lo calcula el Trigger 1.
        RegistroMerma.objects.create(
            folio=folio,
            cantidad=cantidad,
            fecha=fecha_merma,
            unidad='Pieza',
            descripcion=random.choice(DESCRIPCIONES),
            edo_flujo_merma_id='REGISTRADA',
            usuario=random.choice(self.supervisores),
            lote_material_id=combo['lote'],
            componente_id=combo['componente'],
            tipo_merma=tipo,
            causa_raiz=self.causas.get(codigo_causa),
            estacion_trabajo_id=combo['estacion'],
            orden_produccion_id=combo['orden'],
        )
        contadores['mermas'] += 1

        if estado_objetivo == 'REGISTRADA':
            return

        # ---- PASO 2: el Almacenista encuentra una diferencia (RF-05) ---
        if estado_objetivo == 'DISCREPAN':
            # cantidad_reportada debe coincidir con la merma o el Trigger 3
            # rechaza el insert. La diferencia la recalcula el trigger: aquí
            # se manda un valor cualquiera a propósito.
            faltante = Decimal(random.randint(1, int(cantidad)))
            Discrepancia.objects.create(
                folio=f'{P_DISCREPANCIA}{n:04d}',
                fecha=fecha_merma + timedelta(days=1),
                cantidad_reportada=cantidad,
                cantidad_recibida=cantidad - faltante,
                diferencia=Decimal('0'),          # el Trigger 3 lo sobreescribe
                motivo=random.choice(MOTIVOS_DISCREPANCIA),
                usuario=random.choice(self.almacenistas),
                registro_merma_id=folio,
            )
            contadores['discrepancias'] += 1
            return

        # ---- PASO 3: recepción sin diferencias (RF-04) ------------------
        # Este UPDATE dispara el Trigger 2, que crea la solicitud de
        # inspección solo porque el folio no tiene discrepancias.
        fecha_recepcion = fecha_merma + timedelta(days=1)
        RegistroMerma.objects.filter(folio=folio).update(edo_flujo_merma_id='RECIBIDA')
        contadores['solicitudes'] += 1

        if estado_objetivo == 'RECIBIDA':
            return

        # ---- PASO 4: el Ingeniero de Calidad toma la inspección (RF-07) -
        RegistroMerma.objects.filter(folio=folio).update(edo_flujo_merma_id='INSPECCIO')

        if estado_objetivo == 'INSPECCIO':
            return

        # ---- PASO 5: dictamen y cierre (RF-08, RF-09, RF-10) ------------
        fecha_dictamen = fecha_recepcion + timedelta(days=random.randint(1, 4))
        ingeniero = random.choice(self.ingenieros)

        # Marcar como atendida la solicitud que generó el trigger
        SolicitudInspeccion.objects.filter(registro_merma_id=folio).update(
            edo_solicitud_id='ATENDIDA',
            fecha_atencion=fecha_dictamen,
            hora_atencion=time(random.randint(8, 17), random.choice([0, 15, 30, 45])),
        )

        dictamen = random.choices(
            ['RECICLAJE', 'RTN_PROV', 'DESTR_CTRL'],
            weights=[55, 30, 15],
        )[0]

        folio_disp = f'{P_DISPOSICION}{n:04d}'
        RegistroDisposicion.objects.create(
            folio=folio_disp,
            fecha_determinacion=fecha_dictamen,
            fecha_ejecucion=fecha_dictamen + timedelta(days=1),
            cantidad_ejecutada=cantidad,
            observaciones=f'Dictamen emitido tras inspección del folio {folio}.',
            sale_almacen=self.almacen_scrap,
            llega_almacen=self.almacen_scrap,
            disposicion_final_id=dictamen,
            usuario=ingeniero,
            registro_merma_id=folio,
            estado_disposicion_id='EJECUTADO',
        )
        contadores['disposiciones'] += 1

        # Tabla satélite según el dictamen
        if dictamen == 'RECICLAJE':
            DisposicionReciclaje.objects.create(
                folio=f'{P_RECICLAJE}{n:04d}',
                empresa_recicladora=random.choice(self.recicladoras),
                peso_neto=cantidad * Decimal('0.85'),
                registro_disposicion_id=folio_disp,
            )
        elif dictamen == 'RTN_PROV':
            DisposicionDevolucion.objects.create(
                folio=f'{P_DEVOLUCION}{n:04d}',
                motivo_rechazo='Defecto atribuible al proveedor, detectado en línea.',
                registro_disposicion_id=folio_disp,
                # Se devuelve al proveedor que suministró el lote de origen
                proveedor_id=combo['proveedor'],
            )
        else:
            DisposicionDesecho.objects.create(
                folio=f'{P_DESECHO}{n:04d}',
                metodo_destruccion=random.choice(self.metodos),
                folio_probatorio=f'ACT-{n:06d}',   # el campo admite 10 caracteres
                registro_disposicion_id=folio_disp,
            )

        RegistroMerma.objects.filter(folio=folio).update(edo_flujo_merma_id='CERRADA')

    # ==================================================================
    # Preparación
    # ==================================================================
    def _cargar_referencias(self):
        self.supervisores = list(Usuario.objects.filter(rol='SUPER', activo=True))
        self.almacenistas = list(Usuario.objects.filter(rol='ALMAC', activo=True))
        self.ingenieros = list(Usuario.objects.filter(rol='CALID', activo=True))

        faltan = [n for n, v in (('SUPER', self.supervisores),
                                 ('ALMAC', self.almacenistas),
                                 ('CALID', self.ingenieros)) if not v]
        if faltan:
            self.stderr.write(self.style.ERROR(
                f'No hay usuarios activos con rol: {", ".join(faltan)}'
            ))
            return False

        self.tipos = list(TipoMerma.objects.filter(activo=True))
        self.causas = {c.codigo: c for c in CausaRaiz.objects.filter(activo=True)}
        self.recicladoras = list(EmpresaRecicladora.objects.filter(activo=True))
        self.metodos = list(MetodoDestruccion.objects.filter(activo=True))
        self.almacen_scrap = (Almacen.objects.filter(clave='ALM-SCRP').first()
                              or Almacen.objects.first())

        if not (self.tipos and self.causas and self.recicladoras and self.metodos):
            self.stderr.write(self.style.ERROR(
                'Faltan catálogos base (tipos de merma, causas raíz, recicladoras o métodos).'
            ))
            return False
        return True

    def _construir_combos(self):
        """
        Arma, agrupadas por línea, las combinaciones que el Trigger 1 acepta:
        componente + lote que lo contiene + estación + orden de esa estación.

        Se lee de la base en vez de escribirse a mano, para que siga
        funcionando si el equipo agrega líneas, estaciones o lotes.
        """
        ordenes_por_estacion = {}
        for orden in OrdenProduccion.objects.all():
            ordenes_por_estacion.setdefault(orden.estacion_trabajo_id, []).append(orden.numero)

        # COMP-01 se ensambla en la línea 1, COMP-02 en la 2, y así. Se deriva
        # del orden del catálogo en vez de dejarlo escrito a mano.
        codigos = list(Componente.objects.filter(activo=True)
                       .order_by('codigo').values_list('codigo', flat=True))
        linea_de_componente = {codigo: i + 1 for i, codigo in enumerate(codigos)}

        estaciones_por_linea = {}
        for est in EstacionTrabajo.objects.filter(activo=True):
            estaciones_por_linea.setdefault(est.linea_produccion_id, []).append(est.codigo)

        combos = {}
        for lote in LoteMaterial.objects.all():
            linea = linea_de_componente.get(lote.componente_id)
            if linea is None:
                continue
            for codigo_est in estaciones_por_linea.get(linea, []):
                for numero_orden in ordenes_por_estacion.get(codigo_est, []):
                    combos.setdefault(linea, []).append({
                        'componente': lote.componente_id,
                        'lote': lote.num,
                        'estacion': codigo_est,
                        'orden': numero_orden,
                        'proveedor': lote.proveedor_id,
                    })
        return combos

    # ==================================================================
    # Limpieza y resumen
    # ==================================================================
    def _limpiar(self):
        """Borra en orden inverso a las llaves foráneas."""
        pasos = [
            ('Devoluciones ', DisposicionDevolucion.objects.filter(folio__startswith=P_DEVOLUCION)),
            ('Reciclajes   ', DisposicionReciclaje.objects.filter(folio__startswith=P_RECICLAJE)),
            ('Desechos     ', DisposicionDesecho.objects.filter(folio__startswith=P_DESECHO)),
            ('Disposiciones', RegistroDisposicion.objects.filter(folio__startswith=P_DISPOSICION)),
            ('Solicitudes  ', SolicitudInspeccion.objects.filter(codigo__startswith=f'SOL-{P_MERMA}')),
            ('Discrepancias', Discrepancia.objects.filter(folio__startswith=P_DISCREPANCIA)),
            ('Mermas       ', RegistroMerma.objects.filter(folio__startswith=P_MERMA)),
        ]
        for nombre, qs in pasos:
            n, _ = qs.delete()
            self.stdout.write(f'  {nombre}: {n} borrados')
        self.stdout.write(self.style.SUCCESS(
            '\nListo. Los datos semilla de mermax.sql quedaron intactos.'
        ))

    def _resumen(self):
        from django.db.models import Count, Sum

        self.stdout.write('\n--- Mermas por estado del flujo ---')
        for fila in (RegistroMerma.objects
                     .values('edo_flujo_merma')
                     .annotate(n=Count('folio'), costo=Sum('costo_total'))
                     .order_by('-n')):
            costo = fila['costo'] or 0
            self.stdout.write(
                f"  {fila['edo_flujo_merma']:<12} {fila['n']:>5} mermas   $ {costo:>13,.2f}"
            )

        self.stdout.write('\n--- % de scrap por linea (KPI del RF-12) ---')
        producido = {}
        for to in TurnoOrden.objects.select_related('orden_produccion__estacion_trabajo'):
            linea = to.orden_produccion.estacion_trabajo.linea_produccion_id
            producido[linea] = producido.get(linea, 0) + (to.cantidad_producida or 0)

        mermado = {}
        for m in (RegistroMerma.objects
                  .select_related('estacion_trabajo')
                  .exclude(estacion_trabajo__isnull=True)):
            linea = m.estacion_trabajo.linea_produccion_id
            mermado[linea] = mermado.get(linea, 0) + float(m.cantidad)

        for linea in sorted(producido):
            piezas = mermado.get(linea, 0)
            total = producido[linea]
            pct = (piezas / total * 100) if total else 0
            semaforo = 'ALERTA' if pct >= 2.5 else 'ok'
            self.stdout.write(
                f'  Linea {linea}:  {piezas:>7,.0f} de {total:>7,} piezas   {pct:>5.2f} %   {semaforo}'
            )

        total_costo = RegistroMerma.objects.aggregate(c=Sum('costo_total'))['c'] or 0
        self.stdout.write(f'\n  Costo total acumulado: $ {total_costo:,.2f}')
        self.stdout.write('  (calculado por el Trigger 1, no por este script)')