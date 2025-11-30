from postgres_pgvector.conection_pgvector import get_vector_conn


def limpar_tabelas():
    conn = get_vector_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("TRUNCATE TABLE chat_ia RESTART IDENTITY")
        cursor.execute("TRUNCATE TABLE users CASCADE")
       # cursor.execute("TRUNCATE TABLE rag_embeddings RESTART IDENTITY")  # ← adicionar
        conn.commit()
        print("✅ Tabelas limpas com sucesso!")

    except Exception as e:
        conn.rollback()  # ← boa prática adicionar rollback
        print(f"❌ Erro ao limpar tabelas: {e}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    confirmacao = input("⚠️  Tem certeza que deseja limpar TODAS as tabelas? (sim/não): ")
    
    if confirmacao.lower() == "sim":
        limpar_tabelas()
    else:
        print("❌ Operação cancelada.")