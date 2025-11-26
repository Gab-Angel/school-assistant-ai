from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from postgres.conection_postgres import get_conn


def get_historico(numero: str):
    conn = get_conn()

    try:
        cur = conn.execute("""
            SELECT message 
            FROM chat_ia
            WHERE session_id = %s
            ORDER BY id ASC
            LIMIT 20
        """, (numero,))

        rows = cur.fetchall()
        historico = []

        for row in rows:
            msg = row["message"]

            if msg["type"] == "human":
                historico.append(HumanMessage(content=msg["content"]))

            elif msg["type"] == "ai":
                historico.append(AIMessage(content=msg["content"]))

            elif msg["type"] == "tool":
                historico.append(ToolMessage(content=msg["content"]))

        return historico

    except Exception as e:
        print(f"❌ Erro ao recuperar histórico: {e}")
        return []

    finally:
        conn.close()