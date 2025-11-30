from postgres_pgvector.conection_pgvector import get_vector_conn
import json


def salvar_mensagem(session_id: str, message: dict):
    conn = get_vector_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO chat_ia (session_id, message)
            VALUES (%s, %s)
        """, (session_id, json.dumps(message)))

        conn.commit()
        print(f"✅ Mensagem salva com sucesso")

    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao salvar mensagem no banco: {e}")

    finally:
        cursor.close()
        conn.close()