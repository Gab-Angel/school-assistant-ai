from postgres.conection_postgres import get_conn


def limpar_tabelas():
    conn = get_conn()

    try:
        conn.execute("TRUNCATE TABLE chat_ia RESTART IDENTITY")
        conn.execute("TRUNCATE TABLE users CASCADE")
        conn.commit()
        print("✅ Tabelas limpas com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao limpar tabelas: {e}")

    finally:
        conn.close()


if __name__ == "__main__":
    limpar_tabelas()