import logging
from pathlib import Path
from datetime import datetime


def get_logger(nombre_logger: str = "medallion_pipeline"):
    """
    Crea un logger para registrar la ejecución del pipeline.
    Genera archivo .log dentro de la carpeta logs/.
    """

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    fecha_actual = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"pipeline_{fecha_actual}.log"

    logger = logging.getLogger(nombre_logger)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formato)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formato)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
