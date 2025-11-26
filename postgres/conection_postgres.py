import psycopg
from psycopg.rows import dict_row
import os
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg.connect(
        host=os.getenv("IP_VPS"),
        port=5432,
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
        row_factory=dict_row  # retorna dicts em vez de tuplas
    )