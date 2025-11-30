from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from postgres_pgvector.conection_pgvector import get_vector_conn


def get_historico(numero: str):
    conn = get_vector_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT message 
            FROM chat_ia
            WHERE session_id = %s
            ORDER BY id ASC
            LIMIT 20
        """, (numero,))

        rows = cursor.fetchall()  
        historico = []

        for row in rows:
            msg = row["message"]

            if msg["type"] == "human":
                historico.append(HumanMessage(content=msg["content"]))

            elif msg["type"] == "ai":
                historico.append(AIMessage(content=msg["content"]))

            elif msg["type"] == "tool":
                historico.append(ToolMessage(
                    content=msg["content"],
                    tool_call_id=msg.get("tool_call_id", "") 
                ))

        return historico

    except Exception as e:
        print(f"❌ Erro ao recuperar histórico: {e}")
        return []

    finally:
        cursor.close() 
        conn.close()