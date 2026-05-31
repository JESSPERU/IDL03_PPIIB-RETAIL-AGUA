import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en el archivo .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10}
)


def get_engine():
    """
    Devuelve el motor de conexión a Supabase/PostgreSQL.
    Esta función será usada por los scripts del pipeline.
    """
    return engine


def test_connection():
    """
    Prueba simple de conexión a Supabase.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();"))
            print("Conexión exitosa a Supabase:", result.scalar())
    except OperationalError as e:
        print("No se pudo conectar a Supabase.")
        print("Revisa DATABASE_URL y usa Transaction Pooler.")
        print(e)


if __name__ == "__main__":
    test_connection()