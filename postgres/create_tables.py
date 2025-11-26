from postgres.conection_postgres import get_conn


def create_tables():
    conn = get_conn()

    sql = """
    CREATE TABLE IF NOT EXISTS users (
        numero VARCHAR(20) PRIMARY KEY,
        nome VARCHAR(200),
        tipo_usuario VARCHAR(20),
        turma_serie VARCHAR(50),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS chat_ia (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(20),
        message JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS faq_escola (
        id SERIAL PRIMARY KEY,
        categoria VARCHAR(50) NOT NULL,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        ativo BOOLEAN DEFAULT TRUE,
        criado_em TIMESTAMP DEFAULT NOW(),
        atualizado_em TIMESTAMP DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_faq_categoria ON faq_escola(categoria);
    CREATE INDEX IF NOT EXISTS idx_faq_ativo ON faq_escola(ativo);
    """

    try:
        conn.execute(sql)
        conn.commit()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_tables()