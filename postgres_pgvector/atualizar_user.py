from postgres_pgvector.conection_pgvector import get_vector_conn


def atualizar_user(
    numero: str,
    nome: str | None,
    tipo_usuario: str | None,
    turma_serie: str | None
):
    conn = get_vector_conn()
    cursor = conn.cursor()  # ← adicionar cursor

    try:
        cursor.execute("""
            UPDATE users
            SET 
                nome = COALESCE(%s, nome),
                tipo_usuario = COALESCE(%s, tipo_usuario),
                turma_serie = COALESCE(%s, turma_serie),
                updated_at = NOW()
            WHERE numero = %s
        """, (nome, tipo_usuario, turma_serie, numero))

        conn.commit()
        print(f"🔄 Usuário {numero} atualizado com sucesso")

    except Exception as e:
        print(f"❌ Erro ao atualizar usuário: {e}")

    finally:
        cursor.close()  # ← fechar cursor
        conn.close()