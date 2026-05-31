from pathlib import Path

import pandas as pd

from utils.db import get_engine
from utils.logger import get_logger


logger = get_logger("export_gold")
engine = get_engine()

OUTPUT_DIR = Path("data/gold")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GOLD_TABLES = [
    "dim_producto",
    "dim_tiempo",
    "fact_ventas_diarias",
    "fact_inventario",
    "fact_marketing",
    "ml_dataset",
    "ml_score_input",
    "ml_score_output",
    "ml_feature_importance",
]


def export_table(table_name: str):
    query = f"SELECT * FROM gold.{table_name};"
    df = pd.read_sql(query, engine)

    output_path = OUTPUT_DIR / f"{table_name}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    logger.info(f"Exportado gold.{table_name} → {output_path} | filas={len(df)}")


def main():
    logger.info("==================================================")
    logger.info("INICIO EXPORTACIÓN CAPA GOLD")
    logger.info("==================================================")

    for table in GOLD_TABLES:
        export_table(table)

    logger.info("==================================================")
    logger.info("FIN EXPORTACIÓN CAPA GOLD")
    logger.info("==================================================")


if __name__ == "__main__":
    main()