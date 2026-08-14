/* ==========================================================================
   PROCEDIMIENTOS ALMACENADOS — FLUJO DEL CICLO DE VIDA DE LA MERMA
   MERMAX - Sistema de Control y Trazabilidad de Mermas
   ==========================================================================
   1. sp_confirmar_recepcion_merma       (RF-04)
   2. sp_resolver_discrepancia           (RF-05 / RF-48)
   3. sp_generar_registro_disposicion    (RF-08 / RF-09 / RF-10, parte 1)
   4. sp_cerrar_solicitud_inspeccion     (RF-08 / RF-09 / RF-10, parte 2)
   5. sp_ejecutar_disposicion_final
   6. sp_trazabilidad_lote               (RF-11)

   Nota: los procedimientos 3 y 4 forman parte de un mismo proceso de negocio
   (el dictamen de disposición final) y se invocan en secuencia desde la
   misma vista de Django, separados por responsabilidad única: el 3 genera
   el registro y su tabla satélite, el 4 cierra la solicitud y la merma.
   ========================================================================== */

/*
    1. sp_confirmar_recepcion_merma
*/
DROP PROCEDURE IF EXISTS sp_confirmar_recepcion_merma;
DELIMITER $$
CREATE PROCEDURE sp_confirmar_recepcion_merma(
    IN folioMerma VARCHAR(20)
)
BEGIN
    DECLARE estadoActual VARCHAR(10);

    SELECT edo_flujo_merma INTO estadoActual
    FROM REGISTRO_MERMA
    WHERE folio = folioMerma;

    IF estadoActual IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No existe una merma con ese folio.';
    END IF;

    IF estadoActual <> 'REGISTRADA' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Solo se puede confirmar recepción de mermas en estado REGISTRADA.';
    END IF;

    UPDATE REGISTRO_MERMA
    SET edo_flujo_merma = 'RECIBIDA'
    WHERE folio = folioMerma;

    SELECT folioMerma AS folio, 'RECIBIDA' AS nuevoEstado;
END$$
DELIMITER ;

-- SELECT folio, edo_flujo_merma FROM REGISTRO_MERMA WHERE edo_flujo_merma = 'REGISTRADA' LIMIT 5;

-- Llamada sp_confirmar_recepcion_merma:
-- CALL sp_confirmar_recepcion_merma('MRM-2026-010');
-- Verifica que el trigger disparó la solicitud sola:
-- SELECT * FROM SOLICITUD_INSPECCION WHERE registro_merma = 'MRM-2026-010';

/*
    Estado de un folio de registro de merma:

select 
folio as Folio, 
edo_flujo_merma as Estado
from registro_merma
where folio = 'MRM-2026-010';
*/

/*
    2. sp_resolver_discrepancia
*/
DROP PROCEDURE IF EXISTS sp_resolver_discrepancia;
DELIMITER $$
CREATE PROCEDURE sp_resolver_discrepancia(
    IN folioDiscrepancia VARCHAR(20),
    IN motivoResolucion VARCHAR(100),
    IN cantidadCorrecta DECIMAL(10,2),  
    IN usuarioResolucion INT
)
BEGIN
    DECLARE estadoActual VARCHAR(10);
    DECLARE folioMerma VARCHAR(20);
    DECLARE discrepanciasAbiertas INT;

    SELECT edo_discrepancia, registro_merma
        INTO estadoActual, folioMerma
    FROM DISCREPANCIA
    WHERE folio = folioDiscrepancia;

    IF estadoActual IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No existe una discrepancia con ese folio.';
    END IF;

    IF estadoActual <> 'ABIERTA' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Esta discrepancia ya se encuentra resuelta.';
    END IF;

    IF motivoResolucion IS NULL OR TRIM(motivoResolucion) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El motivo de resolución es obligatorio.';
    END IF;

    IF cantidadCorrecta IS NULL OR cantidadCorrecta < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La cantidad correcta es obligatoria y debe ser mayor a cero.'
    END IF;

    UPDATE DISCREPANCIA
    SET edo_discrepancia = 'RESUELTA',
        fecha_resolucion = CURDATE(),
        motivo_resolucion = motivoResolucion,
        usuario_resolucion = usuarioResolucion
    WHERE folio = folioDiscrepancia;

    SET @resolviendo_discrepancia = 1;

    UPDATE REGISTRO_MERMA 
    SET cantidad = cantidadCorrecta
    WHERE folio = folioMerma;

    SET @resolviendo_discrepancia = NULL;

    SELECT COUNT(*) INTO discrepanciasAbiertas
    FROM DISCREPANCIA
    WHERE registro_merma = folioMerma
      AND edo_discrepancia = 'ABIERTA';

    IF discrepanciasAbiertas = 0 THEN
        UPDATE REGISTRO_MERMA
        SET edo_flujo_merma = 'RECIBIDA'
        WHERE folio = folioMerma;
    END IF;

    SELECT folioDiscrepancia AS folioDiscrepancia,
           folioMerma AS folioMerma,
           discrepanciasAbiertas AS discrepanciasRestantes;
END$$
DELIMITER ;

/*

-- Ubicar una discrepancia abierta:
-- SELECT folio, registro_merma, edo_discrepancia 
FROM DISCREPANCIA 
WHERE edo_discrepancia = 'ABIERTA' LIMIT 5;
-- Llamada sp_resolver_discrepancia:
-- CALL sp_resolver_discrepancia
('DISC-2026-004', 'Conteo verificado con báscula', 3);
-- Confirmamos solicitud de inspección creada:
-- SELECT * FROM SOLICITUD_INSPECCION 
WHERE registro_merma = 'MRM-2026-012';

-- SELECT codigo as Codigo, 
edo_solicitud as EstadoSolicitud
FROM SOLICITUD_INSPECCION 
WHERE registro_merma = 'MRM-2026-012';

-- SELECT folio as Folio, 
edo_flujo_merma as EstadoMerma
FROM REGISTRO_MERMA 
WHERE folio = 'MRM-2026-012';



-- Para el flujo 3 -> 4, se necesita una merma en INSPECCIO con su solicitud PENDIENTE:
-- SELECT si.codigo, si.registro_merma, rm.edo_flujo_merma
FROM SOLICITUD_INSPECCION si
JOIN REGISTRO_MERMA rm ON rm.folio = si.registro_merma
WHERE si.edo_solicitud = 'PENDIENTE' AND rm.edo_flujo_merma = 'INSPECCIO';

*/

/*
    3. sp_generar_registro_disposicion
*/

DROP PROCEDURE IF EXISTS sp_generar_registro_disposicion;
DELIMITER $$
CREATE PROCEDURE sp_generar_registro_disposicion(
    IN folioMerma VARCHAR(20),
    IN dictamen VARCHAR(10),           -- RTN_PROV / RECICLAJE / DESTR_CTRL
    IN usuarioDictamina INT,
    IN cantidadEjecutada DECIMAL(10,2),
    IN observaciones VARCHAR(255),
    IN proveedor VARCHAR(10),          -- solo si RTN_PROV
    IN motivoRechazo VARCHAR(255),     -- solo si RTN_PROV
    IN empresaRecicladora VARCHAR(10), -- solo si RECICLAJE
    IN pesoNeto DECIMAL(10,2),         -- solo si RECICLAJE
    IN metodoDestruccion VARCHAR(10),  -- solo si DESTR_CTRL
    IN folioProbatorio VARCHAR(20),    -- solo si DESTR_CTRL
    OUT folioDisposicion VARCHAR(20)
)
BEGIN
    DECLARE edoFlujoMerma VARCHAR(10);
    DECLARE folioSatelite VARCHAR(20);
    DECLARE anio VARCHAR(4);
    DECLARE consecutivo INT;

    SET anio = YEAR(CURDATE());

    SELECT edo_flujo_merma INTO edoFlujoMerma
    FROM REGISTRO_MERMA WHERE folio = folioMerma;

    IF edoFlujoMerma IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No existe esa merma.';
    END IF;

    IF edoFlujoMerma <> 'INSPECCIO' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La merma debe estar en INSPECCIO para poder dictaminarse.';
    END IF;

    IF dictamen NOT IN ('RTN_PROV', 'RECICLAJE', 'DESTR_CTRL') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Dictamen inválido.';
    END IF;

    SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(folio, '-', -1) AS UNSIGNED)), 0) + 1
        INTO consecutivo
    FROM REGISTRO_DISPOSICION
    WHERE folio LIKE CONCAT('DISP-', anio, '-%');

    SET folioDisposicion = CONCAT('DISP-', anio, '-', LPAD(consecutivo, 3, '0'));

    INSERT INTO REGISTRO_DISPOSICION (
        folio, fecha_determinacion, fecha_ejecucion, cantidad_ejecutada,
        observaciones, sale_almacen, llega_almacen, disposicion_final,
        usuario, registro_merma, estado_disposicion
    ) VALUES (
        folioDisposicion, CURDATE(), NULL, cantidadEjecutada,
        IFNULL(observaciones, CONCAT('Dictamen emitido tras inspección del folio ', folioMerma)),
        'ALM-SCRP', NULL, dictamen,
        usuarioDictamina, folioMerma, 'PENDIENTE'
    );

    IF dictamen = 'RTN_PROV' THEN
        SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(folio, '-', -1) AS UNSIGNED)), 0) + 1
            INTO consecutivo
        FROM disposicion_devolucion WHERE folio LIKE CONCAT('DEV-', anio, '-%');
        SET folioSatelite = CONCAT('DEV-', anio, '-', LPAD(consecutivo, 3, '0'));

        INSERT INTO disposicion_devolucion (folio, motivo_rechazo, registro_disposicion, proveedor)
        VALUES (folioSatelite, motivoRechazo, folioDisposicion, proveedor);
    ELSEIF dictamen = 'RECICLAJE' THEN
        SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(folio, '-', -1) AS UNSIGNED)), 0) + 1
            INTO consecutivo
        FROM DISPOSICION_RECICLAJE WHERE folio LIKE CONCAT('RCJ-', anio, '-%');
        SET folioSatelite = CONCAT('RCJ-', anio, '-', LPAD(consecutivo, 3, '0'));

        INSERT INTO DISPOSICION_RECICLAJE (folio, empresa_recicladora, peso_neto, registro_disposicion)
        VALUES (folioSatelite, empresaRecicladora, pesoNeto, folioDisposicion);
    ELSE
        SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(folio, '-', -1) AS UNSIGNED)), 0) + 1
            INTO consecutivo
        FROM DISPOSICION_DESECHO WHERE folio LIKE CONCAT('DES-', anio, '-%');
        SET folioSatelite = CONCAT('DES-', anio, '-', LPAD(consecutivo, 3, '0'));

        INSERT INTO DISPOSICION_DESECHO (folio, metodo_destruccion, folio_probatorio, registro_disposicion)
        VALUES (folioSatelite, metodoDestruccion, folioProbatorio, folioDisposicion);
    END IF;
END$$
DELIMITER ;

-- elegir una empresa de reciclaje
-- SELECT codigo, nombre FROM EMPRESA_RECICLADORA LIMIT 5;
/*
-- CALL sp_generar_registro_disposicion(
    'MRM-SEED-0004',
    'RECICLAJE', 3,
    NULL, NULL,
    NULL, NULL,
    'REC-01',   -- reemplazar por el código real que te dio el SELECT
    12.5,
    NULL, NULL,
    @folioGenerado
);
*/

-- SELECT @folioGenerado;

-- verificar que se creo bien
-- SELECT * FROM REGISTRO_DISPOSICION WHERE folio = @folioGenerado;
-- SELECT * FROM DISPOSICION_RECICLAJE WHERE registro_disposicion = @folioGenerado;


/* 
   4. sp_cerrar_solicitud_inspeccion
*/
DROP PROCEDURE IF EXISTS sp_cerrar_solicitud_inspeccion;
DELIMITER $$
CREATE PROCEDURE sp_cerrar_solicitud_inspeccion(
    IN codigoSolicitud VARCHAR(20),
    IN folioMerma VARCHAR(20),
    IN usuarioAtencion INT
)
BEGIN
    DECLARE edoSolicitud VARCHAR(10);

    SELECT edo_solicitud INTO edoSolicitud
    FROM SOLICITUD_INSPECCION WHERE codigo = codigoSolicitud;

    IF edoSolicitud IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No existe esa solicitud de inspección.';
    END IF;
    IF edoSolicitud <> 'PENDIENTE' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Esta solicitud ya fue atendida.';
    END IF;

    UPDATE SOLICITUD_INSPECCION
    SET edo_solicitud = 'ATENDIDA',
        fecha_atencion = CURDATE(),
        hora_atencion = CURTIME(),
        usuario_atencion = usuarioAtencion
    WHERE codigo = codigoSolicitud;

    UPDATE REGISTRO_MERMA
    SET edo_flujo_merma = 'CERRADA'
    WHERE folio = folioMerma;

    SELECT codigoSolicitud AS codigoSolicitud,
           folioMerma AS folioMerma,
           'CERRADA' AS nuevoEstadoMerma;
END$$
DELIMITER ;

-- usando el mismo folio de merma:
-- CALL sp_cerrar_solicitud_inspeccion('SOL-MRM-SEED-0004', 'MRM-SEED-0004', 3);

-- confirmaa el cierre completo
-- SELECT edo_solicitud, fecha_atencion FROM SOLICITUD_INSPECCION WHERE codigo = 'SOL-MRM-SEED-0004';
-- SELECT edo_flujo_merma FROM REGISTRO_MERMA WHERE folio = 'MRM-SEED-0004';


/*
    5. sp_ejecutar_disposicion_final
*/

DROP PROCEDURE IF EXISTS sp_ejecutar_disposicion_final;
DELIMITER $$
CREATE PROCEDURE sp_ejecutar_disposicion_final(
    IN folioDisposicion VARCHAR(20)
)
BEGIN
    DECLARE estadoDisposicion VARCHAR(10);
    DECLARE folioMerma VARCHAR(20);
    DECLARE edoFlujoMerma VARCHAR(10);

    SELECT estado_disposicion, registro_merma
        INTO estadoDisposicion, folioMerma
    FROM REGISTRO_DISPOSICION
    WHERE folio = folioDisposicion;

    IF estadoDisposicion IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No existe esa disposición.';
    END IF;

    IF estadoDisposicion = 'EJECUTADO' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Esta disposición ya fue ejecutada.';
    END IF;

    SELECT edo_flujo_merma INTO edoFlujoMerma
    FROM REGISTRO_MERMA WHERE folio = folioMerma;

    IF edoFlujoMerma <> 'CERRADA' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede ejecutar una disposición cuya merma no está CERRADA.';
    END IF;

    UPDATE REGISTRO_DISPOSICION
    SET estado_disposicion = 'EJECUTADO',
        fecha_ejecucion = CURDATE()
    WHERE folio = folioDisposicion;

    SELECT folioDisposicion AS folio, 'EJECUTADO' AS nuevoEstado, CURDATE() AS fechaEjecucion;
END$$
DELIMITER ;


-- Llamada sp_ejecutar_disposicion_final:
-- CALL sp_ejecutar_disposicion_final('DISP-2026-006');

-- Verificamos:
-- SELECT folio, estado_disposicion, fecha_ejecucion FROM REGISTRO_DISPOSICION WHERE folio = 'DISP-2026-006';

-- Prueba extra con caso de error (mensaje: esta disposicion ya fue ejecutada.):
-- CALL sp_ejecutar_disposicion_final('DISP-2026-006');

/*
    6. sp_trazabilidad_lote
*/
DROP PROCEDURE IF EXISTS sp_trazabilidad_lote;

DELIMITER $$

CREATE PROCEDURE sp_trazabilidad_lote(
    IN numLote INT
)
BEGIN
    DECLARE cantidadRecibida DECIMAL(10,2);

    SELECT cantidad INTO cantidadRecibida
    FROM LOTE_MATERIAL WHERE num = numLote;

    IF cantidadRecibida IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No existe ese lote.';
    END IF;

    SELECT
        numLote AS numLote,
        cantidadRecibida AS cantidadRecibida,
        IFNULL(SUM(rm.cantidad), 0) AS cantidadMermada,
        ROUND(IFNULL(SUM(rm.cantidad), 0) / cantidadRecibida * 100, 2) AS porcentajeMerma,
        IFNULL(SUM(rm.costo_total), 0) AS costoTotalDesperdicio,
        COUNT(rm.folio) AS eventosMerma
    FROM LOTE_MATERIAL lm
    LEFT JOIN REGISTRO_MERMA rm ON rm.lote_material = lm.num
    WHERE lm.num = numLote;
END$$

DELIMITER ;

-- tomamos cualquier numero de la lista
-- SELECT DISTINCT lote_material FROM REGISTRO_MERMA WHERE lote_material IS NOT NULL LIMIT 5;

-- Llamada sp_trazabilidad_lote:
-- CALL sp_trazabilidad_lote(2);