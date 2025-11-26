# =================================================
# FUNÇÃO DE SALVAR USUÁRIO
# =================================================

from postgres.conection_postgres import get_conn
from psycopg.types.json import Json


def salvar_user(
    numero: str,
    nome: str,
    tipo_usuario: str,
    turma_serie: str | None = None,
    metadata: dict = None
):
    if metadata is None:
        metadata = {}

    conn = get_conn()

    try:
        conn.execute("""
            INSERT INTO users (numero, nome, tipo_usuario, turma_serie, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (numero) DO NOTHING
        """, (numero, nome, tipo_usuario, turma_serie, Json(metadata)))

        conn.commit()
        print(f"✅ Usuário {numero} salvo com sucesso")

    except Exception as e:
        print(f"❌ Erro ao salvar usuário: {e}")

    finally:
        
        conn.close()