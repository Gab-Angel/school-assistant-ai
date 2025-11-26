from postgres.conection_postgres import get_conn


def atualizar_user(
    numero: str,
    nome: str | None,
    tipo_usuario: str | None,
    turma_serie: str | None
):
    conn = get_conn()

    try:
        conn.execute("""
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
        conn.close()