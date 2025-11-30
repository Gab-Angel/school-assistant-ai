from postgres_pgvector.conection_pgvector import get_vector_conn


def usuario_existe(numero: str) -> bool:
    conn = get_vector_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT numero
            FROM users
            WHERE numero = %s
        """, (numero,))

        row = cursor.fetchone()
        return row is not None

    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")
        return False

    finally:
        cursor.close()
        conn.close()