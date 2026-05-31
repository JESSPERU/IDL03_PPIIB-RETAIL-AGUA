from utils.logger import get_logger
from load_bronze_delta import main as cargar_bronze
from run_sp import main as ejecutar_transformaciones


logger = get_logger("run_pipeline")


def main():
    logger.info("==================================================")
    logger.info("INICIO PIPELINE MEDALLION COMPLETO")
    logger.info("==================================================")

    logger.info("Paso 1: Ingesta RAW hacia Bronze")
    cargar_bronze()

    logger.info("Paso 2: Transformaciones Bronze → Silver y Silver → Gold")
    ejecutar_transformaciones()

    logger.info("==================================================")
    logger.info("FIN PIPELINE MEDALLION COMPLETO")
    logger.info("==================================================")


if __name__ == "__main__":
    main()
