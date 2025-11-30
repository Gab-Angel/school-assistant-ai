# =================================================
# FUNÇÃO DE SALVAR USUÁRIO
# =================================================

from postgres_pgvector.conection_pgvector import get_vector_conn
import json  


def salvar_user(
    numero: str,
    nome: str,
    tipo_usuario: str,
    turma_serie: str | None = None,
    metadata: dict = None
):
    if metadata is None:
        metadata = {}

    conn = get_vector_conn()
    cursor = conn.cursor()  

    try:
        cursor.execute("""
            INSERT INTO users (numero, nome, tipo_usuario, turma_serie, metadata)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (numero) DO NOTHING
        """, (numero, nome, tipo_usuario, turma_serie, json.dumps(metadata)))  
        conn.commit()
        print(f"✅ Usuário {numero} salvo com sucesso")

    except Exception as e:
        print(f"❌ Erro ao salvar usuário: {e}")

    finally:
        cursor.close()  
        conn.close()