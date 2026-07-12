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

-- CONSULTAS PRUEBA

-- TRIGGERS