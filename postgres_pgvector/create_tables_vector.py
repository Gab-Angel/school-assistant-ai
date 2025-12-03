from postgres_pgvector.conection_pgvector import get_vector_conn


def create_tables_pgvector():
    conn = get_vector_conn()
    cursor = conn.cursor()

    sql = """
    -- Ativa extensão pgvector
    CREATE EXTENSION IF NOT EXISTS vector;

    -- =========================
    -- TABELA DE USUÁRIOS
    -- =========================
    CREATE TABLE IF NOT EXISTS users (
        numero VARCHAR(20) PRIMARY KEY,
        nome VARCHAR(200),
        tipo_usuario VARCHAR(20),
        turma_serie VARCHAR(50),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );


    -- =========================
    -- HISTÓRICO DE CHAT
    -- =========================
    CREATE TABLE IF NOT EXISTS chat_ia (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(20),
        message JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );


    -- ============================
    -- TABELA DE EMBEDDINGS (RAG)
    -- ============================
    CREATE TABLE IF NOT EXISTS rag_embeddings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        content TEXT NOT NULL,
        categoria VARCHAR(100),
        embedding VECTOR(768),  -- ajuste conforme o modelo de embedding
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- ============================
    -- ÍNDICE VETORIAL (BUSCA RÁPIDA)
    -- ============================
    CREATE INDEX IF NOT EXISTS rag_embedding_idx
    ON rag_embeddings
    USING hnsw (embedding vector_cosine_ops);

    -- ============================
    -- ÍNDICE PARA FILTRAR POR CATEGORIA
    -- ============================ 
    CREATE INDEX IF NOT EXISTS rag_categoria_idx
    ON rag_embeddings (categoria);

    
    -- ============================
    -- TABELA DE ARQUIVOS (ENVIO POR IA)
    -- ============================
    CREATE TABLE IF NOT EXISTS arquivos (
        id SERIAL PRIMARY KEY,
        categoria VARCHAR(100) NOT NULL,      
        fileName VARCHAR(255) NOT NULL,       
        mediaType VARCHAR(20) NOT NULL,     
        caminho VARCHAR NOT NULL,              

        criado_em TIMESTAMP DEFAULT NOW()
    );

    -- ============================
    -- ÍNDICES PARA PERFORMANCE
    -- ============================
    CREATE INDEX IF NOT EXISTS arquivos_categoria_idx
    ON arquivos (categoria);

    CREATE INDEX IF NOT EXISTS arquivos_mediaType_idx
    ON arquivos (mediaType);

    CREATE INDEX IF NOT EXISTS arquivos_fileName_idx
    ON arquivos (fileName);
    
    """

    try:
        cursor.execute(sql)
        conn.commit()
        print("✅ Tabelas RAG + pgvector + arquivos criadas com sucesso!")
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro ao criar tabelas: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_tables_pgvector()
