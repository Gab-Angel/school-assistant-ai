from postgres.conection_postgres import get_conn


def usuario_existe(numero: str) -> bool:
    conn = get_conn()

    try:
        cur = conn.execute("""
            SELECT numero
            FROM users
            WHERE numero = %s
        """, (numero,))

        row = cur.fetchone()
        return row is not None

    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")
        return False

    finally:
        conn.close()