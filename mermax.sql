DROP DATABASE IF EXISTS mermax_db;
CREATE DATABASE mermax_db
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

CREATE TABLE EDO_DISCREPANCIA (
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (codigo)
);

CREATE TABLE INDICADOR_KPI (
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(150),
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
    correo VARCHAR(100),
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
    fecha_nacimiento DATE,
    fecha_ingreso DATE,
    area VARCHAR(10) NOT NULL,
    turno VARCHAR(10),
    PRIMARY KEY (numero),
    CONSTRAINT fk_empleado_area FOREIGN KEY (area) REFERENCES AREA(codigo),
    CONSTRAINT fk_empleado_turno FOREIGN KEY (turno) REFERENCES TURNO(clave)
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
    indicador_kpi VARCHAR(20) NOT NULL,
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
    fecha_reporte DATE NOT NULL,
    cantidad_reportada DECIMAL(10,2) NOT NULL,
    cantidad_recibida DECIMAL(10,2) NOT NULL,
    diferencia DECIMAL(10,2) NOT NULL,
    motivo_reporte VARCHAR(100),
    usuario_reporte INT NOT NULL,
    registro_merma VARCHAR(20),
    edo_discrepancia VARCHAR(10) NOT NULL DEFAULT 'ABIERTA',
    fecha_resolucion DATE,
    motivo_resolucion VARCHAR(100),
    usuario_resolucion INT,
    PRIMARY KEY (folio),
    CONSTRAINT fk_discrepancia_usuario_reporte FOREIGN KEY (usuario_reporte) REFERENCES USUARIO(num),
    CONSTRAINT fk_discrepancia_usuario_resolucion FOREIGN KEY (usuario_resolucion) REFERENCES USUARIO(num),
    CONSTRAINT fk_discrepancia_edo FOREIGN KEY (edo_discrepancia) REFERENCES EDO_DISCREPANCIA(codigo),
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
('ACTIVA', 'Activa'),
('INACTIVA', 'Inactiva'),
('MANTTO', 'En Mantenimiento');

INSERT INTO TURNO (clave, nombre, hora_inicio, hora_fin) VALUES
('MAT', 'Matutino', '07:00:00', '19:00:00'),
('NOC', 'Nocturno', '19:00:00', '07:00:00');

INSERT INTO ESTADO_ORDEN (codigo, nombre) VALUES
('PENDIENTE', 'Pendiente'),
('PROCESO', 'En Proceso'),
('COMPLETA', 'Completada'),
('CANCELADA', 'Cancelada');

INSERT INTO PRODUCTO (codigo, modelo, nombre, descripcion, pulgadas) VALUES
('PROD-01', 'TLX-55Q', 'Televisor 4K Smart TV 55"', 'Televisor 4K con panel LED de 55 pulgadas', 55.00);

INSERT INTO COMPONENTE (codigo, nombre, costo, descripcion, tipo) VALUES
('COMP-01', 'Tarjeta Principal (Mainboard)', 850.00, 'Tarjeta de control principal del televisor', 'Electrónico'),
('COMP-02', 'Fuente de Poder', 320.00, 'Fuente de alimentación del televisor', 'Electrónico'),
('COMP-03', 'Panel LED 55"', 4200.00, 'Panel de despliegue 4K de 55 pulgadas', 'Panel'),
('COMP-04', 'Gabinete Trasero', 180.00, 'Cubierta plástica trasera del televisor', 'Plástico'),
('COMP-05', 'Arnés de Cableado', 95.00, 'Cableado interno de conexión entre módulos', 'Cableado');

INSERT INTO ROL (clave, nombre, descripcion) VALUES
('SUPER', 'Supervisor de Línea', 'Detecta y registra eventos de merma en piso de producción'),
('ALMAC', 'Almacenista', 'Confirma recepción física del scrap y registra discrepancias'),
('CALID', 'Ingeniero de Calidad', 'Inspecciona el scrap y emite el dictamen de disposición final'),
('ADMIN', 'Administrador', 'Gestiona catálogos, usuarios y roles del sistema');

INSERT INTO EDO_FLUJO_MERMA (codigo, nombre) VALUES
('REGISTRADA', 'Registrada'),
('DISCREPAN', 'En Discrepancia'),
('RECIBIDA', 'Recibida en Almacén'),
('INSPECCIO', 'En Inspección'),
('CERRADA', 'Cerrada');

INSERT INTO TIPO_MERMA (codigo, nombre, descripcion) VALUES
('DEF_FAB', 'Defecto de Fabricación', 'Falla detectada en el componente desde su origen'),
('DAN_MANEJO', 'Daño por Manejo', 'Daño físico ocasionado durante traslado o manipulación'),
('ERR_ENSAM', 'Error de Ensamble', 'Falla generada durante el proceso de integración en línea'),
('FALLA_COMP', 'Falla de Componente', 'Componente no funcional detectado en pruebas'),
('OTROS', 'Otros', 'Causas no clasificadas en las categorías anteriores');

INSERT INTO CAUSA_RAIZ (codigo, nombre, descripcion) VALUES
('SOLD_FRIA', 'Soldadura Fría', 'Unión eléctrica deficiente en tarjeta principal'),
('ESD', 'Descarga Electroestática', 'Daño por falta de tierra o protección ESD en estación'),
('CONTAM', 'Contaminación', 'Presencia de polvo o partículas en panel LED'),
('MANIP_INAD', 'Manipulación Inadecuada', 'Manejo incorrecto del componente por parte del operador'),
('FALTA_PROC', 'Falta de Procedimiento', 'Ausencia o incumplimiento de instrucción de trabajo'),
('FALLA_MAQ', 'Falla de Máquina', 'Desviación de parámetros en equipo automatizado');

INSERT INTO DISPOSICION_FINAL (clave, nombre, descripcion) VALUES
('RTN_PROV', 'Devolución a Proveedor', 'Retorno del material al proveedor por defecto de origen'),
('RECICLAJE', 'Reciclaje', 'Envío del material a empresa recicladora autorizada'),
('DESTR_CTRL', 'Desecho Controlado', 'Destrucción certificada del material bajo método autorizado');

INSERT INTO EDO_SOLICITUD (codigo, nombre) VALUES
('PENDIENTE', 'Pendiente'),
('ATENDIDA', 'Atendida');

INSERT INTO EDO_DISCREPANCIA (codigo, nombre) VALUES
('ABIERTA', 'Abierta'),
('RESUELTA', 'Resuelta');

INSERT INTO INDICADOR_KPI (codigo, nombre, descripcion, formula, unidad) VALUES
('PCT_SCRAP', '% de Scrap por Línea', 'Porcentaje de merma respecto a la producción total', '(cantidad_merma / cantidad_producida) * 100', '%'),
('COSTO_MERMA', 'Costo Total de Merma', 'Impacto económico acumulado del scrap en el periodo', 'SUM(costo_total)', 'USD'),
('TOP_CAUSA', 'Causa Raíz Más Frecuente', 'Conteo de eventos de merma agrupados por causa raíz', 'COUNT(registro_merma) GROUP BY causa_raiz', 'eventos');

INSERT INTO ESTADO_ALERTA (codigo, nombre) VALUES
('ACTIVA', 'Activa'),
('ATENDIDA', 'Atendida');

INSERT INTO ESTADO_LOTE (codigo, nombre) VALUES
('DISPONIBLE', 'Disponible'),
('AGOTADO', 'Agotado'),
('VENCIDO', 'Vencido');

INSERT INTO ESTADO_DISPOSICION (codigo, nombre) VALUES
('PENDIENTE', 'Pendiente'),
('PROCESO', 'En Proceso'),
('EJECUTADO', 'Ejecutado'),
('CANCELADO', 'Cancelado');

-- PLANTA, AREA, ALMACEN (deben ir antes que cualquier tabla que dependa de ellas)

INSERT INTO PLANTA (clave, nombre, numTel, dirCalle, dirNumero, dirColonia) VALUES
('PLT-TIJ', 'Telvix Electronics Tijuana', '664-555-0100', 'Av. Industria Electrónica', '4500', 'Parque Industrial El Florido');

INSERT INTO AREA (codigo, nombre, descripcion, planta) VALUES
('ARE-PROD', 'Producción', 'Área de líneas de ensamble', 'PLT-TIJ'),
('ARE-QA', 'Calidad', 'Área de inspección y aseguramiento de calidad', 'PLT-TIJ'),
('ARE-ALM', 'Almacén', 'Área de recepción y resguardo de material', 'PLT-TIJ'),
('ARE-ADM', 'Administración', 'Área administrativa de la planta', 'PLT-TIJ');

INSERT INTO ALMACEN (clave, nombre, ubicacion, tipo, capacidad, planta) VALUES
('ALM-PROD', 'Almacén de Producción', 'Nave 1, sección A', 'Origen de Lote', 5000.00, 'PLT-TIJ'),
('ALM-SCRP', 'Almacén de Scrap', 'Nave 2, sección B', 'Destino de Merma', 1500.00, 'PLT-TIJ');

-- LINEA_PRODUCCION (num es AUTO_INCREMENT, por eso no se manda ese campo)

INSERT INTO LINEA_PRODUCCION (nombre, descripcion, numero_linea, area, estado_linea) VALUES
('Preparación de Tarjeta Principal', 'Ensamble de mainboard', 10, 'ARE-PROD', 'ACTIVA'),
('Ensamble de Fuente de Poder', 'Integración de fuente de poder', 20, 'ARE-PROD', 'ACTIVA'),
('Integración de Panel LED', 'Etapa más costosa del proceso', 30, 'ARE-PROD', 'ACTIVA'),
('Ensamble de Gabinete y Arnés', 'Integración de gabinete y cableado', 40, 'ARE-PROD', 'ACTIVA'),
('Pruebas Finales y Empaque', 'Control de calidad final y empaque', 50, 'ARE-PROD', 'ACTIVA');

-- ESTACION_TRABAJO (2 por línea, linea_produccion 1-5 según el AUTO_INCREMENT de arriba)

INSERT INTO ESTACION_TRABAJO (codigo, nombre, etapa, linea_produccion) VALUES
('EST-01', 'Soldadura SMT', 'Preparación', 1),
('EST-02', 'Inspección de Tarjeta', 'Preparación', 1),
('EST-03', 'Ensamble de Fuente', 'Integración', 2),
('EST-04', 'Prueba Eléctrica de Fuente', 'Integración', 2),
('EST-05', 'Montaje de Panel LED', 'Integración', 3),
('EST-06', 'Calibración de Panel', 'Integración', 3),
('EST-07', 'Ensamble de Gabinete', 'Integración', 4),
('EST-08', 'Colocación de Arnés', 'Integración', 4),
('EST-09', 'Prueba Funcional Final', 'Pruebas', 5),
('EST-10', 'Empaque', 'Empaque', 5);

INSERT INTO LINEA_TURNO (codigo, fecha, linea_produccion, turno) VALUES
('LT-260701A', '2026-07-01', 1, 'MAT'),
('LT-260701B', '2026-07-01', 1, 'NOC'),
('LT-260702A', '2026-07-02', 2, 'MAT');

INSERT INTO PROVEEDOR (codigo, nombre, correo, telefono, dirCalle, dirNumero, dirColonia, RFC) VALUES
('PRV-LGX02', 'LG Display de México', 'ventas@lgdisplay.mx', '664-201-8800', 'Blvd. Industrial', '2200', 'Otay', 'LGD920115AB3'),
('PRV-FOX01', 'Foxconn Baja California', 'compras@foxconn.mx', '664-330-1200', 'Av. Manufactura', '1100', 'El Florido', 'FOX880210KL9'),
('PRV-SAM03', 'Samsung Electro-Mechanics', 'contacto@sem.com.mx', '656-441-5500', 'Parque Tecnológico', '300', 'Ciudad Juárez Industrial', 'SEM750619MN2');

-- LOTE_MATERIAL (num es AUTO_INCREMENT, quedan como 1,2,3... en ese orden)

INSERT INTO LOTE_MATERIAL (fecha, cantidad, caducidad, numero_lote_prov, componente, almacen, estado_lote, proveedor) VALUES
('2026-06-15', 500.00, NULL, 'LGX-MAIN-01', 'COMP-01', 'ALM-PROD', 'DISPONIBLE', 'PRV-LGX02'),
('2026-06-18', 350.00, NULL, 'FOX-FUENTE-02', 'COMP-02', 'ALM-PROD', 'DISPONIBLE', 'PRV-FOX01'),
('2026-06-20', 200.00, '2027-06-20', 'SAM-PANEL-03', 'COMP-03', 'ALM-PROD', 'DISPONIBLE', 'PRV-SAM03'),
('2026-06-22', 1000.00, NULL, 'FOX-GAB-04', 'COMP-04', 'ALM-PROD', 'DISPONIBLE', 'PRV-FOX01'),
('2026-06-25', 1200.00, NULL, 'LGX-ARNES-05', 'COMP-05', 'ALM-PROD', 'DISPONIBLE', 'PRV-LGX02');

-- RF-15: cada linea de produccion lleva configurado su maximo de scrap.
-- La linea 3 (Panel LED) tolera mas porque es la etapa mas costosa y delicada.
-- La linea 2 lleva ademas un umbral de costo, para ejercitar los dos KPIs.
INSERT INTO UMBRAL_ALERTA (valor, activo, indicador_kpi, linea_produccion) VALUES
(2.50, TRUE, 'PCT_SCRAP', 1),
(2.50, TRUE, 'PCT_SCRAP', 2),
(3.00, TRUE, 'PCT_SCRAP', 3),
(2.50, TRUE, 'PCT_SCRAP', 4),
(2.50, TRUE, 'PCT_SCRAP', 5),
(30000.00, TRUE, 'COSTO_MERMA', 2);

-- ORDEN_PRODUCCION (numero es AUTO_INCREMENT, quedan 1..10)
-- Una orden por cada estacion de trabajo. Es requisito del Trigger 1:
-- rechaza cualquier merma cuya estacion no coincida con su orden, asi que
-- sin una orden por estacion no se pueden registrar mermas en toda la planta.
--   Orden 1  -> EST-01   Orden 6  -> EST-06
--   Orden 2  -> EST-03   Orden 7  -> EST-07
--   Orden 3  -> EST-05   Orden 8  -> EST-08
--   Orden 4  -> EST-02   Orden 9  -> EST-09
--   Orden 5  -> EST-04   Orden 10 -> EST-10

-- Volumen de un trimestre de operacion. Es el denominador del KPI de scrap:
-- con lotes de 200-500 piezas el porcentaje de merma sale en 30%, absurdo para
-- una planta real (lo normal es 1-3%) y deja las 5 lineas en alerta permanente.
INSERT INTO ORDEN_PRODUCCION (cantidad_inicial, cantidad_final, fecha_inicio, fecha_fin, estacion_trabajo, estado_orden) VALUES
(2000, 1985, '2026-05-04', '2026-06-12', 'EST-01', 'COMPLETA'),
(2000, 1990, '2026-05-04', '2026-06-12', 'EST-03', 'COMPLETA'),
(2000, 1960, '2026-05-04', '2026-06-12', 'EST-05', 'COMPLETA'),
(2000, 1978, '2026-05-04', '2026-06-12', 'EST-02', 'COMPLETA'),
(2000, 1982, '2026-05-04', '2026-06-12', 'EST-04', 'COMPLETA'),
(2000, 1955, '2026-05-04', '2026-06-12', 'EST-06', 'COMPLETA'),
(2000, 1988, '2026-06-15', '2026-07-24', 'EST-07', 'COMPLETA'),
(2000, 1986, '2026-06-15', '2026-07-24', 'EST-08', 'COMPLETA'),
(2000, NULL, '2026-06-15', NULL, 'EST-09', 'PROCESO'),
(2000, NULL, '2026-06-15', NULL, 'EST-10', 'PROCESO');

-- Produccion por turno. Es el denominador del KPI PCT_SCRAP:
-- % de scrap = cantidad mermada / cantidad_producida
INSERT INTO TURNO_ORDEN (clave, fecha, hora_inicio, hora_fin, cantidad_producida, turno, orden_produccion) VALUES
('TO-001', '2026-06-12', '07:00:00', '19:00:00', 1985, 'MAT', 1),
('TO-002', '2026-06-12', '19:00:00', '07:00:00', 1990, 'NOC', 2),
('TO-003', '2026-06-12', '07:00:00', '19:00:00', 1960, 'MAT', 3),
('TO-004', '2026-06-12', '07:00:00', '19:00:00', 1978, 'MAT', 4),
('TO-005', '2026-06-12', '19:00:00', '07:00:00', 1982, 'NOC', 5),
('TO-006', '2026-06-12', '07:00:00', '19:00:00', 1955, 'MAT', 6),
('TO-007', '2026-07-24', '07:00:00', '19:00:00', 1988, 'MAT', 7),
('TO-008', '2026-07-24', '19:00:00', '07:00:00', 1986, 'NOC', 8),
('TO-009', '2026-07-24', '07:00:00', '19:00:00', 1940, 'MAT', 9),
('TO-010', '2026-07-24', '19:00:00', '07:00:00', 1935, 'NOC', 10);

INSERT INTO ORDEN_PRODUCTO (orden, producto, cantidad) VALUES
(1, 'PROD-01', 2000),
(2, 'PROD-01', 2000),
(3, 'PROD-01', 2000),
(4, 'PROD-01', 2000),
(5, 'PROD-01', 2000),
(6, 'PROD-01', 2000),
(7, 'PROD-01', 2000),
(8, 'PROD-01', 2000),
(9, 'PROD-01', 2000),
(10, 'PROD-01', 2000);

INSERT INTO PROD_COMP (producto, componente, unidad, cantidad_requerida) VALUES
('PROD-01', 'COMP-01', 'Pieza', 1.00),
('PROD-01', 'COMP-02', 'Pieza', 1.00),
('PROD-01', 'COMP-03', 'Pieza', 1.00),
('PROD-01', 'COMP-04', 'Pieza', 1.00),
('PROD-01', 'COMP-05', 'Pieza', 1.00);

-- EMPLEADO y USUARIO del equipo (los 4 integrantes como usuarios de prueba)

INSERT INTO EMPLEADO (emNombre, emPrimerApell, emSegundoApell, fecha_nacimiento, fecha_ingreso, area, turno) VALUES
('Axel', 'Islas', 'Ruelas', '1996-03-12', '2026-01-15', 'ARE-ALM', 'MAT'),
('Anwar', 'Estrada', 'Santos', '1995-11-04', '2026-01-15', 'ARE-ADM', 'MAT'),
('Jorge', 'Martinez', 'Zambrano', '1996-07-21', '2026-01-15', 'ARE-PROD', 'MAT'),
('Diego', 'Sanchez', 'Hernandez', '1997-02-09', '2026-01-15', 'ARE-QA', 'NOC'),
('Marisol', 'Aguirre', 'Trejo', '1994-08-30', '2026-02-02', 'ARE-PROD', 'NOC'),
('Ramon', 'Quintero', 'Bejarano', '1993-05-17', '2026-02-02', 'ARE-ALM', 'NOC');

-- Contraseñas hasheadas con PBKDF2-SHA256 de Django 4.2. Los 6 usuarios: 123
INSERT INTO USUARIO (contrasena, username, correo, empleado, rol) VALUES
('pbkdf2_sha256$600000$NJ8VRTRgu9Ph$j27xRKYr4Yxcc4qIqXHxXQTxY4BA2hVuGouw4W5OnjE=', 'axel', 'axel@mermax.com', 1, 'ALMAC'),
('pbkdf2_sha256$600000$IBOf69JCDXTX$An+iXBhMEmIwwVTY/5wLj6iQJ7BLiIBhtS/gXNByyyU=', 'anwar', 'anwar@mermax.com', 2, 'ADMIN'),
('pbkdf2_sha256$600000$kH6f9zScdSOF$OBQ8QrXhq53ULqGn9Q8HQQFU0EpJ0dHJjbTM0yrvGZk=', 'jorge', 'jorge@mermax.com', 3, 'SUPER'),
('pbkdf2_sha256$600000$i42rnKDGVSaw$XuXopO3zFpiXmOWUSCzfXfzwUzEtSct+Uf6xHSuR03s=', 'diego', 'diego@mermax.com', 4, 'CALID'),
('pbkdf2_sha256$600000$meuTFeyuDF1I$gPoiY8vC0Tk7pu7xeCpacLrEss51iR8hPYVS5/HiIF4=', 'marisol', 'marisol@mermax.com', 5, 'SUPER'),
('pbkdf2_sha256$600000$ILqd4BSYDnmu$inOSUhqdhZ1FISPXTILxVdguNQ4ubFvrNUSqClDPHXU=', 'ramon', 'ramon@mermax.com', 6, 'ALMAC');

-- Usuarios: 1=axel/ALMAC/MAT, 2=anwar/ADMIN/MAT, 3=jorge/SUPER/MAT,
-- 4=diego/CALID/NOC, 5=marisol/SUPER/NOC, 6=ramon/ALMAC/NOC
-- Nota: jorge (SUPER) es quien normalmente registra la merma
--   MRM-2026-001: CERRADA    - ciclo completo, sin discrepancia
--   MRM-2026-002: REGISTRADA - limpio, sirve para probar el Trigger 2
--   MRM-2026-003: RECIBIDA   - limpio, ya recibido en almacén
--   MRM-2026-004: DISCREPAN  - bloqueado por discrepancia

INSERT INTO REGISTRO_MERMA (folio, cantidad, costo_total, fecha, unidad, descripcion, edo_flujo_merma, usuario, lote_material, componente, tipo_merma, causa_raiz, estacion_trabajo, orden_produccion) VALUES
('MRM-2026-001', 5.00, 21000.00, '2026-07-02', 'Pieza', 'Paneles LED con líneas verticales detectadas en inspección.', 'CERRADA', 3, 3, 'COMP-03', 'DEF_FAB', 'CONTAM', 'EST-05', 3),
('MRM-2026-002', 3.00,  2550.00, '2026-07-05', 'Pieza', 'Tarjetas principales con soldadura fría en pruebas eléctricas.', 'REGISTRADA', 3, 1, 'COMP-01', 'ERR_ENSAM', 'SOLD_FRIA', 'EST-01', 1),
('MRM-2026-003', 8.00,  2560.00, '2026-07-06', 'Pieza', 'Fuentes de poder dañadas por descarga electroestática.', 'RECIBIDA', 3, 2, 'COMP-02', 'DAN_MANEJO', 'ESD', 'EST-03', 2),
('MRM-2026-004', 2.00,   640.00, '2026-07-07', 'Pieza', 'Fuentes de poder con carcasa fracturada por manejo en traslado.', 'DISCREPAN', 3, 2, 'COMP-02', 'DAN_MANEJO', 'MANIP_INAD', 'EST-03', 2);

-- La discrepancia cuelga de MRM-2026-004, que es el folio que queda bloqueado.
-- cantidad_reportada debe coincidir con REGISTRO_MERMA.cantidad (regla del Trigger 3).
INSERT INTO DISCREPANCIA (folio, fecha_reporte, cantidad_reportada, cantidad_recibida, diferencia, motivo_reporte, usuario_reporte, registro_merma, edo_discrepancia) VALUES
('DISC-2026-001', '2026-07-07', 2.00, 1.00, -1.00, 'Sólo se recibió una pieza de las dos reportadas por la línea.', 1, 'MRM-2026-004', 'ABIERTA');

-- Toda merma que llega a RECIBIDA tiene solicitud: es lo que hace el Trigger 2.
-- MRM-2026-001 ya cerro su ciclo (solicitud ATENDIDA); MRM-2026-003 apenas se
-- recibio, asi que su solicitud sigue PENDIENTE.
-- MRM-2026-002 no tiene: sigue en REGISTRADA, nunca llego al almacen.
-- MRM-2026-004 no tiene: esta bloqueada por discrepancia (Trigger 3).
INSERT INTO SOLICITUD_INSPECCION (codigo, fecha_generacion, hora_generacion, fecha_atencion, hora_atencion, edo_solicitud, registro_merma, usuario) VALUES
('SOL-2026-001', '2026-07-02', '08:30:00', '2026-07-02', '14:15:00', 'ATENDIDA', 'MRM-2026-001', 4),
('SOL-2026-002', '2026-07-06', '10:05:00', NULL, NULL, 'PENDIENTE', 'MRM-2026-003', 4);

INSERT INTO REGISTRO_DISPOSICION (folio, fecha_determinacion, fecha_ejecucion, cantidad_ejecutada, observaciones, sale_almacen, llega_almacen, disposicion_final, usuario, registro_merma, estado_disposicion) VALUES
('DISP-2026-001', '2026-07-02', '2026-07-03', 5.00, 'Panel LED enviado a reciclaje por daño irreparable en cristal líquido.', 'ALM-SCRP', 'ALM-SCRP', 'RECICLAJE', 4, 'MRM-2026-001', 'EJECUTADO');

-- TRIGGERS

/* ==========================================================================
   TRIGGER 1: tg_validar_y_costear_merma
   Objetivo: Validar consistencia, evitar inserciones incorrectas y costear.
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_validar_y_costear_merma;

DELIMITER $$

CREATE TRIGGER tg_validar_y_costear_merma
BEFORE INSERT ON REGISTRO_MERMA
FOR EACH ROW
BEGIN
    DECLARE costo_unitario DECIMAL(10,2);
    DECLARE existe_comp_lote INT;
    DECLARE existe_estacion_orden INT;

    -- 1. Validar que la cantidad sea mayor a cero
    IF NEW.cantidad <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: La cantidad de merma debe ser mayor a cero.';
    END IF;

    -- 2. Verificar que el componente pertenezca al lote de material indicado
    SELECT COUNT(*) INTO existe_comp_lote
    FROM LOTE_MATERIAL
    WHERE num = NEW.lote_material AND componente = NEW.componente;

    IF existe_comp_lote = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: El componente no corresponde al lote de material referenciado.';
    END IF;

    -- 3. Verificar que la estación de trabajo corresponda a la orden de producción
    SELECT COUNT(*) INTO existe_estacion_orden
    FROM ORDEN_PRODUCCION
    WHERE numero = NEW.orden_produccion AND estacion_trabajo = NEW.estacion_trabajo;

    IF existe_estacion_orden = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: La estación de trabajo no coincide con la orden de producción seleccionada.';
    END IF;

    -- 4. Consultar costo unitario y calcular el costo total automáticamente
    SELECT costo INTO costo_unitario
    FROM COMPONENTE
    WHERE codigo = NEW.componente;

    SET NEW.costo_total = NEW.cantidad * IFNULL(costo_unitario, 0.00);

END $$

DELIMITER ;


/* ==========================================================================
   TRIGGER 2: tg_generar_solicitud_inspeccion
   Objetivo: Crear solicitud de inspección al cambiar el estado a "Recibida".
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_generar_solicitud_inspeccion;

DELIMITER $$

CREATE TRIGGER tg_generar_solicitud_inspeccion
AFTER UPDATE ON REGISTRO_MERMA
FOR EACH ROW
BEGIN
    DECLARE existe_discrepancia INT;
    DECLARE nuevo_codigo_solicitud VARCHAR(20);

    -- 1. Verificar si el estado cambió a "Recibida en Almacén"
    IF NEW.edo_flujo_merma = 'RECIBIDA' AND OLD.edo_flujo_merma <> 'RECIBIDA' THEN

        -- 2. Verificar si tiene discrepancias abiertas
        SELECT COUNT(*) INTO existe_discrepancia
        FROM DISCREPANCIA
        WHERE registro_merma = NEW.folio
          AND edo_discrepancia <> 'RESUELTA';

        -- 3. Si no hay discrepancias, generar la solicitud automáticamente
        IF existe_discrepancia = 0 THEN
            SET nuevo_codigo_solicitud = CONCAT('SOL-', NEW.folio);

            INSERT INTO SOLICITUD_INSPECCION (
                codigo, fecha_generacion, hora_generacion, edo_solicitud, registro_merma, usuario
            ) VALUES (
                nuevo_codigo_solicitud,
                CURDATE(),
                CURTIME(),
                'PENDIENTE',
                NEW.folio,
                NEW.usuario
            );
        END IF;
    END IF;
END $$

DELIMITER ;

-- ======================================================
-- Tablas satélite de disposición final (Axel, 21/07/2026)
-- ======================================================

-- RF-08: Devolución a proveedor
CREATE TABLE disposicion_devolucion (
    folio VARCHAR(20) PRIMARY KEY,
    motivo_rechazo VARCHAR(255) NOT NULL,
    registro_disposicion VARCHAR(20) NOT NULL UNIQUE,
    proveedor VARCHAR(10) NOT NULL,
    CONSTRAINT fk_devolucion_registro FOREIGN KEY (registro_disposicion) REFERENCES REGISTRO_DISPOSICION(folio),
    CONSTRAINT fk_devolucion_proveedor FOREIGN KEY (proveedor) REFERENCES PROVEEDOR(codigo)
);

-- RF-09: Reciclaje
CREATE TABLE EMPRESA_RECICLADORA (
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE DISPOSICION_RECICLAJE (
    folio VARCHAR(20) PRIMARY KEY,
    empresa_recicladora VARCHAR(10) NOT NULL,
    peso_neto DECIMAL(10,2) NOT NULL,
    registro_disposicion VARCHAR(20) NOT NULL UNIQUE,
    CONSTRAINT fk_reciclaje_registro FOREIGN KEY (registro_disposicion) REFERENCES REGISTRO_DISPOSICION(folio),
    CONSTRAINT fk_reciclaje_empresa FOREIGN KEY (empresa_recicladora) REFERENCES EMPRESA_RECICLADORA(codigo)
);

-- RF-10: Desecho controlado
CREATE TABLE METODO_DESTRUCCION (
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE DISPOSICION_DESECHO (
    folio VARCHAR(20) PRIMARY KEY,
    metodo_destruccion VARCHAR(10) NOT NULL,
    folio_probatorio VARCHAR(20) NOT NULL,
    registro_disposicion VARCHAR(20) NOT NULL UNIQUE,
    CONSTRAINT fk_desecho_registro FOREIGN KEY (registro_disposicion) REFERENCES REGISTRO_DISPOSICION(folio),
    CONSTRAINT fk_desecho_metodo FOREIGN KEY (metodo_destruccion) REFERENCES METODO_DESTRUCCION(codigo)
);

-- Columnas de estado (activo/inactivo) para baja lógica, según RF correspondientes
ALTER TABLE COMPONENTE ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE PROVEEDOR ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE ESTACION_TRABAJO ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE EMPLEADO ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE CAUSA_RAIZ ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE TIPO_MERMA ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE USUARIO ADD COLUMN activo BOOLEAN NOT NULL DEFAULT TRUE;

-- Bitácora de auditoría (tabla física en código, NO representada en DER/MR - decisión de equipo)
CREATE TABLE BITACORA_AUDITORIA (
    num INT AUTO_INCREMENT PRIMARY KEY,
    usuario INT NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(20) NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    motivo VARCHAR(255),
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bitacora_auditoria_usuario FOREIGN KEY (usuario) REFERENCES USUARIO(num)
);

-- Datos de catálogo para las tablas satélite

INSERT INTO EMPRESA_RECICLADORA (codigo, nombre, telefono, correo, activo) VALUES
('REC-01', 'Reciclados Tecnológicos del Norte', '664-201-3344', 'contacto@rectecnorte.com', TRUE),
('REC-02', 'Metales Industriales S.A.', '656-402-1188', 'ventas@metalesind.com', TRUE);

INSERT INTO METODO_DESTRUCCION (codigo, nombre, descripcion, activo) VALUES
('MET-01', 'Trituración Mecánica', 'Reducción física del material mediante trituradora industrial', TRUE),
('MET-02', 'Incineración Controlada', 'Destrucción térmica bajo condiciones ambientales autorizadas', TRUE);

-- Ejemplo del RF-09 (Reciclaje) sobre el registro de disposición ya insertado
INSERT INTO DISPOSICION_RECICLAJE (folio, empresa_recicladora, peso_neto, registro_disposicion) VALUES
('RCJ-2026-001', 'REC-01', 4.20, 'DISP-2026-001');

-- Ejemplo de bitácora (registro manual de prueba; en el sistema real se llenará por logging de Django)
INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora) VALUES
(4, 'REGISTRO_DISPOSICION', 'INSERT', NULL, 'DISP-2026-001 creado con disposicion_final=RECICLAJE', 'Alta de disposición por reciclaje de panel LED', '2026-07-02 09:15:00');

-- ======================================================
-- Trigger de folio y fecha automáticos (Jona, 23/07/2026)
-- ======================================================

DROP TRIGGER IF EXISTS tg_generar_folio_merma;

DELIMITER $$

CREATE TRIGGER tg_generar_folio_merma
BEFORE INSERT ON registro_merma
FOR EACH ROW
BEGIN
    DECLARE ultimo INT DEFAULT 0;

    IF NEW.fecha IS NULL THEN
        SET NEW.fecha = CURDATE();
    END IF;

    IF NEW.folio IS NULL OR NEW.folio = '' THEN

        SELECT IFNULL(
            MAX(CAST(SUBSTRING(folio,10) AS UNSIGNED)),
            0
        )
        INTO ultimo
        FROM registro_merma
        WHERE folio LIKE CONCAT('MRM-',YEAR(CURDATE()),'-%');

        SET NEW.folio = CONCAT(
            'MRM-',
            YEAR(CURDATE()),
            '-',
            LPAD(ultimo+1,3,'0')
        );

    END IF;

END$$

DELIMITER ;


/* ==========================================================================
   TRIGGER 4: tg_actualizar_costo_merma
   Objetivo: Recalcular el costo total sólo cuando cambia la base del cálculo,
   y bloquear la edición del registro una vez recibido en almacén (RF-03).
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_actualizar_costo_merma;

DELIMITER $$

CREATE TRIGGER tg_actualizar_costo_merma
BEFORE UPDATE ON REGISTRO_MERMA
FOR EACH ROW
BEGIN
    DECLARE costo_unitario DECIMAL(10,2);

    -- RF-03: sólo se puede corregir mientras el almacenista no registre la
    -- recepción. Los cambios de estado sí se permiten: hacen avanzar el flujo.
    IF OLD.edo_flujo_merma <> 'REGISTRADA'
       AND ( NEW.cantidad <> OLD.cantidad
             OR NOT (NEW.componente <=> OLD.componente)
             OR NOT (NEW.tipo_merma <=> OLD.tipo_merma)
             OR NOT (NEW.causa_raiz <=> OLD.causa_raiz) ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: el registro ya fue recibido en almacen y no puede modificarse.';
    END IF;

    -- Recostear sólo si cambió la cantidad o el componente. Si se recalculara
    -- en cada UPDATE, un cambio de estado reescribiría el costo histórico con
    -- el precio actual del componente.
    IF NEW.cantidad <> OLD.cantidad OR NOT (NEW.componente <=> OLD.componente) THEN

        IF NEW.cantidad <= 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error: La cantidad de merma debe ser mayor a cero.';
        END IF;

        SELECT costo INTO costo_unitario
        FROM COMPONENTE
        WHERE codigo = NEW.componente;

        SET NEW.costo_total = NEW.cantidad * IFNULL(costo_unitario, 0.00);

    END IF;

END$$

DELIMITER ;


DELIMITER ;

/* ==========================================================================
   TRIGGER UNIFICADO: tg_validar_y_bloquear_discrepancia
   Objetivo: 
     1. Validar que la merma esté en estado 'REGISTRADA'.
     2. Validar cantidad reportada contra la merma original.
     3. Generar folio automático (DISC-YYYY-XXX).
     4. Asignar fecha de reporte si viene nula.
     5. Calcular la diferencia (recibida - reportada).
     6. Actualizar el estado del registro de merma a 'DISCREPAN'.
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_validar_y_bloquear_discrepancia;

DELIMITER $$

CREATE TRIGGER tg_validar_y_bloquear_discrepancia
BEFORE INSERT ON DISCREPANCIA
FOR EACH ROW
BEGIN
    DECLARE cantidad_original DECIMAL(10,2);
    DECLARE estado_actual VARCHAR(50);
    DECLARE ultimo INT DEFAULT 0;

    -- 1. Consultar cantidad y estado actual de la merma original
    SELECT cantidad, edo_flujo_merma 
    INTO cantidad_original, estado_actual
    FROM REGISTRO_MERMA
    WHERE folio = NEW.registro_merma;

    -- 1.1 Validar que la merma esté en estado 'REGISTRADA'
    IF estado_actual <> 'REGISTRADA' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: No se puede crear una discrepancia. La merma no se encuentra en estado REGISTRADA.';
    END IF;

    -- 1.2 Validar cantidad reportada contra el registro original
    IF NEW.cantidad_reportada <> cantidad_original THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: La cantidad reportada no coincide con el registro original de la merma.';
    END IF;

    -- 2. Autocompletar la fecha de reporte si viene vacía
    IF NEW.fecha_reporte IS NULL THEN
        SET NEW.fecha_reporte = CURDATE();
    END IF;

    -- 3. Autogenerar folio (DISC-YYYY-XXX) si no se especifica
    IF NEW.folio IS NULL OR NEW.folio = '' THEN
        SELECT IFNULL(
            MAX(CAST(SUBSTRING(folio, 11) AS UNSIGNED)),
            0
        )
        INTO ultimo
        FROM DISCREPANCIA
        WHERE folio LIKE CONCAT('DISC-', YEAR(CURDATE()), '-%');

        SET NEW.folio = CONCAT(
            'DISC-',
            YEAR(CURDATE()),
            '-',
            LPAD(ultimo + 1, 3, '0')
        );
    END IF;

    -- 4. Calcular la diferencia
    SET NEW.diferencia = NEW.cantidad_recibida - NEW.cantidad_reportada;

    -- 5. Cambiar el estado en la tabla REGISTRO_MERMA
    UPDATE REGISTRO_MERMA
    SET edo_flujo_merma = 'DISCREPAN'
    WHERE folio = NEW.registro_merma;

END $$

DELIMITER ;