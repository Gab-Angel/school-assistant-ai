from postgres_pgvector.conection_pgvector import get_vector_conn

def buscar_arquivo_bd(categoria: str):
    
    try:
        conn = get_vector_conn()
        cursor = conn.cursor()

        query = """
            SELECT categoria, fileName, mediaType, caminho
            FROM arquivos
            WHERE categoria ILIKE %s
            LIMIT 1;
        """

        termo = f"%{categoria}%"
        cursor.execute(query, (termo,)) 
        
        resultado = cursor.fetchone()
        return resultado
        
    finally:
    
        if cursor:
            cursor.close()
        if conn:
            conn.close()