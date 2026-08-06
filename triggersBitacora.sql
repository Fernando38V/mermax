/* ==========================================================================
   TRIGGERS DE BITÁCORA DE AUDITORÍA (RF-47 / RNF-09)
   MERMAX - Sistema de Control y Trazabilidad de Mermas
   ==========================================================================

   ALCANCE (definido con Axel):
     - REGISTRO_MERMA
     - DISCREPANCIA
     - SOLICITUD_INSPECCION
     - REGISTRO_DISPOSICION
     - USUARIO
     - EMPLEADO
   Se cubren INSERT y UPDATE (los DELETE no aplican: el sistema usa baja
   lógica con la columna `activo`, y eso ya se audita como UPDATE).

   CÓMO SE RESUELVE "QUIÉN HIZO LA ACCIÓN":
     Se usa la variable de sesión MySQL `@usuario_actual`. La aplicación
     (Django, vía ApiClient o un decorador/middleware común) debe ejecutar:

         SET @usuario_actual = <num_usuario_de_la_sesion>;

     justo antes de cualquier INSERT/UPDATE sobre las tablas auditadas,
     dentro de la MISMA conexión/transacción. Esto es necesario porque:
       - En UPDATE, quien modifica un registro no siempre es el usuario
         "dueño" original (ej. un Ingeniero de Calidad resuelve una
         discrepancia reportada por un Almacenista).
       - USUARIO y EMPLEADO no tienen un campo que apunte a "quién hizo
         el cambio", solo a sí mismos.

     Por seguridad ante olvidos, en REGISTRO_MERMA, DISCREPANCIA,
     SOLICITUD_INSPECCION y REGISTRO_DISPOSICION hay un fallback al
     campo `usuario` propio de la fila si @usuario_actual no fue seteada.
     En USUARIO y EMPLEADO NO hay fallback confiable, así que si
     @usuario_actual no está seteada, el trigger detiene la operación
     con SIGNAL (mejor bloquear que registrar auditoría incorrecta o nula).

   IMPORTANTE - Pooling de conexiones:
     Si Django reutiliza conexiones entre requests (CONN_MAX_AGE > 0),
     @usuario_actual puede "quedar pegada" del request anterior. Setéala
     SIEMPRE al inicio de cada operación de escritura, no confíes en que
     ya esté vacía.

   SEGURIDAD:
     El trigger de USUARIO NUNCA guarda `contrasena` (ni el hash) en la
     bitácora. Solo registra si la contraseña cambió (booleano), no su
     valor. Nunca se debe exponer eso en un log.
   ========================================================================== */


/* ==========================================================================
   1. REGISTRO_MERMA
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_bitacora_ins_registro_merma;
DROP TRIGGER IF EXISTS tg_bitacora_upd_registro_merma;

DELIMITER $$

CREATE TRIGGER tg_bitacora_ins_registro_merma
AFTER INSERT ON REGISTRO_MERMA
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    SET v_usuario = IFNULL(@usuario_actual, NEW.usuario);

    INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
    VALUES (
        v_usuario,
        'REGISTRO_MERMA',
        'CREATE',
        NULL,
        JSON_OBJECT(
            'folio', NEW.folio,
            'cantidad', NEW.cantidad,
            'costo_total', NEW.costo_total,
            'fecha', NEW.fecha,
            'unidad', NEW.unidad,
            'descripcion', NEW.descripcion,
            'edo_flujo_merma', NEW.edo_flujo_merma,
            'usuario', NEW.usuario,
            'lote_material', NEW.lote_material,
            'componente', NEW.componente,
            'tipo_merma', NEW.tipo_merma,
            'causa_raiz', NEW.causa_raiz,
            'estacion_trabajo', NEW.estacion_trabajo,
            'orden_produccion', NEW.orden_produccion
        ),
        @motivo_actual,
        NOW()
    );
END$$

CREATE TRIGGER tg_bitacora_upd_registro_merma
AFTER UPDATE ON REGISTRO_MERMA
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    DECLARE v_old JSON;
    DECLARE v_new JSON;

    SET v_old = JSON_OBJECT(
            'folio', OLD.folio, 'cantidad', OLD.cantidad, 'costo_total', OLD.costo_total,
            'fecha', OLD.fecha, 'unidad', OLD.unidad, 'descripcion', OLD.descripcion,
            'edo_flujo_merma', OLD.edo_flujo_merma, 'usuario', OLD.usuario,
            'lote_material', OLD.lote_material, 'componente', OLD.componente,
            'tipo_merma', OLD.tipo_merma, 'causa_raiz', OLD.causa_raiz,
            'estacion_trabajo', OLD.estacion_trabajo, 'orden_produccion', OLD.orden_produccion
        );
    SET v_new = JSON_OBJECT(
            'folio', NEW.folio, 'cantidad', NEW.cantidad, 'costo_total', NEW.costo_total,
            'fecha', NEW.fecha, 'unidad', NEW.unidad, 'descripcion', NEW.descripcion,
            'edo_flujo_merma', NEW.edo_flujo_merma, 'usuario', NEW.usuario,
            'lote_material', NEW.lote_material, 'componente', NEW.componente,
            'tipo_merma', NEW.tipo_merma, 'causa_raiz', NEW.causa_raiz,
            'estacion_trabajo', NEW.estacion_trabajo, 'orden_produccion', NEW.orden_produccion
        );

    IF CAST(v_old AS CHAR) <> CAST(v_new AS CHAR) THEN
        SET v_usuario = IFNULL(@usuario_actual, NEW.usuario);

        INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
        VALUES (v_usuario, 'REGISTRO_MERMA', 'UPDATE', v_old, v_new, @motivo_actual, NOW());
    END IF;
END$$

DELIMITER ;


/* ==========================================================================
   2. DISCREPANCIA
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_bitacora_ins_discrepancia;
DROP TRIGGER IF EXISTS tg_bitacora_upd_discrepancia;

DELIMITER $$

CREATE TRIGGER tg_bitacora_ins_discrepancia
AFTER INSERT ON DISCREPANCIA
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    SET v_usuario = IFNULL(@usuario_actual, NEW.usuario_reporte);

    INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
    VALUES (
        v_usuario,
        'DISCREPANCIA',
        'CREATE',
        NULL,
        JSON_OBJECT(
            'folio', NEW.folio,
            'fecha_reporte', NEW.fecha_reporte,
            'cantidad_reportada', NEW.cantidad_reportada,
            'cantidad_recibida', NEW.cantidad_recibida,
            'diferencia', NEW.diferencia,
            'motivo_reporte', NEW.motivo_reporte,
            'usuario_reporte', NEW.usuario_reporte,
            'registro_merma', NEW.registro_merma,
            'edo_discrepancia', NEW.edo_discrepancia,
            'fecha_resolucion', NEW.fecha_resolucion,
            'motivo_resolucion', NEW.motivo_resolucion,
            'usuario_resolucion', NEW.usuario_resolucion
        ),
        @motivo_actual,
        NOW()
    );
END$$

CREATE TRIGGER tg_bitacora_upd_discrepancia
AFTER UPDATE ON DISCREPANCIA
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    DECLARE v_old JSON;
    DECLARE v_new JSON;

    SET v_old = JSON_OBJECT(
            'folio', OLD.folio, 'fecha_reporte', OLD.fecha_reporte,
            'cantidad_reportada', OLD.cantidad_reportada, 'cantidad_recibida', OLD.cantidad_recibida,
            'diferencia', OLD.diferencia, 'motivo_reporte', OLD.motivo_reporte,
            'usuario_reporte', OLD.usuario_reporte, 'registro_merma', OLD.registro_merma,
            'edo_discrepancia', OLD.edo_discrepancia, 'fecha_resolucion', OLD.fecha_resolucion,
            'motivo_resolucion', OLD.motivo_resolucion, 'usuario_resolucion', OLD.usuario_resolucion
        );
    SET v_new = JSON_OBJECT(
            'folio', NEW.folio, 'fecha_reporte', NEW.fecha_reporte,
            'cantidad_reportada', NEW.cantidad_reportada, 'cantidad_recibida', NEW.cantidad_recibida,
            'diferencia', NEW.diferencia, 'motivo_reporte', NEW.motivo_reporte,
            'usuario_reporte', NEW.usuario_reporte, 'registro_merma', NEW.registro_merma,
            'edo_discrepancia', NEW.edo_discrepancia, 'fecha_resolucion', NEW.fecha_resolucion,
            'motivo_resolucion', NEW.motivo_resolucion, 'usuario_resolucion', NEW.usuario_resolucion
        );

    IF CAST(v_old AS CHAR) <> CAST(v_new AS CHAR) THEN
        -- Prioridad de autoría: quien resuelve (si ya se asignó) > quien reportó
        SET v_usuario = IFNULL(@usuario_actual, IFNULL(NEW.usuario_resolucion, NEW.usuario_reporte));

        INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
        VALUES (v_usuario, 'DISCREPANCIA', 'UPDATE', v_old, v_new, @motivo_actual, NOW());
    END IF;
END$$

DELIMITER ;


/* ==========================================================================
   3. SOLICITUD_INSPECCION
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_bitacora_ins_solicitud_inspeccion;
DROP TRIGGER IF EXISTS tg_bitacora_upd_solicitud_inspeccion;

DELIMITER $$

CREATE TRIGGER tg_bitacora_ins_solicitud_inspeccion
AFTER INSERT ON SOLICITUD_INSPECCION
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    SET v_usuario = IFNULL(@usuario_actual, NEW.usuario);

    INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
    VALUES (
        v_usuario,
        'SOLICITUD_INSPECCION',
        'CREATE',
        NULL,
        JSON_OBJECT(
            'codigo', NEW.codigo,
            'fecha_generacion', NEW.fecha_generacion,
            'hora_generacion', NEW.hora_generacion,
            'fecha_atencion', NEW.fecha_atencion,
            'hora_atencion', NEW.hora_atencion,
            'edo_solicitud', NEW.edo_solicitud,
            'registro_merma', NEW.registro_merma,
            'usuario', NEW.usuario,
            'usuario_atencion', NEW.usuario_atencion
        ),
        @motivo_actual,
        NOW()
    );
END$$

CREATE TRIGGER tg_bitacora_upd_solicitud_inspeccion
AFTER UPDATE ON SOLICITUD_INSPECCION
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    DECLARE v_old JSON;
    DECLARE v_new JSON;

    SET v_old = JSON_OBJECT(
            'codigo', OLD.codigo, 'fecha_generacion', OLD.fecha_generacion,
            'hora_generacion', OLD.hora_generacion, 'fecha_atencion', OLD.fecha_atencion,
            'hora_atencion', OLD.hora_atencion, 'edo_solicitud', OLD.edo_solicitud,
            'registro_merma', OLD.registro_merma, 'usuario', OLD.usuario,
            'usuario_atencion', OLD.usuario_atencion
        );
    SET v_new = JSON_OBJECT(
            'codigo', NEW.codigo, 'fecha_generacion', NEW.fecha_generacion,
            'hora_generacion', NEW.hora_generacion, 'fecha_atencion', NEW.fecha_atencion,
            'hora_atencion', NEW.hora_atencion, 'edo_solicitud', NEW.edo_solicitud,
            'registro_merma', NEW.registro_merma, 'usuario', NEW.usuario,
            'usuario_atencion', NEW.usuario_atencion
        );

    IF CAST(v_old AS CHAR) <> CAST(v_new AS CHAR) THEN
        -- Prioridad de autoría: quien atiende la solicitud (si ya se asignó) > quien la generó
        SET v_usuario = IFNULL(@usuario_actual, IFNULL(NEW.usuario_atencion, NEW.usuario));

        INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
        VALUES (v_usuario, 'SOLICITUD_INSPECCION', 'UPDATE', v_old, v_new, @motivo_actual, NOW());
    END IF;
END$$

DELIMITER ;


/* ==========================================================================
   4. REGISTRO_DISPOSICION
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_bitacora_ins_registro_disposicion;
DROP TRIGGER IF EXISTS tg_bitacora_upd_registro_disposicion;

DELIMITER $$

CREATE TRIGGER tg_bitacora_ins_registro_disposicion
AFTER INSERT ON REGISTRO_DISPOSICION
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    SET v_usuario = IFNULL(@usuario_actual, NEW.usuario);

    INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
    VALUES (
        v_usuario,
        'REGISTRO_DISPOSICION',
        'CREATE',
        NULL,
        JSON_OBJECT(
            'folio', NEW.folio,
            'fecha_determinacion', NEW.fecha_determinacion,
            'fecha_ejecucion', NEW.fecha_ejecucion,
            'cantidad_ejecutada', NEW.cantidad_ejecutada,
            'observaciones', NEW.observaciones,
            'sale_almacen', NEW.sale_almacen,
            'llega_almacen', NEW.llega_almacen,
            'disposicion_final', NEW.disposicion_final,
            'usuario', NEW.usuario,
            'registro_merma', NEW.registro_merma,
            'estado_disposicion', NEW.estado_disposicion
        ),
        @motivo_actual,
        NOW()
    );
END$$

CREATE TRIGGER tg_bitacora_upd_registro_disposicion
AFTER UPDATE ON REGISTRO_DISPOSICION
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    DECLARE v_old JSON;
    DECLARE v_new JSON;

    SET v_old = JSON_OBJECT(
            'folio', OLD.folio, 'fecha_determinacion', OLD.fecha_determinacion,
            'fecha_ejecucion', OLD.fecha_ejecucion, 'cantidad_ejecutada', OLD.cantidad_ejecutada,
            'observaciones', OLD.observaciones, 'sale_almacen', OLD.sale_almacen,
            'llega_almacen', OLD.llega_almacen, 'disposicion_final', OLD.disposicion_final,
            'usuario', OLD.usuario, 'registro_merma', OLD.registro_merma,
            'estado_disposicion', OLD.estado_disposicion
        );
    SET v_new = JSON_OBJECT(
            'folio', NEW.folio, 'fecha_determinacion', NEW.fecha_determinacion,
            'fecha_ejecucion', NEW.fecha_ejecucion, 'cantidad_ejecutada', NEW.cantidad_ejecutada,
            'observaciones', NEW.observaciones, 'sale_almacen', NEW.sale_almacen,
            'llega_almacen', NEW.llega_almacen, 'disposicion_final', NEW.disposicion_final,
            'usuario', NEW.usuario, 'registro_merma', NEW.registro_merma,
            'estado_disposicion', NEW.estado_disposicion
        );

    IF CAST(v_old AS CHAR) <> CAST(v_new AS CHAR) THEN
        SET v_usuario = IFNULL(@usuario_actual, NEW.usuario);

        INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
        VALUES (v_usuario, 'REGISTRO_DISPOSICION', 'UPDATE', v_old, v_new, @motivo_actual, NOW());
    END IF;
END$$

DELIMITER ;


/* ==========================================================================
   5. USUARIO
   No hay fallback: si @usuario_actual no está seteada, se bloquea el
   INSERT/UPDATE. La contraseña NUNCA se guarda en la bitácora.
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_bitacora_ins_usuario;
DROP TRIGGER IF EXISTS tg_bitacora_upd_usuario;

DELIMITER $$

CREATE TRIGGER tg_bitacora_ins_usuario
AFTER INSERT ON USUARIO
FOR EACH ROW
BEGIN
    IF @usuario_actual IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error de auditoria: debe establecerse @usuario_actual antes de crear un USUARIO.';
    END IF;

    INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
    VALUES (
        @usuario_actual,
        'USUARIO',
        'CREATE',
        NULL,
        JSON_OBJECT(
            'num', NEW.num,
            'username', NEW.username,
            'correo', NEW.correo,
            'empleado', NEW.empleado,
            'rol', NEW.rol,
            'activo', NEW.activo
        ),
        @motivo_actual,
        NOW()
    );
END$$

CREATE TRIGGER tg_bitacora_upd_usuario
AFTER UPDATE ON USUARIO
FOR EACH ROW
BEGIN
    DECLARE v_old JSON;
    DECLARE v_new JSON;
    DECLARE v_password_cambio BOOLEAN;

    SET v_password_cambio = NOT (OLD.contrasena <=> NEW.contrasena);

    -- OJO: nunca se incluye `contrasena`/hash en la bitácora, solo si cambió.
    SET v_old = JSON_OBJECT(
            'num', OLD.num, 'username', OLD.username, 'correo', OLD.correo,
            'empleado', OLD.empleado, 'rol', OLD.rol, 'activo', OLD.activo
        );
    SET v_new = JSON_OBJECT(
            'num', NEW.num, 'username', NEW.username, 'correo', NEW.correo,
            'empleado', NEW.empleado, 'rol', NEW.rol, 'activo', NEW.activo,
            'password_modificada', v_password_cambio
        );

    IF CAST(v_old AS CHAR) <> CAST(v_new AS CHAR) OR v_password_cambio THEN
        IF @usuario_actual IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error de auditoria: debe establecerse @usuario_actual antes de modificar un USUARIO.';
        END IF;

        INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
        VALUES (@usuario_actual, 'USUARIO', 'UPDATE', v_old, v_new, @motivo_actual, NOW());
    END IF;
END$$

DELIMITER ;


/* ==========================================================================
   6. EMPLEADO
   No hay fallback fiable propio de la tabla. Si @usuario_actual no está
   seteada, se intenta usar la cuenta de USUARIO ligada a ese mismo
   empleado (si existe); si tampoco existe, se bloquea la operación.
   ========================================================================== */

DROP TRIGGER IF EXISTS tg_bitacora_ins_empleado;
DROP TRIGGER IF EXISTS tg_bitacora_upd_empleado;

DELIMITER $$

CREATE TRIGGER tg_bitacora_ins_empleado
AFTER INSERT ON EMPLEADO
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    SET v_usuario = @usuario_actual;

    IF v_usuario IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error de auditoria: debe establecerse @usuario_actual antes de crear un EMPLEADO.';
    END IF;

    INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
    VALUES (
        v_usuario,
        'EMPLEADO',
        'CREATE',
        NULL,
        JSON_OBJECT(
            'numero', NEW.numero,
            'emNombre', NEW.emNombre,
            'emPrimerApell', NEW.emPrimerApell,
            'emSegundoApell', NEW.emSegundoApell,
            'fecha_nacimiento', NEW.fecha_nacimiento,
            'fecha_ingreso', NEW.fecha_ingreso,
            'area', NEW.area,
            'turno', NEW.turno,
            'activo', NEW.activo
        ),
        @motivo_actual,
        NOW()
    );
END$$

CREATE TRIGGER tg_bitacora_upd_empleado
AFTER UPDATE ON EMPLEADO
FOR EACH ROW
BEGIN
    DECLARE v_usuario INT;
    DECLARE v_old JSON;
    DECLARE v_new JSON;

    SET v_old = JSON_OBJECT(
            'numero', OLD.numero, 'emNombre', OLD.emNombre, 'emPrimerApell', OLD.emPrimerApell,
            'emSegundoApell', OLD.emSegundoApell, 'fecha_nacimiento', OLD.fecha_nacimiento,
            'fecha_ingreso', OLD.fecha_ingreso, 'area', OLD.area, 'turno', OLD.turno, 'activo', OLD.activo
        );
    SET v_new = JSON_OBJECT(
            'numero', NEW.numero, 'emNombre', NEW.emNombre, 'emPrimerApell', NEW.emPrimerApell,
            'emSegundoApell', NEW.emSegundoApell, 'fecha_nacimiento', NEW.fecha_nacimiento,
            'fecha_ingreso', NEW.fecha_ingreso, 'area', NEW.area, 'turno', NEW.turno, 'activo', NEW.activo
        );

    IF CAST(v_old AS CHAR) <> CAST(v_new AS CHAR) THEN
        -- Fallback: la cuenta de usuario ligada a este mismo empleado, si existe
        SET v_usuario = COALESCE(@usuario_actual, (SELECT num FROM USUARIO WHERE empleado = NEW.numero LIMIT 1));

        IF v_usuario IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Error de auditoria: debe establecerse @usuario_actual antes de modificar este EMPLEADO.';
        END IF;

        INSERT INTO BITACORA_AUDITORIA (usuario, modulo, accion, valor_anterior, valor_nuevo, motivo, fecha_hora)
        VALUES (v_usuario, 'EMPLEADO', 'UPDATE', v_old, v_new, @motivo_actual, NOW());
    END IF;
END$$

DELIMITER ;