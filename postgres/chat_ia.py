from postgres.conection_postgres import get_conn
from psycopg.types.json import Json


def salvar_mensagem(session_id: str, message: dict):
    conn = get_conn()

    try:
        conn.execute("""
            INSERT INTO chat_ia (session_id, message)
            VALUES (%s, %s)
        """, (session_id, Json(message)))

        conn.commit()
        print(f"✅ Mensagem salva com sucesso")

    except Exception as e:
        print(f"❌ Erro ao salvar mensagem no banco: {e}")

    finally:
        conn.close()