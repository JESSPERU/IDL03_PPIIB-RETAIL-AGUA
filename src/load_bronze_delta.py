import hashlib
import uuid
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from utils.db import get_engine
from utils.logger import get_logger


logger = get_logger("load_bronze_delta")
engine = get_engine()


AUDIT_COLUMNS = [
    "etl_batch_id",
    "etl_fecha_carga",
    "etl_archivo_origen",
    "etl_hash_registro",
    "etl_usuario",
]


def calcular_hash_fila(row: pd.Series) -> str:
    """
    Calcula un hash del contenido de cada fila.
    Sirve para detectar duplicados o cambios.
    """
    texto = "|".join([str(valor) for valor in row.fillna("").values])
    return hashlib.md5(texto.encode("utf-8")).hexdigest()


def leer_configuracion_pipeline() -> pd.DataFrame:
    """
    Lee meta.pipeline_config para saber qué archivos cargar,
    en qué orden y si la carga es FULL o DELTA.
    """
    query = """
        SELECT
            nombre_tabla,
            ruta_archivo,
            tipo_carga,
            campo_delta,
            ultima_fecha_delta,
            activo,
            orden_ejecucion
        FROM meta.pipeline_config
        WHERE activo = TRUE
          AND esquema_destino = 'bronze'
        ORDER BY orden_ejecucion;
    """
    return pd.read_sql(query, engine)


def registrar_log_bd(
    nombre_tabla: str,
    capa: str,
    tipo_carga: str,
    estado: str,
    registros_leidos: int = 0,
    registros_insertados: int = 0,
    registros_actualizados: int = 0,
    registros_duplicados: int = 0,
    mensaje_error: str | None = None,
):
    """
    Inserta registro de auditoría en meta.pipeline_run_log.
    """
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO meta.pipeline_run_log (
                    nombre_tabla,
                    capa,
                    tipo_carga,
                    estado,
                    fecha_inicio,
                    fecha_fin,
                    registros_leidos,
                    registros_insertados,
                    registros_actualizados,
                    registros_duplicados,
                    mensaje_error
                )
                VALUES (
                    :nombre_tabla,
                    :capa,
                    :tipo_carga,
                    :estado,
                    NOW(),
                    NOW(),
                    :registros_leidos,
                    :registros_insertados,
                    :registros_actualizados,
                    :registros_duplicados,
                    :mensaje_error
                );
                """
            ),
            {
                "nombre_tabla": nombre_tabla,
                "capa": capa,
                "tipo_carga": tipo_carga,
                "estado": estado,
                "registros_leidos": registros_leidos,
                "registros_insertados": registros_insertados,
                "registros_actualizados": registros_actualizados,
                "registros_duplicados": registros_duplicados,
                "mensaje_error": mensaje_error,
            },
        )


def registrar_error_bd(nombre_tabla: str, capa: str, mensaje_error: str):
    """
    Inserta errores generales en meta.pipeline_error_log.
    """
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO meta.pipeline_error_log (
                    nombre_tabla,
                    capa,
                    registro_json,
                    mensaje_error,
                    fecha_error
                )
                VALUES (
                    :nombre_tabla,
                    :capa,
                    NULL,
                    :mensaje_error,
                    NOW()
                );
                """
            ),
            {
                "nombre_tabla": nombre_tabla,
                "capa": capa,
                "mensaje_error": mensaje_error,
            },
        )


def obtener_columnas_bronze(nombre_tabla: str) -> list[str]:
    """
    Obtiene columnas reales de la tabla Bronze en Supabase.
    """
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'bronze'
          AND table_name = :nombre_tabla
        ORDER BY ordinal_position;
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), {"nombre_tabla": nombre_tabla})
        return [row[0] for row in result.fetchall()]


def normalizar_columnas_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza cabeceras del CSV:
    - espacios por guion bajo
    - minúsculas
    - quita caracteres simples problemáticos
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace("á", "a", regex=False)
        .str.replace("é", "e", regex=False)
        .str.replace("í", "i", regex=False)
        .str.replace("ó", "o", regex=False)
        .str.replace("ú", "u", regex=False)
    )
    return df


def cargar_tabla_bronze(config: pd.Series):
    nombre_tabla = config["nombre_tabla"]
    ruta_archivo = config["ruta_archivo"]
    tipo_carga = config["tipo_carga"]
    campo_delta = config["campo_delta"]
    ultima_fecha_delta = config["ultima_fecha_delta"]

    logger.info(f"Inicio carga Bronze | tabla={nombre_tabla} | tipo={tipo_carga}")

    archivo = Path(ruta_archivo)

    if not archivo.exists():
        mensaje = f"No existe el archivo: {ruta_archivo}"
        logger.error(mensaje)
        registrar_log_bd(
            nombre_tabla=nombre_tabla,
            capa="bronze",
            tipo_carga=tipo_carga,
            estado="ERROR",
            mensaje_error=mensaje,
        )
        registrar_error_bd(nombre_tabla, "bronze", mensaje)
        return

    try:
        df = pd.read_csv(archivo, dtype=str, encoding="utf-8-sig")
        df = normalizar_columnas_csv(df)

        registros_leidos = len(df)

        if registros_leidos == 0:
            logger.warning(f"Archivo vacío: {ruta_archivo}")
            registrar_log_bd(
                nombre_tabla=nombre_tabla,
                capa="bronze",
                tipo_carga=tipo_carga,
                estado="EXITOSO",
                registros_leidos=0,
                registros_insertados=0,
            )
            return

        # Aplicar DELTA si corresponde
        if tipo_carga == "DELTA" and pd.notna(campo_delta) and campo_delta in df.columns:
            df[campo_delta] = pd.to_datetime(df[campo_delta], errors="coerce")

            if pd.notna(ultima_fecha_delta):
                ultima_fecha_delta = pd.to_datetime(ultima_fecha_delta)
                df = df[df[campo_delta] > ultima_fecha_delta]

            # Volver a texto para Bronze
            df[campo_delta] = df[campo_delta].dt.strftime("%Y-%m-%d %H:%M:%S")

        registros_post_delta = len(df)

        if registros_post_delta == 0:
            logger.info(f"Sin registros nuevos para {nombre_tabla}")
            registrar_log_bd(
                nombre_tabla=nombre_tabla,
                capa="bronze",
                tipo_carga=tipo_carga,
                estado="EXITOSO",
                registros_leidos=registros_leidos,
                registros_insertados=0,
            )
            return

        columnas_bronze = obtener_columnas_bronze(nombre_tabla)
        columnas_negocio = [col for col in columnas_bronze if col not in AUDIT_COLUMNS]

        # Mantener solo columnas que existen en Bronze.
        columnas_presentes = [col for col in columnas_negocio if col in df.columns]
        df = df[columnas_presentes].copy()

        # Agregar columnas faltantes de negocio como None
        for col in columnas_negocio:
            if col not in df.columns:
                df[col] = None

        df = df[columnas_negocio]

        batch_id = str(uuid.uuid4())
        fecha_carga = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        df["etl_batch_id"] = batch_id
        df["etl_fecha_carga"] = fecha_carga
        df["etl_archivo_origen"] = str(ruta_archivo)
        df["etl_hash_registro"] = df.apply(calcular_hash_fila, axis=1)
        df["etl_usuario"] = "python_pipeline"

        df = df[columnas_bronze]

        # FULL: limpia tabla antes de cargar.
        if tipo_carga == "FULL":
            with engine.begin() as conn:
                conn.execute(text(f"TRUNCATE TABLE bronze.{nombre_tabla};"))

        df.to_sql(
            nombre_tabla,
            engine,
            schema="bronze",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000,
        )

        # Actualizar watermark DELTA
        if tipo_carga == "DELTA" and pd.notna(campo_delta) and campo_delta in df.columns:
            nueva_fecha = pd.to_datetime(df[campo_delta], errors="coerce").max()
            if pd.notna(nueva_fecha):
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            UPDATE meta.pipeline_config
                            SET ultima_fecha_delta = :nueva_fecha,
                                actualizado_en = NOW()
                            WHERE nombre_tabla = :nombre_tabla;
                            """
                        ),
                        {
                            "nueva_fecha": nueva_fecha.to_pydatetime(),
                            "nombre_tabla": nombre_tabla,
                        },
                    )

        logger.info(
            f"Carga exitosa | tabla={nombre_tabla} | leídos={registros_leidos} | insertados={len(df)}"
        )

        registrar_log_bd(
            nombre_tabla=nombre_tabla,
            capa="bronze",
            tipo_carga=tipo_carga,
            estado="EXITOSO",
            registros_leidos=registros_leidos,
            registros_insertados=len(df),
        )

    except Exception as e:
        mensaje = str(e)
        logger.error(f"Error cargando {nombre_tabla}: {mensaje}")

        registrar_log_bd(
            nombre_tabla=nombre_tabla,
            capa="bronze",
            tipo_carga=tipo_carga,
            estado="ERROR",
            mensaje_error=mensaje,
        )
        registrar_error_bd(nombre_tabla, "bronze", mensaje)


def main():
    logger.info("==================================================")
    logger.info("INICIO PIPELINE DE INGESTA BRONZE")
    logger.info("==================================================")

    config_df = leer_configuracion_pipeline()

    if config_df.empty:
        logger.warning("No hay tablas activas configuradas en meta.pipeline_config")
        return

    for _, config in config_df.iterrows():
        cargar_tabla_bronze(config)

    logger.info("==================================================")
    logger.info("FIN PIPELINE DE INGESTA BRONZE")
    logger.info("==================================================")


if __name__ == "__main__":
    main()
