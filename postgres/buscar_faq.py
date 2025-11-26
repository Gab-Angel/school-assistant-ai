from postgres.conection_postgres import get_conn

def buscar_faq_no_banco(categoria: str):
    conn = get_conn()

    try:
        cur = conn.execute("""
            SELECT pergunta, resposta 
            FROM faq_escola
            WHERE categoria = %s AND ativo = TRUE
        """, (categoria,))
        
        resultados = cur.fetchall()
        return resultados

    except Exception as e:
        print(f"❌ Erro ao buscar FAQ no banco: {e}")
        raise e

    finally:
        conn.close()
