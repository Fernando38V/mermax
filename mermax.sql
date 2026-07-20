CREATE DATABASE IF NOT EXISTS mermax_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mermax_db;

CREATE TABLE ESTADO_LINEA (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE TURNO (
    clave VARCHAR(10) NOT NULL,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    PRIMARY KEY (clave)
);

CREATE TABLE ESTADO_ORDEN (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE PRODUCTO (
    codigo VARCHAR(10) NOT NULL,
    modelo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100),
    descripcion VARCHAR(100),
    pulgadas DECIMAL(10,2),
    PRIMARY KEY (codigo)
);

CREATE TABLE COMPONENTE (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    costo DECIMAL(10,2),
    descripcion VARCHAR(100),
    tipo VARCHAR(50),
    PRIMARY KEY (codigo)
);

CREATE TABLE ROL (
    clave VARCHAR(10) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(100),
    PRIMARY KEY (clave)
);

CREATE TABLE EDO_FLUJO_MERMA (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE TIPO_MERMA (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(100),
    PRIMARY KEY (codigo)
);

CREATE TABLE CAUSA_RAIZ (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(100),
    PRIMARY KEY (codigo)
);

CREATE TABLE DISPOSICION_FINAL (
    clave VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(100),
    PRIMARY KEY (clave)
);

CREATE TABLE EDO_SOLICITUD (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE INDICADOR_KPI (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(50),
    formula VARCHAR(100),
    unidad VARCHAR(50),
    PRIMARY KEY (codigo)
);

CREATE TABLE ESTADO_ALERTA (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE PROVEEDOR (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    dirCalle VARCHAR(150),
    dirNumero VARCHAR(10),
    dirColonia VARCHAR(100),
    RFC VARCHAR(13),
    PRIMARY KEY (codigo)
);

CREATE TABLE ESTADO_LOTE (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE PLANTA (
    clave VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    numTel VARCHAR(20),
    dirCalle VARCHAR(150),
    dirNumero VARCHAR(10),
    dirColonia VARCHAR(100),
    PRIMARY KEY (clave)
);

CREATE TABLE ESTADO_DISPOSICION (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(25) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE AREA (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(100),
    planta VARCHAR(10) NOT NULL,
    PRIMARY KEY (codigo),
    CONSTRAINT fk_area_planta FOREIGN KEY (planta) REFERENCES PLANTA(clave)
);

CREATE TABLE ALMACEN (
    clave VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    ubicacion VARCHAR(200),
    tipo VARCHAR(50),
    capacidad DECIMAL(10,2),
    planta VARCHAR(10) NOT NULL,
    PRIMARY KEY (clave),
    CONSTRAINT fk_almacen_planta FOREIGN KEY (planta) REFERENCES PLANTA(clave)
);

CREATE TABLE LINEA_PRODUCCION (
    num INT AUTO_INCREMENT NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(100),
    numero_linea INT,
    area VARCHAR(10) NOT NULL,
    estado_linea VARCHAR(10) NOT NULL,
    PRIMARY KEY (num),
    CONSTRAINT fk_linea_produccion_area FOREIGN KEY (area) REFERENCES AREA(codigo),
    CONSTRAINT fk_linea_produccion_estado_linea FOREIGN KEY (estado_linea) REFERENCES ESTADO_LINEA(codigo)
);

CREATE TABLE EMPLEADO (
    numero INT AUTO_INCREMENT NOT NULL,
    emNombre VARCHAR(80) NOT NULL,
    emPrimerApell VARCHAR(80) NOT NULL,
    emSegundoApell VARCHAR(80),
    puesto VARCHAR(80),
    edad INT,
    fecha_ingreso DATE,
    area VARCHAR(10) NOT NULL,
    PRIMARY KEY (numero),
    CONSTRAINT fk_empleado_area FOREIGN KEY (area) REFERENCES AREA(codigo)
);

CREATE TABLE LINEA_TURNO (
    codigo VARCHAR(10) NOT NULL,
    fecha DATE NOT NULL,
    linea_produccion INT NOT NULL,
    turno VARCHAR(10) NOT NULL,
    PRIMARY KEY (codigo),
    CONSTRAINT fk_linea_turno_linea_produccion FOREIGN KEY (linea_produccion) REFERENCES LINEA_PRODUCCION(num),
    CONSTRAINT fk_linea_turno_turno FOREIGN KEY (turno) REFERENCES TURNO(clave)
);

CREATE TABLE ESTACION_TRABAJO (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    etapa VARCHAR(50),
    linea_produccion INT NOT NULL,
    PRIMARY KEY (codigo),
    CONSTRAINT fk_estacion_trabajo_linea_produccion FOREIGN KEY (linea_produccion) REFERENCES LINEA_PRODUCCION(num)
);

CREATE TABLE USUARIO (
    num INT AUTO_INCREMENT NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL,
    correo VARCHAR(50) NOT NULL,
    empleado INT NOT NULL UNIQUE,
    rol VARCHAR(10) NOT NULL,
    PRIMARY KEY (num),
    CONSTRAINT fk_usuario_empleado FOREIGN KEY (empleado) REFERENCES EMPLEADO(numero),
    CONSTRAINT fk_usuario_rol FOREIGN KEY (rol) REFERENCES ROL(clave)
);

CREATE TABLE UMBRAL_ALERTA (
    numero INT AUTO_INCREMENT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    activo BOOLEAN NOT NULL,
    indicador_kpi VARCHAR(10) NOT NULL,
    linea_produccion INT NOT NULL,
    PRIMARY KEY (numero),
    CONSTRAINT fk_umbral_alerta_indicador_kpi FOREIGN KEY (indicador_kpi) REFERENCES INDICADOR_KPI(codigo),
    CONSTRAINT fk_umbral_alerta_linea_produccion FOREIGN KEY (linea_produccion) REFERENCES LINEA_PRODUCCION(num)
);

CREATE TABLE LOTE_MATERIAL (
    num INT AUTO_INCREMENT NOT NULL,
    fecha DATE NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    caducidad DATE,
    numero_lote_prov VARCHAR(50),
    componente VARCHAR(10) NOT NULL,
    almacen VARCHAR(10) NOT NULL,
    estado_lote VARCHAR(10) NOT NULL,
    proveedor VARCHAR(10) NOT NULL,
    PRIMARY KEY (num),
    CONSTRAINT fk_lote_material_componente FOREIGN KEY (componente) REFERENCES COMPONENTE(codigo),
    CONSTRAINT fk_lote_material_almacen FOREIGN KEY (almacen) REFERENCES ALMACEN(clave),
    CONSTRAINT fk_lote_material_estado_lote FOREIGN KEY (estado_lote) REFERENCES ESTADO_LOTE(codigo),
    CONSTRAINT fk_lote_material_proveedor FOREIGN KEY (proveedor) REFERENCES PROVEEDOR(codigo)
);

CREATE TABLE ORDEN_PRODUCCION (
    numero INT AUTO_INCREMENT NOT NULL,
    cantidad_inicial INT NOT NULL,
    cantidad_final INT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    estacion_trabajo VARCHAR(10) NOT NULL,
    estado_orden VARCHAR(10) NOT NULL,
    PRIMARY KEY (numero),
    CONSTRAINT fk_orden_produccion_estacion_trabajo FOREIGN KEY (estacion_trabajo) REFERENCES ESTACION_TRABAJO(codigo),
    CONSTRAINT fk_orden_produccion_estado_orden FOREIGN KEY (estado_orden) REFERENCES ESTADO_ORDEN(codigo)
);

CREATE TABLE TURNO_ORDEN (
    clave VARCHAR(10) NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    cantidad_producida INT,
    turno VARCHAR(10) NOT NULL,
    orden_produccion INT NOT NULL,
    PRIMARY KEY (clave),
    CONSTRAINT fk_turno_orden_turno FOREIGN KEY (turno) REFERENCES TURNO(clave),
    CONSTRAINT fk_turno_orden_orden_produccion FOREIGN KEY (orden_produccion) REFERENCES ORDEN_PRODUCCION(numero)
);

CREATE TABLE ORDEN_PRODUCTO (
    orden INT NOT NULL,
    producto VARCHAR(10) NOT NULL,
    cantidad INT NOT NULL,
    PRIMARY KEY (orden, producto),
    CONSTRAINT fk_orden_producto_orden FOREIGN KEY (orden) REFERENCES ORDEN_PRODUCCION(numero),
    CONSTRAINT fk_orden_producto_producto FOREIGN KEY (producto) REFERENCES PRODUCTO(codigo)
);

CREATE TABLE PROD_COMP (
    producto VARCHAR(10) NOT NULL,
    componente VARCHAR(10) NOT NULL,
    unidad VARCHAR(20),
    cantidad_requerida DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (producto, componente),
    CONSTRAINT fk_prod_comp_producto FOREIGN KEY (producto) REFERENCES PRODUCTO(codigo),
    CONSTRAINT fk_prod_comp_componente FOREIGN KEY (componente) REFERENCES COMPONENTE(codigo)
);

CREATE TABLE ALERTA_GENERADA (
    num INT AUTO_INCREMENT NOT NULL,
    fecha DATE NOT NULL,
    observaciones VARCHAR(100),
    valor_detectado DECIMAL(10,2) NOT NULL,
    usuario INT,
    estado_alerta VARCHAR(10) NOT NULL,
    umbral_alerta INT NOT NULL,
    PRIMARY KEY (num),
    CONSTRAINT fk_alerta_generada_usuario FOREIGN KEY (usuario) REFERENCES USUARIO(num),
    CONSTRAINT fk_alerta_generada_estado_alerta FOREIGN KEY (estado_alerta) REFERENCES ESTADO_ALERTA(codigo),
    CONSTRAINT fk_alerta_generada_umbral_alerta FOREIGN KEY (umbral_alerta) REFERENCES UMBRAL_ALERTA(numero)
);

CREATE TABLE REGISTRO_MERMA (
    folio VARCHAR(20) NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    costo_total DECIMAL(10,2),
    fecha DATE NOT NULL,
    unidad VARCHAR(20) NOT NULL,
    descripcion VARCHAR(100),
    edo_flujo_merma VARCHAR(10) NOT NULL,
    usuario INT NOT NULL,
    lote_material INT,
    componente VARCHAR(10),
    tipo_merma VARCHAR(10) NOT NULL,
    causa_raiz VARCHAR(10),
    estacion_trabajo VARCHAR(10),
    orden_produccion INT,
    PRIMARY KEY (folio),
    CONSTRAINT fk_registro_merma_edo_flujo_merma FOREIGN KEY (edo_flujo_merma) REFERENCES EDO_FLUJO_MERMA(codigo),
    CONSTRAINT fk_registro_merma_usuario FOREIGN KEY (usuario) REFERENCES USUARIO(num),
    CONSTRAINT fk_registro_merma_lote_material FOREIGN KEY (lote_material) REFERENCES LOTE_MATERIAL(num),
    CONSTRAINT fk_registro_merma_componente FOREIGN KEY (componente) REFERENCES COMPONENTE(codigo),
    CONSTRAINT fk_registro_merma_tipo_merma FOREIGN KEY (tipo_merma) REFERENCES TIPO_MERMA(codigo),
    CONSTRAINT fk_registro_merma_causa_raiz FOREIGN KEY (causa_raiz) REFERENCES CAUSA_RAIZ(codigo),
    CONSTRAINT fk_registro_merma_estacion_trabajo FOREIGN KEY (estacion_trabajo) REFERENCES ESTACION_TRABAJO(codigo),
    CONSTRAINT fk_registro_merma_orden_produccion FOREIGN KEY (orden_produccion) REFERENCES ORDEN_PRODUCCION(numero)
);

CREATE TABLE DISCREPANCIA (
    folio VARCHAR(20) NOT NULL,
    fecha DATE NOT NULL,
    cantidad_reportada DECIMAL(10,2) NOT NULL,
    cantidad_recibida DECIMAL(10,2) NOT NULL,
    diferencia DECIMAL(10,2) NOT NULL,
    motivo VARCHAR(100),
    usuario INT NOT NULL,
    registro_merma VARCHAR(20),
    PRIMARY KEY (folio),
    CONSTRAINT fk_discrepancia_usuario FOREIGN KEY (usuario) REFERENCES USUARIO(num),
    CONSTRAINT fk_discrepancia_registro_merma FOREIGN KEY (registro_merma) REFERENCES REGISTRO_MERMA(folio)
);

CREATE TABLE SOLICITUD_INSPECCION (
    codigo VARCHAR(20) NOT NULL,
    fecha_generacion DATE NOT NULL,
    hora_generacion TIME NOT NULL,
    fecha_atencion DATE,
    hora_atencion TIME,
    edo_solicitud VARCHAR(10) NOT NULL,
    registro_merma VARCHAR(20),
    usuario INT NOT NULL,
    PRIMARY KEY (codigo),
    CONSTRAINT fk_solicitud_inspeccion_edo_solicitud FOREIGN KEY (edo_solicitud) REFERENCES EDO_SOLICITUD(codigo),
    CONSTRAINT fk_solicitud_inspeccion_registro_merma FOREIGN KEY (registro_merma) REFERENCES REGISTRO_MERMA(folio),
    CONSTRAINT fk_solicitud_inspeccion_usuario FOREIGN KEY (usuario) REFERENCES USUARIO(num)
);

CREATE TABLE REGISTRO_DISPOSICION (
    folio VARCHAR(20) NOT NULL,
    fecha_determinacion DATE NOT NULL,
    fecha_ejecucion DATE,
    cantidad_ejecutada DECIMAL(10,2),
    observaciones VARCHAR(255),
    motivo_rechazo VARCHAR(255) NOT NULL,
    empresa_recicladora VARCHAR(50) NOT NULL,
    peso_neto DECIMAL(10,2) NOT NULL,
    metodo_destruccion VARCHAR(30) NOT NULL,
    folio_probatorio VARCHAR(10) NOT NULL,
    sale_almacen VARCHAR(10),
    llega_almacen VARCHAR(10),
    disposicion_final VARCHAR(10) NOT NULL,
    usuario INT NOT NULL,
    registro_merma VARCHAR(20) NOT NULL,
    estado_disposicion VARCHAR(10) NOT NULL,
    PRIMARY KEY (folio),
    CONSTRAINT fk_registro_disposicion_sale_almacen FOREIGN KEY (sale_almacen) REFERENCES ALMACEN(clave),
    CONSTRAINT fk_registro_disposicion_llega_almacen FOREIGN KEY (llega_almacen) REFERENCES ALMACEN(clave),
    CONSTRAINT fk_registro_disposicion_disposicion_final FOREIGN KEY (disposicion_final) REFERENCES DISPOSICION_FINAL(clave),
    CONSTRAINT fk_registro_disposicion_usuario FOREIGN KEY (usuario) REFERENCES USUARIO(num),
    CONSTRAINT fk_registro_disposicion_registro_merma FOREIGN KEY (registro_merma) REFERENCES REGISTRO_MERMA(folio),
    CONSTRAINT fk_registro_disposicion_estado_disposicion FOREIGN KEY (estado_disposicion) REFERENCES ESTADO_DISPOSICION(codigo)
);

-- CATALOGO DE DATOS

INSERT INTO ESTADO_LINEA (codigo, nombre) VALUES
('PROD_NORM', 'Producción Normal Activa'),
('SETUP_MOD', 'Cambio de Modelo (Setup TV)'),
('STARTUP', 'Arranque y Estabilización'),
('MANT_PROG', 'Mantenimiento Programado'),
('MANT_CORR', 'Paro por Falla en Línea'),
('ESPERA_MAT', 'Espera de Componentes CKD'),
('PARO_CALID', 'Línea Detenida por Alta Merma'),
('FALLA_ROB', 'Falla en Robot de Carga (Panel)'),
('CALIB_OPT', 'Calibración de Estación Óptica'),
('LIMPIEZA', 'Limpieza de Sala Limpia (Cleanroom)'),
('PRUEBA_NUE', 'Corrida de Prueba (Nuevo Modelo)'),
('FALLA_CONV', 'Falla en Transportador/Conveyor'),
('ESPERA_PER', 'Falta de Operadores en Estación'),
('RETRABAJO', 'Línea en Modo Retrabajo Masivo'),
('BLOQ_LOTO', 'Bloqueo de Seguridad (LOTO)'),
('AUDIT_PROG', 'Auditoría de Proceso Activa'),
('FIN_TURNO', 'Cierre y Limpieza de Turno'),
('FALLA_TEST', 'Falla en Estación de Pruebas ATS'),
('RESETEO', 'Falla de Software en Atornilladoras'),
('FALLA_NEUM', 'Pérdida de Presión Neumática (Pick&Place)');

INSERT INTO TURNO (clave, nombre, hora_inicio, hora_fin) VALUES
('MAT_A', 'Matutino Ensambles A', '06:00:00', '14:00:00'),
('VESP_B', 'Vespertino Ensambles B', '14:00:00', '22:00:00'),
('NOC_C', 'Nocturno Ensambles C', '22:00:00', '06:00:00'),
('MIX_ADM', 'Administrativo e Ingeniería', '08:00:00', '17:00:00'),
('12H_D1', 'Jornada 12 Horas Día 1', '07:00:00', '19:00:00'),
('12H_N1', 'Jornada 12 Horas Noche 1', '19:00:00', '07:00:00'),
('FSEM_D', 'Fin de Semana Diurno', '06:00:00', '18:00:00'),
('FSEM_N', 'Fin de Semana Nocturno', '18:00:00', '06:00:00'),
('CAL_MAT', 'Aseguramiento Calidad Mañana', '05:30:00', '13:30:00'),
('CAL_VES', 'Aseguramiento Calidad Tarde', '13:30:00', '21:30:00'),
('CAL_NOC', 'Aseguramiento Calidad Noche', '21:30:00', '05:30:00'),
('MNT_MAT', 'Soporte Técnico Mañana', '05:45:00', '14:15:00'),
('MNT_VES', 'Soporte Técnico Tarde', '13:45:00', '22:15:00'),
('MNT_NOC', 'Soporte Técnico Noche', '21:45:00', '06:15:00'),
('LOG_MAT', 'Surtido Materiales Mañana', '06:00:00', '14:30:00'),
('LOG_VES', 'Surtido Materiales Tarde', '14:00:00', '22:30:00'),
('LOG_NOC', 'Surtido Materiales Noche', '22:00:00', '06:30:00'),
('REWORK_M', 'Estación Retrabajos Mañana', '06:00:00', '14:00:00'),
('REWORK_V', 'Estación Retrabajos Tarde', '14:00:00', '22:00:00'),
('GUARDIA', 'Guardia Soporte Crítico', '00:00:00', '23:59:59');

INSERT INTO ESTADO_ORDEN (codigo, nombre) VALUES
('PLAN', 'Planificada en ERP'),
('LIB_MAT', 'Materiales Asignados (Kitting)'),
('LANZADA', 'Lanzada a Línea de Ensamble'),
('EN_PROG', 'En Proceso de Ensamble'),
('PAUS_COMP', 'Detenida por Defecto en Lote Componente'),
('PAUS_MAQ', 'Detenida por Falla de Atornillado/Robot'),
('PAUS_QA', 'Retenida por Auditoría de Calidad'),
('ESPERA_L', 'Espera de Configuración de Plantilla'),
('REPROCESO', 'Detenida: Unidades a Retrabajo Crítico'),
('TERM_PARC', 'Terminada Parcial (Cierre de Turno)'),
('TERM_COMP', 'Terminada Totalmente'),
('AUDITADA', 'Aprobada por Control de Calidad Post-Ensamble'),
('CERR_COST', 'Cerrada y Costeada (Finanzas)'),
('CANC_ING', 'Cancelada por Cambio de Ingeniería (ECO)'),
('CANC_LOG', 'Cancelada por Desabasto de Paneles'),
('EXC_MERMA', 'Bloqueada por Exceso de Scrap/Merma'),
('URG_PROD', 'Prioridad Crítica en Ejecución'),
('HOLD_DIS', 'En Espera por Cambio de Diseño Exterior'),
('REVI_TOL', 'Detenida por Desviación de Tolerancia'),
('REPROG', 'Reprogramada en Plan Maestro');

INSERT INTO PRODUCTO (codigo, modelo, nombre, descripcion, pulgadas) VALUES
('TV-LED32', 'TV-LED-32HD-2026', 'Televisor LED 32" HD Basic', 'Televisor LED básico 32 pulgadas, empaque estándar', 32.00),
('TV-FHD43', 'TV-FHD-43SM-2026', 'Smart TV LED 43" Full HD', 'Televisor Inteligente 43 pulgadas resolución 1080p', 43.00),
('TV-UHD50', 'TV-UHD-504K-XT', 'Smart TV LED 50" 4K UHD', 'Televisor 4K económico con tecnología Direct LED', 50.00),
('TV-UHD55', 'TV-UHD-554K-XT', 'Smart TV LED 55" 4K Slim', 'Televisor 4K diseño delgado, marco de resina', 55.00),
('TV-UHD65', 'TV-UHD-654K-XT', 'Smart TV LED 65" 4K Standard', 'Televisor 4K gran formato retroiluminación trasera', 65.00),
('TV-QLED55', 'TV-QLED-55-PREM', 'Smart TV QLED 55" Premium', 'Televisor Quantum Dot 55 pulgadas tasa refresco 120Hz', 55.00),
('TV-QLED65', 'TV-QLED-65-PREM', 'Smart TV QLED 65" Premium', 'Televisor Quantum Dot 65 pulgadas marcos metálicos', 65.00),
('TV-QLED75', 'TV-QLED-75-CIN', 'Smart TV QLED 75" Cinema Ultra', 'Televisor de gama alta QLED formato cine de 75 pulgadas', 75.00),
('TV-QLED85', 'TV-QLED-85-MAST', 'Smart TV QLED 85" Master Room', 'Televisor masivo Premium QLED para teatros en casa', 85.00),
('TV-OLED55', 'TV-OLED-55-PRO', 'Televisor OLED 55" Professional', 'Pantalla autoemisiva OLED 55 pulgadas negros puros', 55.00),
('TV-OLED65', 'TV-OLED-65-PRO', 'Televisor OLED 65" Professional', 'Pantalla autoemisiva OLED 65 pulgadas chasis ultradelgado', 65.00),
('TV-OLED77', 'TV-OLED-77-ELITE', 'Televisor OLED 77" Elite Series', 'Gama ultra premium OLED con audio integrado en pantalla', 77.00),
('TV-MLED65', 'TV-MINILED-65-X', 'Smart TV MiniLED 65" High-Zone', 'Televisor MiniLED con 2000 zonas de atenuación local', 65.00),
('TV-MLED75', 'TV-MINILED-75-X', 'Smart TV MiniLED 75" High-Zone', 'Televisor MiniLED de alto brillo y gama dinámica ampliada', 75.00),
('TV-LED40', 'TV-LED-40FHD-2026', 'Televisor LED 40" Full HD', 'Televisor intermedio LED sin Smart TV para hotelería', 40.00),
('TV-UHD58', 'TV-UHD-584K-SL', 'Smart TV LED 58" 4K Home', 'Modelo de tamaño intermedio 58 pulgadas marcos delgados', 58.00),
('TV-QLED50', 'TV-QLED-50-MID', 'Smart TV QLED 50" Mid-Range', 'Televisor QLED de entrada para salas medianas', 50.00),
('TV-OLED48', 'TV-OLED-48-GAMER', 'Televisor OLED 48" Gaming Custom', 'Televisor optimizado para consolas de nueva generación', 48.00),
('TV-MLED85', 'TV-MINILED-85-ELITE', 'Smart TV MiniLED 85" Titan', 'Televisor gigante tecnología MiniLED brillo extremo', 85.00),
('TV-LED24', 'TV-LED-24HD-KIT', 'Mini TV LED 24" Cocina/Espacios', 'Televisor de formato pequeño para cocinas o dormitorios', 24.00);

INSERT INTO COMPONENTE (codigo, nombre, costo, descripcion, tipo) VALUES
('CEL-32HD', 'Panel Open Cell 32" HD', 28.00, 'Celda abierta de cristal líquido sin retroiluminación', 'Display / Panel'),
('CEL-43FHD', 'Panel Open Cell 43" FHD', 42.50, 'Celda abierta de cristal líquido resolución Full HD', 'Display / Panel'),
('CEL-55UHD', 'Panel Open Cell 55" 4K', 85.00, 'Celda abierta resolución 4K UHD estándar', 'Display / Panel'),
('CEL-65OLED', 'Módulo Display OLED 65" Pro', 290.00, 'Panel orgánico autoemisivo ensamblado con sustrato', 'Display / Panel'),
('MAIN-SM-A', 'Tarjeta Principal SoC Smart TV', 22.10, 'Placa base principal con procesador y WiFi integrado', 'Electrónica / PCB'),
('MAIN-OL-P', 'Tarjeta Principal OLED Ultra', 45.00, 'Placa de procesamiento de video de alta fidelidad', 'Electrónica / PCB'),
('POW-75W', 'Fuente de Poder SMPS 75W', 9.50, 'Tarjeta de alimentación conmutada para TV de 32"-43"', 'Eléctrico / PCB'),
('POW-180W', 'Fuente de Poder SMPS 180W', 18.20, 'Tarjeta de alimentación de alta corriente para QLED', 'Eléctrico / PCB'),
('TCON-4K', 'Tarjeta de Control de Tiempos T-CON 4K', 6.80, 'PCB de control de sincronización para paneles UHD', 'Electrónica / PCB'),
('LED-BACK50', 'Kit Tiras LED Backlight 50"', 8.40, 'Barras de iluminación LED para chasis trasero de 50"', 'Sistema Óptico'),
('DIF-FILM55', 'Lámina Difusora Óptica 55"', 3.10, 'Película plástica para homogeneizar la luz de los LED', 'Sistema Óptico'),
('RECP-IR', 'Módulo Receptor Infrarrojo e Indicador', 1.15, 'Pequeña PCB con sensor IR para control remoto y LED de standby', 'Electrónica'),
('CHAS-PL43', 'Chasis Plástico Trasero 40"-43"', 5.20, 'Carcasa trasera inyectada con orificios VESA', 'Estructural / Plástico'),
('BEZ-AL55', 'Bisel Frontal Metálico Premium 55"', 7.40, 'Marco embellecedor frontal de aluminio anodizado', 'Estructural / Metal'),
('SPK-15W', 'Módulo Altavoces Estéreo 15W', 2.90, 'Par de bocinas con arnés conector rápido', 'Audio'),
('CABLE-LVDS', 'Cable Flex de Señal LVDS 51 pines', 0.95, 'Cable plano flexible de interconexión Main a T-CON', 'Cableado / Flex'),
('BASE-STND', 'Pedestal de Soporte Central Metálico', 8.00, 'Base de sobremesa de aleación metálica con tornillos', 'Estructural'),
('WIFI-MOD', 'Módulo de Red Inalámbrica M.2', 3.50, 'Tarjeta secundaria Wi-Fi 6 + Bluetooth para Smart TV', 'Electrónica'),
('BOX-CRT55', 'Empaque de Cartón e Insertos EPS 55"', 4.60, 'Caja impresa con bloques protectores de unicel', 'Embalaje'),
('SCRW-SET', 'Kit de Tornillería General M3/M4', 0.40, 'Bolsa con juego de tornillos para ensamble mecánico', 'Fijación / Hardware');

INSERT INTO ROL (clave, nombre, descripcion) VALUES
('SUP_LINEA', 'Supervisor de Línea', 'Registra mermas en el ensamble de TV, asocia folios a órdenes y estaciones de trabajo'),
('ALMACEN', 'Almacenista', 'Gestiona inventario de componentes CKD, surte lotes y valida discrepancias de material'),
('ING_CALID', 'Ingeniero de Calidad', 'Inspecciona componentes rechazados, dictamina causa raíz y autoriza la disposición final'),
('ADMIN', 'Administrador', 'Control total del sistema, configuración de umbrales de alerta y gestión de usuarios');

INSERT INTO EDO_FLUJO_MERMA (codigo, nombre) VALUES
('REGISTRADA', 'Merma Registrada en Línea'),
('EN_ESPERA', 'En Espera de Inspección de Calidad'),
('INSP_PROC', 'En Proceso de Inspección Técnica'),
('RECH_CALID', 'Rechazada por Calidad (Requiere Análisis)'),
('APROB_DISP', 'Aprobada para Disposición Final'),
('EN_RETRAB', 'Enviada a Estación de Retrabajo / Reparación'),
('DICTAMINAD', 'Dictaminada (Causa Raíz Asignada)'),
('ESPERA_ALM', 'En Transmisión a Almacén de Scrap'),
('RECIB_SCRP', 'Recibida en Almacén de Desecho'),
('DISC_CANT', 'Detenida por Discrepancia en Cantidad'),
('AUT_DESTR', 'Autorizada para Destrucción'),
('EN_DESTR', 'En Proceso de Destrucción Física'),
('DESTRUIDA', 'Destrucción Confirmada / Concluida'),
('RECLAM_PRV', 'En Proceso de Reclamación a Proveedor'),
('APROB_PRV', 'Reclamación Aceptada por Proveedor'),
('RECUP_COMP', 'Componentes Recuperados Exitosamente'),
('DONACION', 'Autorizada para Donación (Fines Educativos)'),
('AUDITADA', 'Bajo Auditoría de Inventarios'),
('CONCILIADA', 'Conciliada Contablemente / Finanzas'),
('CERRADA', 'Flujo de Merma Cerrado / Archivado');

INSERT INTO TIPO_MERMA (codigo, nombre, descripcion) VALUES
('FRACT_CEL', 'Fractura de Celda / Open Cell', 'Rotura o fisura en el cristal líquido del panel del televisor'),
('RAY_POLAR', 'Rayón en Película Polarizada', 'Daño estético superficial en el filtro polarizador frontal del panel'),
('CONT_PTIC', 'Contaminación Óptica (Polvo)', 'Partículas atrapadas entre las láminas difusoras o el backlight'),
('CORTO_PCB', 'Cortocircuito en PCB (Main/Power)', 'Falla eléctrica por cortocircuito en tarjetas lógicas o fuentes'),
('SOLD_CRUD', 'Soldadura Cría / Soldadura Fría', 'Falla de conectividad en terminales soldadas de las placas electrónicas'),
('FLEX_COMP', 'Flex de Señal Dañado / Roto', 'Rasgaduras o dobleces excesivos en los cables planos LVDS/Flex'),
('CON_ROTO', 'Conector Rápido Quebrado', 'Ruptura de los pines plásticos de conexión de audio, alimentación o IR'),
('LED_QUEM', 'Diodo LED Backlight Inoperativo', 'Tiras de LED con diodos fundidos o con bajo brillo detectadas en prueba'),
('BISEL_DEF', 'Bisel Deformado / Rallado', 'Deformación mecánica o daño estético en el marco frontal del televisor'),
('CHAS_TRAS', 'Gabinete Trasero Fisurado', 'Carcasa plástica posterior con impactos o perforaciones erróneas'),
('ERR_FIRM', 'Falla Crítica de Firmware (Ladrillo)', 'Tarjeta principal inaccesible por error de flasheo irrecuperable en línea'),
('EMB_DANAD', 'Empaque / Unicel Dañado', 'Cajas de cartón corrugado o insertos EPS rotos que no protegen el TV'),
('SOP_TRAS', 'Inserto VESA Barrido', 'Roscas metálicas traseras dañadas por exceso de torque al atornillar'),
('AUDIO_DEF', 'Altavoz Defectuoso (Bocina)', 'Componente de audio con distorsión, cono roto o sin emisión de sonido'),
('TCON_FAIL', 'Falla en Circuito T-CON', 'Líneas verticales o distorsión total de color por falla en la tarjeta de tiempos'),
('SENS_IR_F', 'Falla en Sensor Infrarrojo', 'Incapacidad de la tarjeta receptora para leer la señal del control remoto'),
('TORQ_EXC', 'Tornillo Descabezado / Atrapado', 'Tornillo roto dentro del chasis debido a mala calibración de atornilladora'),
('PIEZA_CKD', 'Material CKD Faltante en Kit', 'Componentes incompletos dentro del lote provisto para el ensamble'),
('DONUT_QA', 'Muestra Destructiva de Auditoría', 'Televisores sacrificados intencionalmente para pruebas de estrés y laboratorio'),
('OBSOLET', 'Obsolescencia por Cambio de Ingeniería', 'Componentes obsoletos que quedan fuera de uso por un cambio de diseño (ECO)');

INSERT INTO CAUSA_RAIZ (codigo, nombre, descripcion) VALUES
('ERR_OPER', 'Error de Operación / Mala Manipulación', 'El operador dañó el componente manualmente durante el ensamble'),
('MANIP_ALM', 'Manejo Inadecuado en Almacén', 'Golpes o caídas del material durante el traslado o kitting'),
('EXC_TORQ', 'Exceso de Torque en Atornilladora', 'Herramienta neumática/eléctrica mal calibrada que rompe el componente'),
('FALLA_ROB', 'Falla de Calibración en Robot Pick&Place', 'Desalineación del brazo robótico al colocar el panel sobre el chasis'),
('ESD_DISCH', 'Descarga Electrostática (ESD)', 'Falta de uso de pulsera antiestática que quemó la tarjeta electrónica'),
('DEF_PROV', 'Defecto Intrínseco de Proveedor', 'El componente venía defectuoso de fábrica antes de ser ensamblado'),
('CONT_MESA', 'Contaminación en Mesa de Ensamble', 'Presencia de partículas o residuos en la estación que rayaron el panel'),
('CAIDA_CON', 'Caída desde Transportador (Conveyor)', 'Falla en los topes de la línea que provocó la caída del televisor'),
('TEMP_HOR', 'Temperatura Incorrecta en Horno de Soldadura', 'Estrés térmico que dañó los componentes de la Main Board'),
('MAQ_DESCA', 'Maquinaria Descalibrada', 'Prensas o herramentales fuera de parámetros geométricos tolerados'),
('ERR_DISE', 'Error de Diseño / Ajuste Mecánico Insuficiente', 'El bisel ejerce demasiada presión sobre el panel por diseño erróneo'),
('EXP_IND', 'Exposición Inadecuada a la Humedad', 'Componentes almacenados sin bolsas desecantes que sufrieron corrosión'),
('USO_HERR', 'Uso de Herramienta Incorrecta', 'El operador utilizó utensilios no autorizados para ajustar una pieza'),
('EMB_DEF', 'Embalaje Defectuoso de Origen', 'Caja del proveedor muy débil que causó daños por vibración en el trayecto'),
('VOLT_INP', 'Pico de Voltaje en Línea de Pruebas', 'Sobrecarga eléctrica en la estación de encendido y prueba funcional'),
('FALT_TRA', 'Falta de Entrenamiento / Capacitación', 'Operador nuevo ejecutando la tarea sin la certificación requerida'),
('VEL_EXCE', 'Velocidad de Línea Excesiva', 'Ritmo de producción (Takt Time) acelerado que induce a errores humanos'),
('ILUM_DEF', 'Iluminación Deficiente en Estación', 'Baja visibilidad que impidió al operador alinear correctamente el flex'),
('MNT_PND', 'Falta de Mantenimiento Preventivo', 'Herramientas desgastadas que no recibieron servicio a tiempo'),
('DESV_STD', 'Desviación de Procedimiento Estándar (POE)', 'El personal no siguió el método de trabajo aprobado para el ensamble');

INSERT INTO DISPOSICION_FINAL (clave, nombre, descripcion) VALUES
('SCRAP_TOT', 'Destrucción Total (Scrap)', 'El material no tiene salvación ni valor de recuperación, va a trituración'),
('REWORK_LN', 'Retrabajo en Línea', 'El defecto se corrige inmediatamente en la misma línea de producción'),
('REWORK_ST', 'Enviado a Estación de Retrabajos', 'Se mueve a un área especializada fuera de línea para reparación detallada'),
('RTN_PROV', 'Retorno a Proveedor (Garantía)', 'Componente defectuoso de origen que se devuelve para nota de crédito o cambio'),
('REC_COMP', 'Recuperación de Componentes', 'El televisor se desarma para salvar piezas funcionales (Main Board, bocinas, etc.)'),
('RECIC_MET', 'Reciclaje de Metal / Aluminio', 'Envío de biseles y soportes deformados a fundición externa autorizada'),
('RECIC_PLA', 'Reciclaje de Plástico (Chasis)', 'Trituración y peletizado de carcasas traseras plásticas dañadas'),
('VENTA_EMP', 'Venta a Empleados (Clase B)', 'Televisores con detalles estéticos mínimos que se venden a precio de costo'),
('DONACION', 'Donación Institucional', 'Equipo funcional con detalles cosméticos destinado a escuelas o fundaciones'),
('LAB_ANALI', 'Envío a Laboratorio de Análisis', 'Retención permanente de la pieza para estudios metalúrgicos o de fallas en QA'),
('RE-INSP', 'Re-Inspección post-ajuste', 'El componente se somete a una segunda ronda de pruebas tras calibración'),
('MERMA_ING', 'Uso por Ingeniería / Prototipos', 'Material destinado a pruebas de desarrollo de nuevos modelos de TV'),
('RECH_ABSO', 'Obsolescencia Inmediata', 'Material obsoleto que se desecha por políticas de fin de ciclo de vida del producto'),
('HAZ_WASTE', 'Residuo Peligroso (Baterías/Químicos)', 'Disposición especial controlada para soldaduras, químicos de limpieza o baterías'),
('DISP_PEND', 'Disposición en Retención (Hold)', 'Material congelado a la espera de un dictamen definitivo corporativo'),
('TRFR_OTRA', 'Transferencia a Otra Planta', 'Material enviado a una planta hermana que utiliza la misma tecnología de panel'),
('DESTR_CER', 'Destrucción Certificada Fiscal', 'Scrap de alto valor que requiere presencia de un auditor fiscal para dar de baja'),
('RE-EMPAQ', 'Re-Empacado', 'El producto está perfecto pero el empaque se dañó; se cambia la caja y unicel'),
('DON_ESM', 'Desecho Electrónico Especializado (E-Waste)', 'Envío de PCBs a empresas autorizadas para la extracción regulada de metales preciosos'),
('SUBASTA', 'Venta por Lote de Recuperación', 'Venta en subasta de componentes dañados a empresas terceras de reconstrucción');

INSERT INTO EDO_SOLICITUD (codigo, nombre) VALUES
('NUEVA', 'Nueva / Pendiente de Asignación'),
('ASIGNADA', 'Asignada a Ingeniero de Calidad'),
('EN_ESPERA', 'En Espera de Muestra Física'),
('RECIBIDA', 'Muestra Recibida en Laboratorio'),
('EN_ANALIS', 'En Análisis Técnico / Pruebas'),
('ESPERA_DOC', 'Detenida por Falta de Documentación'),
('PRUEBA_FT', 'En Pruebas de Funcionamiento Térmico'),
('PRUEBA_EL', 'En Pruebas de Estrés Eléctrico'),
('ESPERA_PRV', 'En Espera de Respuesta del Proveedor'),
('REVIS_ING', 'En Revisión conjunta con Ingeniería'),
('PRE_DICTAM', 'Pre-Dictaminada / Pendiente de Firma'),
('APROBADA', 'Dictamen Aprobado'),
('RECHAZADA', 'Solicitud Rechazada por Datos Incorrectos'),
('URGENTE', 'Prioridad Alta / Bloqueo de Línea'),
('COMPLETA', 'Inspección Concluida'),
('CONGELADA', 'Detenida por Cambio de Prioridad'),
('EXC_TIEMPO', 'Vencida / Fuera de SLA de Respuesta'),
('REABIERTA', 'Reabierta por Discrepancia en Dictamen'),
('CANCELADA', 'Cancelada por el Supervisor'),
('ARCHIVADA', 'Cerrada e Histórica');

REPLACE INTO INDICADOR_KPI (codigo, nombre, descripcion, formula, unidad) VALUES
('KPI-SCRP-R', 'Tasa Global de Scrap (Merma)', 'Porcentaje total de componentes mermados del inventario', '(Componentes Mermados / Componentes Introducidos) * 100', '%'),
('KPI-FTY', 'Rendimiento a la Primera (First Time Yield)', 'Porcentaje de TVs que pasan las pruebas sin retrabajos', '(TVs Aprobadas sin Defectos / Total TVs Ensambladas) * 100', '%'),
('KPI-DPMO', 'Defectos por Millón de Oportunidades', 'Densidad de defectos electrónicos en el ensamble de PCBs', '(Total Defectos / (Unidades * Oportunidades)) * 1000000', 'PPM'),
('KPI-SCRP-C', 'Costo Financiero de Merma', 'Impacto económico bruto por destrucción de material', 'Sumatoria(Cantidad Mermada * Costo Unitario Componente)', 'USD'),
('KPI-SCRP-P', 'Tasa de Merma en Paneles (Open Cell)', 'Porcentaje de paneles de TV dañados en el ensamble', '(Paneles Mermados / Total Paneles Surtidos) * 100', '%'),
('KPI-SCRP-M', 'Tasa de Merma en Main Boards', 'Porcentaje de tarjetas madre dañadas por ESD o fallas', '(Main Boards Mermadas / Total Tarjetas Surtidas) * 100', '%'),
('KPI-RWRK-T', 'Tasa de Retrabajo Operativo', 'Porcentaje de televisores enviados a reparación en línea', '(TVs Enviadas a Retrabajo / Total TVs Producidas) * 100', '%'),
('KPI-REC-CO', 'Tasa de Recuperación de Insumos', 'Porcentaje de componentes rescatados de TVs defectuosos', '(Componentes Salvados / Total Componentes Desensamblados) * 100', '%'),
('KPI-SLA-QA', 'Tiempo de Respuesta de Calidad (SLA)', 'Promedio de horas invertidas en dictaminar una solicitud', 'Promedio(Fecha_Atencion - Fecha_Generacion)', 'Horas'),
('KPI-DISC-V', 'Variación de Inventario por Discrepancia', 'Porcentaje de diferencia entre material enviado y recibido', '((Cant_Reportada - Cant_Recibida) / Cant_Reportada) * 100', '%'),
('KPI-OEE', 'Efectividad Global del Equipo (OEE)', 'Eficiencia integral de la línea de ensamble de TV', 'Disponibilidad * Rendimiento * Calidad', '%'),
('KPI-SCRP-E', 'Merma por Daño en Empaque', 'Porcentaje de cajas e insertos de unicel desechados', '(Cajas Mermadas / Total Cajas Utilizadas) * 100', '%'),
('KPI-MTBF', 'Tiempo Medio Entre Fallas de Herramental', 'Tiempo promedio operativo de atornilladores y robots', 'Tiempo Operativo Total / Número de Fallas', 'Horas'),
('KPI-MTTR', 'Tiempo Medio de Reparación', 'Tiempo promedio para solucionar fallas en las estaciones', 'Tiempo Total de Mantenimiento / Número de Intervenciones', 'Minutos'),
('KPI-SCRP-INI', 'Tasa de Scrap por Arranque (Startup)', 'Merma generada únicamente en los arranques de línea', '(Material Mermado en Startup / Total Surtido en Startup) * 100', '%'),
('KPI-SCRP-CFG', 'Merma por Configuración (Setup)', 'Desperdicio generado durante los cambios de modelo', 'Cantidad Mermada durante el Cambio de Modelo', 'Piezas'),
('KPI-PRV-RE', 'Índice de Rechazo a Proveedores', 'Porcentaje de lotes CKD devueltos íntegros a origen', '(Lotes Devueltos / Total Lotes Recibidos) * 100', '%'),
('KPI-TORQ-F', 'Tasa de Fallas por Torque Excesivo', 'Incidencia de tornillos barridos o carcasas fisuradas', '(Fallas de Atornillado / Total Tornillos Insertados) * 1000000', 'PPM'),
('KPI-ESD-IN', 'Incidencia de Daño por Estática (ESD)', 'Placas electrónicas quemadas por fallas de pulsera antiestática', 'Total PCBs Dañadas por ESD', 'Piezas'),
('KPI-COST-W', 'Costo de Merma por Unidad Producida', 'Dinero perdido en desperdicio prorrateado por cada TV útil', 'Costo Financiero de Merma / Total TVs Aprobadas', 'USD/unidad');

INSERT INTO ESTADO_ALERTA (codigo, nombre) VALUES
('ACTIVA', 'Alerta Activa / Disparada'),
('NOTIFICAD', 'Notificación Enviada'),
('LEIDA', 'Alerta Leída'),
('EN_PROCES', 'En Proceso de Investigación'),
('REQ_ACCIO', 'Requiere Acción Correctiva'),
('ESPERA_MNT', 'En Espera de Mantenimiento'),
('MONITOREO', 'En Monitoreo Temporal'),
('FALSA_ALM', 'Falsa Alarma / Error de Sensor'),
('MITIGADA', 'Mitigada Parcialmente'),
('ESPERA_ING', 'En Espera de Ingeniería'),
('CONTENIDA', 'Material Contenido'),
('ESPERA_PRV', 'Espera de Contención de Proveedor'),
('REABIERTA', 'Alerta Reabierta'),
('VENCIDA', 'Vencida sin Atención'),
('ESCALADA', 'Escalada a Gerencia'),
('CERRADA_OK', 'Cerrada - Solucionada'),
('CERRADA_FA', 'Cerrada - Falsa Alarma'),
('CERRADA_EX', 'Cerrada - Excepción Autorizada'),
('SUSPENDID', 'Monitoreo Suspendido'),
('ARCHIVADA', 'Histórica / Archivada');

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO ALERTA_GENERADA (fecha, observaciones, valor_detectado, usuario, estado_alerta, umbral_alerta) VALUES
('2026-07-10', 'Pico de scrap en paneles de 65 OLED en Línea 1 por mala manipulación.', 4.20, 1, 'CERRADA_OK', 1),
('2026-07-20', 'Densidad de defectos alta en lote SMT de Main Boards.', 1450.00, 3, 'ACTIVA', 2),
('2026-07-18', 'Costo de merma semanal excedido debido a celdas open cell.', 12500.00, 4, 'ESCALADA', 3),
('2026-07-19', 'Fallas por torque excesivo en estación de atornillado chasis-panel.', 850.00, 1, 'EN_PROCES', 4),
('2026-07-19', 'Múltiples PCBs quemadas en pruebas funcionales; falla en tierra.', 12.00, 3, 'CONTENIDA', 5),
('2026-07-17', 'Rechazo de tarjetas Main Board por fallas críticas de firmware.', 3.80, 3, 'REQ_ACCIO', 2),
('2026-07-15', 'Línea 3 enviando demasiados TVs a retrabajo por bisel frontal.', 8.50, 1, 'MONITOREO', 1),
('2026-07-12', 'El tiempo de dictamen de laboratorio superó las 24 horas.', 26.50, 3, 'VENCIDA', 3),
('2026-07-14', 'Discrepancia de inventario en Almacén. Error de captura Turno A.', 5.20, 2, 'FALSA_ALM', 5),
('2026-07-11', 'Cajas de empaque reportadas rotas por flejado de proveedor.', 3.10, 2, 'CERRADA_FA', 4),
('2026-07-16', 'Lote de conectores rápidos quebrado de origen.', 15.00, 2, 'ESPERA_PRV', 2),
('2026-07-08', 'Merma por cambio de modelo (55 a 75) excedió el estándar.', 45.00, 1, 'CERRADA_EX', 1),
('2026-07-20', 'Scrap excesivo durante el arranque de producción en Línea 2.', 18.00, 1, 'ACTIVA', 4),
('2026-07-20', 'Robot Pick & Place descalibrado; mantenimiento tardó en reparar.', 45.00, 4, 'LEIDA', 3),
('2026-07-20', 'Paneles rayados reportados en inspección cosmética final.', 3.10, 3, 'ACTIVA', 1),
('2026-07-05', 'Fallas en soldadura SMT resueltas tras ajustar perfiles.', 620.00, 3, 'CERRADA_OK', 2),
('2026-07-20', 'Estación de atornillado reporta estática. Operador sin pulsera.', 6.00, 1, 'ACTIVA', 5),
('2026-07-17', 'El costo de scrap prorrateado por TV útil es crítico.', 4.50, 4, 'ESCALADA', 3),
('2026-07-19', 'El First Time Yield cayó al 88% en el turno nocturno.', 88.00, 3, 'REQ_ACCIO', 2),
('2026-07-06', 'Atornilladoras neumáticas recalibradas por metrología.', 410.00, 1, 'CERRADA_OK', 4);

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO SOLICITUD_INSPECCION (codigo, fecha_generacion, hora_generacion, fecha_atencion, hora_atencion, edo_solicitud, registro_merma, usuario) VALUES
('SOL-2026-001', '2026-07-02', '08:30:00', '2026-07-02', '14:15:00', 'APROBADA', 'MRM-2026-001', 3),
('SOL-2026-002', '2026-07-05', '09:15:00', '2026-07-06', '10:00:00', 'COMPLETA', 'MRM-2026-002', 3),
('SOL-2026-003', '2026-07-06', '11:45:00', NULL, NULL, 'NUEVA', 'MRM-2026-003', 3),
('SOL-2026-004', '2026-07-08', '14:20:00', '2026-07-08', '16:30:00', 'EN_ANALIS', 'MRM-2026-004', 3),
('SOL-2026-005', '2026-07-10', '07:10:00', '2026-07-10', '08:45:00', 'RECHAZADA', 'MRM-2026-005', 2),
('SOL-2026-006', '2026-07-11', '10:00:00', '2026-07-11', '12:00:00', 'COMPLETA', 'MRM-2026-006', 1),
('SOL-2026-007', '2026-07-12', '16:35:00', NULL, NULL, 'EN_ANALIS', 'MRM-2026-007', 3),
('SOL-2026-008', '2026-07-13', '13:12:00', '2026-07-14', '09:00:00', 'APROBADA', 'MRM-2026-008', 2),
('SOL-2026-009', '2026-07-14', '15:40:00', NULL, NULL, 'ASIGNADA', 'MRM-2026-009', 3),
('SOL-2026-010', '2026-07-15', '08:50:00', NULL, NULL, 'EN_ANALIS', 'MRM-2026-010', 1),
('SOL-2026-011', '2026-07-15', '11:15:00', '2026-07-15', '15:00:00', 'COMPLETA', 'MRM-2026-011', 3),
('SOL-2026-012', '2026-07-16', '12:05:00', '2026-07-16', '17:20:00', 'APROBADA', 'MRM-2026-012', 3),
('SOL-2026-013', '2026-07-17', '14:30:00', NULL, NULL, 'EN_ESPERA', 'MRM-2026-013', 2),
('SOL-2026-014', '2026-07-18', '09:25:00', NULL, NULL, 'EN_ANALIS', 'MRM-2026-014', 1),
('SOL-2026-015', '2026-07-18', '10:50:00', '2026-07-18', '11:40:00', 'RECHAZADA', 'MRM-2026-015', 3),
('SOL-2026-016', '2026-07-19', '11:00:00', '2026-07-19', '16:00:00', 'APROBADA', 'MRM-2026-016', 2),
('SOL-2026-017', '2026-07-19', '15:10:00', NULL, NULL, 'EN_ANALIS', 'MRM-2026-017', 3),
('SOL-2026-018', '2026-07-20', '08:20:00', NULL, NULL, 'URGENTE', 'MRM-2026-018', 3),
('SOL-2026-019', '2026-07-20', '10:05:00', '2026-07-20', '12:30:00', 'APROBADA', 'MRM-2026-019', 3),
('SOL-2026-020', '2026-07-20', '13:00:00', NULL, NULL, 'EN_ANALIS', 'MRM-2026-020', 1);

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO REGISTRO_MERMA (folio, cantidad, costo_total, fecha, unidad, descripcion, edo_flujo_merma, usuario, lote_material, componente, tipo_merma, causa_raiz, estacion_trabajo, orden_produccion) VALUES
('MRM-2026-001', 5.00, 140.00, '2026-07-02', 'Piezas', 'Paneles de 32" fracturados durante el ensamble manual.', 'APROB_DISP', 3, 1, 'CEL-32HD', 'FRACT_CEL', 'ERR_OPER', 'EST-01', 1),
('MRM-2026-002', 12.00, 510.00, '2026-07-05', 'Piezas', 'Biseles frontales de 43" rayados detectados en cosméticos.', 'CERRADA', 3, 2, 'BEZ-AL55', 'BISEL_DEF', 'DEF_PROV', 'EST-02', 2),
('MRM-2026-003', 2.00, 170.00, '2026-07-06', 'Piezas', 'Paneles de 55" con líneas verticales fijas.', 'REGISTRADA', 3, 3, 'CEL-55UHD', 'TCON_FAIL', 'DEF_PROV', 'EST-03', 3),
('MRM-2026-004', 15.00, 331.50, '2026-07-08', 'Piezas', 'Tarjetas Main Board Smart TV con boot loop tras flasheo.', 'INSP_PROC', 3, 4, 'MAIN-SM-A', 'ERR_FIRM', 'ERR_DISE', 'EST-04', 4),
('MRM-2026-005', 50.00, 230.00, '2026-07-10', 'Piezas', 'Cajas de empaque mojadas por filtración en contenedor.', 'RECH_CALID', 2, 5, 'BOX-CRT55', 'EMB_DANAD', 'MANIP_ALM', 'EST-05', 5),
('MRM-2026-006', 8.00, 3.20, '2026-07-11', 'Piezas', 'Tornillos M4 degollados por exceso de torque neumático.', 'CERRADA', 1, 6, 'SCRW-SET', 'TORQ_EXC', 'EXC_TORQ', 'EST-06', 6),
('MRM-2026-007', 3.00, 870.00, '2026-07-12', 'Piezas', 'Módulos OLED 65" con retención de imagen severa en test.', 'INSP_PROC', 3, 7, 'CEL-65OLED', 'FRACT_CEL', 'VOLT_INP', 'EST-07', 7),
('MRM-2026-008', 100.00, 40.00, '2026-07-13', 'Piezas', 'Kits de tornillería incompletos reportados por operador.', 'APROB_DISP', 2, 8, 'SCRW-SET', 'PIEZA_CKD', 'DEF_PROV', 'EST-08', 8),
('MRM-2026-009', 4.00, 12.40, '2026-07-14', 'Piezas', 'Películas difusoras de 55" con burbujas de aire.', 'EN_ESPERA', 3, 9, 'DIF-FILM55', 'CONT_PTIC', 'CONT_MESA', 'EST-09', 9),
('MRM-2026-010', 25.00, 23.75, '2026-07-15', 'Piezas', 'Cables Flex LVDS rasgados durante la inserción rápida.', 'INSP_PROC', 1, 10, 'CABLE-LVDS', 'FLEX_COMP', 'FALT_TRA', 'EST-10', 10),
('MRM-2026-011', 6.00, 57.00, '2026-07-15', 'Piezas', 'Fuentes de poder quemadas en la estación de Hi-Pot.', 'CERRADA', 3, 11, 'POW-75W', 'CORTO_PCB', 'VOLT_INP', 'EST-11', 11),
('MRM-2026-012', 14.00, 117.60, '2026-07-16', 'Piezas', 'Tiras LED de 50" con diodos apagados de fábrica.', 'APROB_DISP', 3, 12, 'LED-BACK50', 'LED_QUEM', 'DEF_PROV', 'EST-12', 12),
('MRM-2026-013', 40.00, 140.00, '2026-07-17', 'Piezas', 'Módulos WiFi rayados por fricción en charolas CKD.', 'EN_ESPERA', 2, 13, 'WIFI-MOD', 'CON_ROTO', 'MANIP_ALM', 'EST-13', 13),
('MRM-2026-014', 10.00, 450.00, '2026-07-18', 'Piezas', 'Main Boards de gama alta dañadas por choque estático.', 'INSP_PROC', 1, 14, 'MAIN-OL-P', 'CORTO_PCB', 'ESD_DISCH', 'EST-14', 14),
('MRM-2026-015', 30.00, 156.00, '2026-07-18', 'Piezas', 'Gabinetes traseros plásticos agrietados por estiba masiva.', 'RECH_CALID', 3, 15, 'CHAS-PL43', 'CHAS_TRAS', 'MANIP_ALM', 'EST-15', 15),
('MRM-2026-016', 18.00, 52.20, '2026-07-19', 'Piezas', 'Bocinas de 15W con el cono roto de origen.', 'APROB_DISP', 2, 16, 'SPK-15W', 'AUDIO_DEF', 'DEF_PROV', 'EST-16', 16),
('MRM-2026-017', 5.00, 91.00, '2026-07-19', 'Piezas', 'Fuentes de 180W con soldaduras frías en transformador.', 'INSP_PROC', 3, 17, 'POW-180W', 'SOLD_CRUD', 'TEMP_HOR', 'EST-17', 17),
('MRM-2026-018', 2.00, 16.00, '2026-07-20', 'Piezas', 'Bases metálicas de pedestal con roscas barridas.', 'REGISTRADA', 3, 18, 'BASE-STND', 'SOP_TRAS', 'EXC_TORQ', 'EST-18', 18),
('MRM-2026-019', 1.00, 290.00, '2026-07-20', 'Piezas', 'Módulo OLED rayado accidentalmente con herramienta.', 'APROB_DISP', 3, 19, 'CEL-65OLED', 'RAY_POLAR', 'USO_HERR', 'EST-19', 19),
('MRM-2026-020', 10.00, 11.50, '2026-07-20', 'Piezas', 'Sensores IR con cables trozados en desempaque.', 'INSP_PROC', 1, 20, 'RECP-IR', 'SENS_IR_F', 'VEL_EXCE', 'EST-20', 20);

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO DISCREPANCIA (folio, fecha, cantidad_reportada, cantidad_recibida, diferencia, motivo, usuario, registro_merma) VALUES
('DISC-2026-001', '2026-07-03', 5.00, 4.00, 1.00, 'Falta una celda física en el contenedor de traslado.', 2, 'MRM-2026-001'),
('DISC-2026-002', '2026-07-06', 12.00, 12.00, 0.00, 'Cantidades coinciden plenamente tras validación visual.', 2, 'MRM-2026-002'),
('DISC-2026-003', '2026-07-07', 2.00, 1.00, 1.00, 'Un panel se quedó retenido en la estación para análisis de ingeniería.', 2, 'MRM-2026-003'),
('DISC-2026-004', '2026-07-09', 15.00, 14.00, 1.00, 'Extravío de una Main Board durante el movimiento entre naves.', 2, 'MRM-2026-004'),
('DISC-2026-005', '2026-07-11', 50.00, 48.00, 2.00, 'Dos cajas de cartón deshechas por humedad total no se pudieron contabilizar.', 2, 'MRM-2026-005'),
('DISC-2026-006', '2026-07-12', 8.00, 8.00, 0.00, 'Conteo de tornillería dañado validado por peso en báscula.', 2, 'MRM-2026-006'),
('DISC-2026-007', '2026-07-13', 3.00, 3.00, 0.00, 'Módulos OLED recibidos completos en empaque antiestático.', 2, 'MRM-2026-007'),
('DISC-2026-008', '2026-07-14', 100.00, 95.00, 5.00, 'Diferencia por pérdida de tornillos sueltos en la rejilla del Conveyor.', 2, 'MRM-2026-008'),
('DISC-2026-009', '2026-07-15', 4.00, 4.00, 0.00, 'Láminas difusoras recibidas sin contratiempos.', 2, 'MRM-2026-009'),
('DISC-2026-010', '2026-07-16', 25.00, 22.00, 3.00, 'Cables flex mal contados por el supervisor debido a prisa en línea.', 2, 'MRM-2026-010'),
('DISC-2026-011', '2026-07-16', 6.00, 6.00, 0.00, 'Fuentes de poder quemadas recibidas e identificadas con etiqueta roja.', 2, 'MRM-2026-011'),
('DISC-2026-012', '2026-07-17', 14.00, 15.00, -1.00, 'Llegó una tira LED de más no declarada en el folio original.', 2, 'MRM-2026-012'),
('DISC-2026-013', '2026-07-18', 40.00, 40.00, 0.00, 'Módulos WiFi CKD validados correctamente en almacén secundario.', 2, 'MRM-2026-013'),
('DISC-2026-014', '2026-07-19', 10.00, 8.00, 2.00, 'Dos tarjetas retenidas en laboratorio QA para auditoría de ESD.', 2, 'MRM-2026-014'),
('DISC-2026-015', '2026-07-19', 30.00, 30.00, 0.00, 'Gabinetes plásticos recibidos en tarima física.', 2, 'MRM-2026-015'),
('DISC-2026-016', '2026-07-20', 18.00, 18.00, 0.00, 'Bocinas defectuosas ingresadas al contenedor de desecho electrónico.', 2, 'MRM-2026-016'),
('DISC-2026-017', '2026-07-20', 5.00, 4.00, 1.00, 'Una fuente se quedó en mesa de retrabajo para intento de rescate.', 2, 'MRM-2026-017'),
('DISC-2026-018', '2026-07-20', 2.00, 2.00, 0.00, 'Pedestales con rosca barrida confirmados en zona de desecho.', 2, 'MRM-2026-018'),
('DISC-2026-019', '2026-07-20', 1.00, 1.00, 0.00, 'Panel OLED dañado por herramienta recibido para trituración.', 2, 'MRM-2026-019'),
('DISC-2026-020', '2026-07-20', 10.00, 10.00, 0.00, 'Sensores IR validados en el sistema por el almacenista de turno.', 2, 'MRM-2026-020');

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO REGISTRO_DISPOSICION (folio, fecha_determinacion, fecha_ejecucion, cantidad_ejecutada, observaciones, motivo_rechazo, empresa_recicladora, peso_neto, metodo_destruccion, folio_probatorio, sale_almacen, llega_almacen, disposicion_final, usuario, registro_merma, estado_disposicion) VALUES
('DISP-2026-001', '2026-07-03', '2026-07-04', 4.00, 'Destrucción masiva de cristales de TV de 32 pulgadas en trituradora.', 'N/A', 'Reciclados Tecnológicos del Norte', 35.50, 'Trituración Mecánica', 'CERT-8812', 'ALM-SCRP', 'ALM-FIN', 'SCRAP_TOT', 3, 'MRM-2026-001', 'CERRADA'),
('DISP-2026-002', '2026-07-06', '2026-07-07', 12.00, 'Retorno autorizado de biseles de aluminio defectuosos de origen.', 'N/A', 'Logística Express Internacional', 18.20, 'Devolución Física', 'PROV-9011', 'ALM-SCRP', 'ALM-PROV', 'RTN_PROV', 3, 'MRM-2026-002', 'CERRADA'),
('DISP-2026-003', '2026-07-07', NULL, NULL, 'Retenido en espera de dictamen final sobre falla de TCON.', 'Falta reporte técnico de laboratorio', 'N/A', 0.00, 'N/A', 'PEND-001', 'ALM-SCRP', NULL, 'DISP_PEND', 3, 'MRM-2026-003', 'PROCESO'),
('DISP-2026-004', '2026-07-09', '2026-07-10', 14.00, 'Extracción y recuperación de microcomponentes lógicos.', 'N/A', 'E-Waste Solutions de México', 5.40, 'Desensamble Manual', 'REC-4421', 'ALM-SCRP', 'ALM-QA', 'REC_COMP', 3, 'MRM-2026-004', 'CERRADA'),
('DISP-2026-005', '2026-07-11', '2026-07-12', 48.00, 'Destrucción de cajas de cartón degradadas por humedad.', 'N/A', 'Cartonera y Reciclados Locales', 110.00, 'Compactado e Hidropulpeado', 'CERT-8813', 'ALM-SCRP', 'ALM-FIN', 'RECIC_PLA', 3, 'MRM-2026-005', 'CERRADA'),
('DISP-2026-006', '2026-07-12', '2026-07-12', 8.00, 'Fundición de residuos metálicos de tornillería.', 'N/A', 'Metales Industriales S.A.', 1.20, 'Fundición por Inducción', 'CERT-8814', 'ALM-SCRP', 'ALM-FIN', 'RECIC_MET', 3, 'MRM-2026-006', 'CERRADA'),
('DISP-2026-007', '2026-07-13', '2026-07-15', 3.00, 'Trituración fiscal de paneles OLED de alta gama.', 'N/A', 'Reciclados Tecnológicos del Norte', 22.00, 'Trituración Estructural', 'FIS-9921', 'ALM-SCRP', 'ALM-FIN', 'DESTR_CER', 3, 'MRM-2026-007', 'CERRADA'),
('DISP-2026-008', '2026-07-14', '2026-07-14', 95.00, 'Descarte directo de tornillos defectuosos insalvables.', 'N/A', 'Metales Industriales S.A.', 10.50, 'Fundición', 'CERT-8815', 'ALM-SCRP', 'ALM-FIN', 'SCRAP_TOT', 3, 'MRM-2026-008', 'CERRADA'),
('DISP-2026-009', '2026-07-15', NULL, NULL, 'Láminas ópticas en tránsito hacia laboratorio central.', 'N/A', 'N/A', 0.00, 'N/A', 'PEND-002', 'ALM-SCRP', 'ALM-QA', 'LAB_ANALI', 3, 'MRM-2026-009', 'PROCESO'),
('DISP-2026-010', '2026-07-16', '2026-07-17', 22.00, 'Destrucción ecológica de cables Flex LVDS con cobre.', 'N/A', 'E-Waste Solutions de México', 0.90, 'Incineración Controlada', 'CERT-8816', 'ALM-SCRP', 'ALM-FIN', 'DON_ESM', 3, 'MRM-2026-010', 'CERRADA'),
('DISP-2026-011', '2026-07-16', '2026-07-16', 6.00, 'Desecho electrónico especial de PCBs de fuentes de poder.', 'N/A', 'E-Waste Solutions de México', 4.10, 'Desmantelamiento Químico', 'CERT-8817', 'ALM-SCRP', 'ALM-FIN', 'DON_ESM', 3, 'MRM-2026-011', 'CERRADA'),
('DISP-2026-012', '2026-07-17', '2026-07-19', 15.00, 'Lote devuelto íntegro a proveedor asiático por fallas masivas.', 'N/A', 'Logística Express Internacional', 3.80, 'Devolución Física', 'PROV-9012', 'ALM-SCRP', 'ALM-PROV', 'RTN_PROV', 3, 'MRM-2026-012', 'CERRADA'),
('DISP-2026-013', '2026-07-18', NULL, NULL, 'Módulos WiFi retenidos por aclaración de números de serie.', 'N/A', 'N/A', 0.00, 'N/A', 'PEND-003', 'ALM-SCRP', NULL, 'DISP_PEND', 3, 'MRM-2026-013', 'PROCESO'),
('DISP-2026-014', '2026-07-19', '2026-07-20', 8.00, 'Destrucción de Main Boards dañadas por descarga estática.', 'N/A', 'E-Waste Solutions de México', 2.80, 'Trituración e Incineración', 'CERT-8818', 'ALM-SCRP', 'ALM-FIN', 'SCRAP_TOT', 3, 'MRM-2026-014', 'CERRADA'),
('DISP-2026-015', '2026-07-19', '2026-07-19', 30.00, 'Molido y peletizado de carcasas plásticas traseras.', 'N/A', 'Plásticos e Inyecciones del Norte', 45.00, 'Trituración y Peletizado', 'CERT-8819', 'ALM-SCRP', 'ALM-FIN', 'RECIC_PLA', 3, 'MRM-2026-015', 'CERRADA'),
('DISP-2026-016', '2026-07-20', '2026-07-20', 18.00, 'Destrucción e imantación de bocinas con conos defectuosos.', 'N/A', 'Metales Industriales S.A.', 6.20, 'Trituración Mecánica', 'CERT-8820', 'ALM-SCRP', 'ALM-FIN', 'SCRAP_TOT', 3, 'MRM-2026-016', 'CERRADA'),
('DISP-2026-017', '2026-07-20', NULL, NULL, 'Fuentes enviadas a retrabajo intensivo fuera de la línea principal.', 'N/A', 'N/A', 0.00, 'N/A', 'PEND-004', 'ALM-SCRP', 'ALM-REWRK', 'REWORK_ST', 3, 'MRM-2026-017', 'PROCESO'),
('DISP-2026-018', '2026-07-20', '2026-07-20', 2.00, 'Fundición de pedestales metálicos con roscas barridas.', 'N/A', 'Metales Industriales S.A.', 5.00, 'Fundición', 'CERT-8821', 'ALM-SCRP', 'ALM-FIN', 'RECIC_MET', 3, 'MRM-2026-018', 'CERRADA'),
('DISP-2026-019', '2026-07-20', '2026-07-20', 1.00, 'Trituración mecánica de panel OLED rayado.', 'N/A', 'Reciclados Tecnológicos del Norte', 8.50, 'Trituración Mecánica', 'CERT-8822', 'ALM-SCRP', 'ALM-FIN', 'SCRAP_TOT', 3, 'MRM-2026-019', 'CERRADA'),
('DISP-2026-020', '2026-07-20', NULL, NULL, 'Recepción en laboratorio para verificar degradación de pines.', 'N/A', 'N/A', 0.00, 'N/A', 'PEND-005', 'ALM-SCRP', 'ALM-QA', 'LAB_ANALI', 3, 'MRM-2026-020', 'PROCESO');

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO PLANTA (clave, nombre, numTel, dirCalle, dirNumero, dirColonia) VALUES
('PLT-TIJ1', 'Planta de Ensambles Tijuana Norte', '664-123-4567', 'Av. de la Producción', '1024', 'Parque Industrial Chilpancingo');

INSERT INTO AREA (codigo, nombre, descripcion, planta) VALUES
('ARE-ENS', 'Área de Ensambles Mecánicos', 'Líneas principales de flujo continuo de TV', 'PLT-TIJ1'),
('ARE-QA', 'Laboratorio de Auditoría y Calidad', 'Inspección de componentes y fallas complejas', 'PLT-TIJ1'),
('ARE-ALM', 'Almacén Central y Scrap', 'Control de inventarios CKD y material de desecho', 'PLT-TIJ1');

INSERT INTO ALMACEN (clave, nombre, ubicacion, tipo, capacidad, planta) VALUES
('ALM-MAT', 'Almacén de Materia Prima CKD', 'Nave A - Zona Sur', 'Componentes electrónicos', 50000.00, 'PLT-TIJ1'),
('ALM-SCRP', 'Almacén Temporal de Scrap', 'Nave B - Zona Este', 'Desechos y mermas', 10000.00, 'PLT-TIJ1'),
('ALM-QA', 'Almacén de Retención Calidad (Hold)', 'Laboratorio Central', 'Auditoría', 2000.00, 'PLT-TIJ1'),
('ALM-PROV', 'Zona de Devoluciones a Proveedor', 'Andén 12', 'Tránsito', 5000.00, 'PLT-TIJ1'),
('ALM-REWRK', 'Amortiguador de Retrabajos', 'Línea Posterior 2', 'Producción', 1500.00, 'PLT-TIJ1'),
('ALM-FIN', 'Destino Final Reciclaje', 'Patio Exterior E1', 'Externo', 20000.00, 'PLT-TIJ1');

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO EMPLEADO (numero, emNombre, emPrimerApell, emSegundoApell, puesto, edad, fecha_ingreso, area) VALUES
(1, 'Carlos', 'Mendoza', 'Ruiz', 'Supervisor de Línea Jr', 29, '2024-03-15', 'ARE-ENS'),
(2, 'Ana', 'Gómez', 'López', 'Encargada de Inventarios Scrap', 34, '2023-08-10', 'ARE-ALM'),
(3, 'Ricardo', 'Silva', 'Castro', 'Ingeniero de Calidad de Componentes', 41, '2021-05-22', 'ARE-QA'),
(4, 'Sofía', 'Villarreal', 'Pérez', 'Administrador General de Sistemas', 38, '2020-01-15', 'ARE-QA');

INSERT INTO USUARIO (num, contrasena, username, correo, empleado, rol) VALUES
(1, '$2b$12$K35Ym7u...', 'carlos.mendoza', 'carlos.m@mermax.com', 1, 'SUP_LINEA'),
(2, '$2b$12$P08Xz8v...', 'ana.gomez', 'ana.g@mermax.com', 2, 'ALMACEN'),
(3, '$2b$12$R88Wq2m...', 'ricardo.silva', 'ricardo.s@mermax.com', 3, 'ING_CALID'),
(4, '$2b$12$A11Zp9x...', 'sofia.villa', 'sofia.v@mermax.com', 4, 'ADMIN');

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO LINEA_PRODUCCION (num, nombre, descripcion, numero_linea, area, estado_linea) VALUES
(1, 'Línea de Ensamble 01 - Paneles Grandes', 'Especializada en pantallas de 55 a 85 pulgadas', 1, 'ARE-ENS', 'PROD_NORM'),
(2, 'Línea de Ensamble 02 - Modelos Comerciales', 'Línea de alta velocidad para pantallas de 32 a 50 pulgadas', 2, 'ARE-ENS', 'PROD_NORM'),
(3, 'Línea de Ensamble 03 - Célula Flexible Premium', 'Producción de tecnología OLED y prototipos', 3, 'ARE-ENS', 'SETUP_MOD');

INSERT INTO ESTACION_TRABAJO (codigo, nombre, etapa, linea_produccion) VALUES
('EST-01', 'Estación 01 - Desempaque de Open Cell', 'Preparación de Materiales', 1),
('EST-02', 'Estación 02 - Atornillado de Chasis Estructural', 'Ensamble Mecánico', 1),
('EST-03', 'Estación 03 - Colocación de Biseles y Marcos', 'Ensamble Estético', 1),
('EST-04', 'Estación 04 - Flasheo e Inserción Main Board', 'Ensamble Electrónico', 1),
('EST-05', 'Estación 05 - Empaque e Inspección Final Box', 'Embalaje', 1),
('EST-06', 'Estación 06 - Fijación Robot Pick & Place', 'Ensamble Automatizado', 2),
('EST-07', 'Estación 07 - Encendido y Pruebas ATS', 'Prueba Funcional', 2),
('EST-08', 'Estación 08 - Auditoría Cosmética Calidad', 'Inspección de Calidad', 2),
('EST-09', 'Estación 09 - Colocación de Difusores Ónicos', 'Sistema Óptico', 2),
('EST-10', 'Estación 10 - Ensamble Cables Flex LVDS', 'Ensamble Eléctrico', 2),
('EST-11', 'Estación 11 - Prueba Hi-Pot de Aislamiento', 'Prueba Eléctrica', 2),
('EST-12', 'Estación 12 - Montaje de Tiras LED Backlight', 'Sistema Óptico', 2),
('EST-13', 'Estación 13 - Conexión de Módulo WiFi e IR', 'Ensamble Electrónico', 2),
('EST-14', 'Estación 14 - Pruebas en Cuarto Oscuro OLED', 'Prueba Funcional', 3),
('EST-15', 'Estación 15 - Ensamble Carcasa Trasera Plástica', 'Ensamble Mecánico', 3),
('EST-16', 'Estación 16 - Inserción de Altavoces y Audio', 'Ensamble Acústico', 3),
('EST-17', 'Estación 17 - Soldadura Robótica SMD', 'Ensamble Electrónico', 3),
('EST-18', 'Estación 18 - Fijación Roscas VESA Base', 'Ensamble Mecánico', 3),
('EST-19', 'Estación 19 - Limpieza y Pulido de Polarizador', 'Acabado Estético', 3),
('EST-20', 'Estación 20 - Conexión Sensores Inteligentes', 'Ensamble Electrónico', 3);

INSERT INTO LINEA_TURNO (codigo, fecha, linea_produccion, turno) VALUES
('LT-260701A', '2026-07-01', 1, 'MAT_A'),
('LT-260701B', '2026-07-01', 1, 'VESP_B'),
('LT-260702A', '2026-07-02', 2, 'MAT_A');

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO PROVEEDOR (codigo, nombre, telefono, dirCalle, dirNumero, dirColonia, RFC) VALUES
('PRV-SAM01', 'Samsung Electronics Components Latino', '818-990-1122', 'Av. De la Innovación', '500', 'Apodaca Industrial', 'SEC950101ABC'),
('PRV-LGX02', 'LG Display Supplies Americas', '333-556-7788', 'Calzada del Cristal', '89', 'El Salto', 'LGD010320XYZ'),
('PRV-FOX03', 'Foxconn Precision Hardware México', '656-778-9900', 'Bulevar de los Circuitos', '1202', 'Ciudad Juárez Centro', 'FPH100812K78');

INSERT INTO ESTADO_LOTE (codigo, nombre) VALUES
('INSP_OK', 'Lote Aprobado en IQA'),
('CUARENT', 'Lote Retenido en Cuarentena'),
('RECHAZAD', 'Lote Rechazado por Defectos Críticos');

INSERT INTO LOTE_MATERIAL (num, fecha, cantidad, caducidad, numero_lote_prov, componente, almacen, estado_lote, proveedor) VALUES
(1, '2026-06-15', 500.00, '2027-06-15', 'LN-SAM-32-09B', 'CEL-32HD', 'ALM-MAT', 'INSP_OK', 'PRV-SAM01'),
(2, '2026-06-18', 350.00, '2027-06-18', 'LN-LG-43-11A', 'BEZ-AL55', 'ALM-MAT', 'INSP_OK', 'PRV-LGX02'),
(3, '2026-06-20', 200.00, '2027-06-20', 'LN-SAM-55-88X', 'CEL-55UHD', 'ALM-MAT', 'INSP_OK', 'PRV-SAM01'),
(4, '2026-06-22', 1000.00, NULL, 'FX-MAIN-SMA-01', 'MAIN-SM-A', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(5, '2026-06-25', 1200.00, NULL, 'BOX-CRT-55-V1', 'BOX-CRT55', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(6, '2026-06-01', 50000.00, NULL, 'TORN-M4-HEX', 'SCRW-SET', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(7, '2026-06-26', 150.00, '2027-06-26', 'LN-LG-OLED-65P', 'CEL-65OLED', 'ALM-MAT', 'INSP_OK', 'PRV-LGX02'),
(8, '2026-06-01', 45000.00, NULL, 'TORN-M3-STD', 'SCRW-SET', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(9, '2026-06-28', 800.00, '2028-06-28', 'DIF-FILM-55-A', 'DIF-FILM55', 'ALM-MAT', 'INSP_OK', 'PRV-SAM01'),
(10, '2026-06-29', 2500.00, NULL, 'FLEX-51P-V1', 'CABLE-LVDS', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(11, '2026-06-12', 600.00, '2028-06-12', 'POW-75W-XYZ', 'POW-75W', 'ALM-MAT', 'INSP_OK', 'PRV-SAM01'),
(12, '2026-06-14', 900.00, NULL, 'LED-STRIP-50-B', 'LED-BACK50', 'ALM-MAT', 'INSP_OK', 'PRV-SAM01'),
(13, '2026-06-16', 1500.00, NULL, 'WIFI-M2-G6', 'WIFI-MOD', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(14, '2026-06-19', 400.00, NULL, 'FX-MAIN-OLP-02', 'MAIN-OL-P', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(15, '2026-06-21', 700.00, NULL, 'CHAS-PL-43-B1', 'CHAS-PL43', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(16, '2026-06-23', 2000.00, NULL, 'SPK-15W-AUDIO', 'SPK-15W', 'ALM-MAT', 'INSP_OK', 'PRV-SAM01'),
(17, '2026-06-24', 500.00, '2028-06-24', 'POW-180W-ABC', 'POW-180W', 'ALM-MAT', 'INSP_OK', 'PRV-SAM01'),
(18, '2026-06-26', 1100.00, NULL, 'BASE-STAND-M', 'BASE-STND', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03'),
(19, '2026-06-27', 120.00, '2027-06-27', 'LN-LG-OLED-65P2', 'CEL-65OLED', 'ALM-MAT', 'INSP_OK', 'PRV-LGX02'),
(20, '2026-06-28', 3000.00, NULL, 'IR-RECP-V1', 'RECP-IR', 'ALM-MAT', 'INSP_OK', 'PRV-FOX03');

SET FOREIGN_KEY_CHECKS = 1;

SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO UMBRAL_ALERTA (numero, valor, activo, indicador_kpi, linea_produccion) VALUES
(1, 2.50, 1, 'KPI-SCRP-P', 1),
(2, 1200.00, 1, 'KPI-DPMO', 1),
(3, 10000.00, 1, 'KPI-SCRP-C', 1),
(4, 500.00, 1, 'KPI-TORQ-F', 2),
(5, 5.00, 1, 'KPI-ESD-IN', 2);

INSERT INTO ORDEN_PRODUCCION (numero, cantidad_inicial, cantidad_final, fecha_inicio, fecha_fin, estacion_trabajo, estado_orden) VALUES
(1, 500, 495, '2026-07-02', '2026-07-02', 'EST-01', 'TERM_COMP'),
(2, 350, 338, '2026-07-05', '2026-07-05', 'EST-02', 'TERM_COMP'),
(3, 200, NULL, '2026-07-06', NULL, 'EST-03', 'EN_PROG'),
(4, 1000, 985, '2026-07-08', '2026-07-08', 'EST-04', 'TERM_COMP'),
(5, 1200, 1150, '2026-07-10', '2026-07-10', 'EST-05', 'TERM_COMP'),
(6, 5000, 4992, '2026-07-11', '2026-07-11', 'EST-06', 'TERM_COMP'),
(7, 150, NULL, '2026-07-12', NULL, 'EST-07', 'EXC_MERMA'),
(8, 2000, 1900, '2026-07-13', '2026-07-13', 'EST-08', 'TERM_COMP'),
(9, 800, NULL, '2026-07-14', NULL, 'EST-09', 'EN_PROG'),
(10, 2500, NULL, '2026-07-15', NULL, 'EST-10', 'PAUS_QA'),
(11, 600, 594, '2026-07-15', '2026-07-15', 'EST-11', 'TERM_COMP'),
(12, 900, 886, '2026-07-16', '2026-07-16', 'EST-12', 'TERM_COMP'),
(13, 1500, NULL, '2026-07-17', NULL, 'EST-13', 'EN_PROG'),
(14, 400, NULL, '2026-07-18', NULL, 'EST-14', 'PAUS_MAQ'),
(15, 700, 670, '2026-07-18', '2026-07-18', 'EST-15', 'TERM_COMP'),
(16, 2000, 1982, '2026-07-19', '2026-07-19', 'EST-16', 'TERM_COMP'),
(17, 500, NULL, '2026-07-19', NULL, 'EST-17', 'EN_PROG'),
(18, 1100, NULL, '2026-07-20', NULL, 'EST-18', 'LANZADA'),
(19, 120, 119, '2026-07-20', '2026-07-20', 'EST-19', 'TERM_COMP'),
(20, 300, NULL, '2026-07-20', NULL, 'EST-20', 'URG_PROD');

INSERT INTO TURNO_ORDEN (clave, fecha, hora_inicio, hora_fin, cantidad_producida, turno, orden_produccion) VALUES
(1, '2026-07-02', '06:00:00', '14:00:00', 495, 'MAT_A', 1),
(2, '2026-07-05', '14:00:00', '22:00:00', 338, 'VESP_B', 2);

INSERT INTO ORDEN_PRODUCTO (orden, producto, cantidad) VALUES
(1, 'TV-LED24', 500),
(2, 'TV-LED32', 350);

INSERT INTO PROD_COMP (producto, componente, unidad, cantidad_requerida) VALUES
('TV-LED32', 'CEL-32HD', 'Pieza', 1.00),
('TV-LED32', 'MAIN-SM-A', 'Pieza', 1.00),
('TV-LED32', 'POW-75W', 'Pieza', 1.00);

SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO ESTADO_DISPOSICION (codigo, nombre) VALUES
('PROCESO', 'En Proceso de Dictamen'),
('CERRADA', 'Disposición Concluida'),
('RECHAZADA', 'Disposición Rechazada por Auditoría'),
('HECHA', 'Disposición Ejecutada y Comprobada');

-- CONSULTAS PRUEBA
-- 1. Total de merma y costo acumulado por componente
-- Esta consulta permite identificar cuáles componentes están generando mayor impacto económico debido a mermas, ayudando a priorizar acciones de mejora en la línea de producción.
SELECT 
    componente,
    COUNT(*) AS total_registros,
    SUM(cantidad) AS cantidad_total_merma,
    SUM(costo_total) AS costo_total_perdido
FROM REGISTRO_MERMA
GROUP BY componente
ORDER BY costo_total_perdido DESC;

-- 2. Costo promedio de merma por tipo de componente
-- Esta consulta ayuda a determinar el costo promedio de merma por evento para cada componente, lo que es útil para análisis de eficiencia y control de calidad.
SELECT 
    componente,
    AVG(cantidad) AS promedio_cantidad_por_evento,
    AVG(costo_total) AS costo_promedio_por_evento
FROM REGISTRO_MERMA
GROUP BY componente
ORDER BY costo_promedio_por_evento DESC;

-- 3. Eficiencia de estaciones de trabajo
-- Esta consulta permite evaluar qué estaciones de trabajo están generando más mermas y costos asociados, lo que puede indicar problemas en procesos específicos o necesidad de capacitación adicional.
SELECT 
    estacion_trabajo,
    COUNT(*) AS incidentes,
    SUM(costo_total) AS costo_acumulado
FROM REGISTRO_MERMA
GROUP BY estacion_trabajo
ORDER BY costo_acumulado DESC;

-- 4. Rastreo completo: De la Merma a la Inspección
-- Esta consulta permite rastrear cada registro de merma y su correspondiente solicitud de inspección, proporcionando un panorama completo del flujo de control de calidad y seguimiento de mermas.
SELECT 
    m.folio AS folio_merma,
    m.componente,
    m.cantidad,
    m.edo_flujo_merma AS estado_merma,
    s.codigo AS codigo_inspeccion,
    s.edo_solicitud AS estado_inspeccion,
    s.fecha_generacion
FROM REGISTRO_MERMA m
INNER JOIN SOLICITUD_INSPECCION s ON m.folio = s.registro_merma;

-- 5. Componentes mermados que pertenecen a un proveedor específico
-- Asumiendo que los lotes de material ligan el componente con su origen, esta consulta ayuda a ver el impacto de las mermas según el lote de procedencia.
SELECT 
    lm.num AS numero_lote,
    lm.componente,
    c.descripcion AS nombre_componente,
    SUM(rm.cantidad) AS cantidad_mermada
FROM REGISTRO_MERMA rm
INNER JOIN LOTE_MATERIAL lm ON rm.lote_material = lm.num AND rm.componente = lm.componente
INNER JOIN COMPONENTE c ON rm.componente = c.codigo
GROUP BY lm.num, lm.componente, c.descripcion
ORDER BY cantidad_mermada DESC;

-- TRIGGERS

/* ==========================================================================
   TRIGGER 1: tg_validar_y_costear_merma
   Objetivo: Validar consistencia, evitar inserciones incorrectas y costear.
   ========================================================================== */

DELIMITER $$

CREATE OR REPLACE TRIGGER tg_validar_y_costear_merma
BEFORE INSERT ON REGISTRO_MERMA
FOR EACH ROW
BEGIN
    DECLARE costo_unitario DECIMAL(10,2);
    DECLARE existe_comp_lote INT;
    DECLARE existe_estacion_orden INT;

    -- 1. Validar que la cantidad sea mayor a cero[cite: 4]
    IF NEW.cantidad <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: La cantidad de merma debe ser mayor a cero.';
    END IF;

    -- 2. Verificar que el componente pertenezca al lote de material indicado[cite: 4]
    SELECT COUNT(*) INTO existe_comp_lote
    FROM LOTE_MATERIAL
    WHERE num = NEW.lote_material AND componente = NEW.componente;

    IF existe_comp_lote = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: El componente no corresponde al lote de material referenciado.';
    END IF;

    -- 3. Verificar que la estación de trabajo corresponda a la orden de producción[cite: 4]
    SELECT COUNT(*) INTO existe_estacion_orden
    FROM ORDEN_PRODUCCION
    WHERE numero = NEW.orden_produccion AND estacion_trabajo = NEW.estacion_trabajo;

    IF existe_estacion_orden = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: La estación de trabajo no coincide con la orden de producción seleccionada.';
    END IF;

    -- 4. Consultar costo unitario y calcular el costo total automáticamente[cite: 4]
    SELECT costo INTO costo_unitario
    FROM COMPONENTE
    WHERE codigo = NEW.componente;

    SET NEW.costo_total = NEW.cantidad * IFNULL(costo_unitario, 0.00);
    
END $$

DELIMITER ;


/* ==========================================================================
   TRIGGER 2: tg_generar_solicitud_inspeccion
   Objetivo: Crear solicitud de inspección al cambiar el estado a "Recibido".
   ========================================================================== */

DELIMITER $$

CREATE OR REPLACE TRIGGER tg_generar_solicitud_inspeccion
AFTER UPDATE ON REGISTRO_MERMA
FOR EACH ROW
BEGIN
    DECLARE existe_discrepancia INT;
    DECLARE nuevo_codigo_solicitud VARCHAR(20);

    -- 1. Verificar si el estado cambió a "Recibido en Almacén"[cite: 4, 5]
    IF NEW.edo_flujo_merma = 'RECIB_SCRP' AND OLD.edo_flujo_merma <> 'RECIB_SCRP' THEN
        
        -- 2. Capa de control: Verificar si tiene discrepancias abiertas[cite: 4]
        SELECT COUNT(*) INTO existe_discrepancia
        FROM DISCREPANCIA
        WHERE registro_merma = NEW.folio;

        -- 3. Si no hay discrepancias, generar la solicitud automáticamente[cite: 4]
        IF existe_discrepancia = 0 THEN
            SET nuevo_codigo_solicitud = CONCAT('SOL-', NEW.folio);

            INSERT INTO SOLICITUD_INSPECCION (
                codigo, fecha_generacion, hora_generacion, edo_solicitud, registro_merma, usuario
            ) VALUES (
                nuevo_codigo_solicitud,
                CURDATE(),
                CURTIME(),
                'NUEVA', -- Estado inicial por defecto[cite: 5]
                NEW.folio,
                NEW.usuario
            );
        END IF;
    END IF;
END $$

DELIMITER ;

/* ==========================================================================
   TRIGGER 3: tg_validar_y_bloquear_discrepancia
   Objetivo: Validar datos de entrada, calcular diferencia y cambiar flujo.
   ========================================================================== */

DELIMITER $$

CREATE OR REPLACE TRIGGER tg_validar_y_bloquear_discrepancia
BEFORE INSERT ON DISCREPANCIA
FOR EACH ROW
BEGIN
    DECLARE cantidad_original DECIMAL(10,2);

    -- 1. Obtener la cantidad original declarada por el Supervisor[cite: 4]
    SELECT cantidad INTO cantidad_original
    FROM REGISTRO_MERMA
    WHERE folio = NEW.registro_merma;

    -- 2. Validar que la cantidad reportada coincida con el registro de origen[cite: 4]
    IF NEW.cantidad_reportada <> cantidad_original THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: La cantidad reportada no coincide con el registro original de la merma.';
    END IF;

    -- 3. Recalcular la diferencia de forma segura en el backend[cite: 4]
    SET NEW.diferencia = NEW.cantidad_reportada - NEW.cantidad_recibida;

    -- 4. Actualizar el estado de REGISTRO_MERMA a "En Discrepancia"[cite: 4, 5]
    UPDATE REGISTRO_MERMA
    SET edo_flujo_merma = 'DISC_CANT'
    WHERE folio = NEW.registro_merma;

END $$

DELIMITER ;