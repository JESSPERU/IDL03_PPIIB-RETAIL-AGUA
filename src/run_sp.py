from sqlalchemy import text

from utils.db import get_engine
from utils.logger import get_logger


logger = get_logger("run_sp")
engine = get_engine()


def ejecutar_sp(nombre_sp: str):
    logger.info(f"Ejecutando procedimiento: {nombre_sp}")

    with engine.begin() as conn:
        conn.execute(text(f"CALL {nombre_sp}();"))

    logger.info(f"Procedimiento ejecutado correctamente: {nombre_sp}")


def main():
    ejecutar_sp("silver.sp_bronze_to_silver")
    ejecutar_sp("gold.sp_silver_to_gold")


if __name__ == "__main__":
    main()
