from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Optional
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain.tools import tool
from agent_assistant.integrations import llm_groq, url, headers
from postgres_pgvector.criar_user import salvar_user
from postgres_pgvector.chat_ia import salvar_mensagem
from postgres_pgvector.verificar_user import usuario_existe
from postgres_pgvector.atualizar_user import atualizar_user
from evolution.sender_message import enviar_texto, fatiar_texto
from postgres_pgvector.get_historico import get_historico
from agent_assistant.agent_base import agente_base
from rag.busca_semantica import buscar_contexto_similar, formatar_contexto
import os

prompt_ia = ""

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_PATH, "prompt_ai.txt")

with open(PROMPT_PATH, "r", encoding="utf-8") as file:
    prompt_ia = file.read()

# Variável global para armazenar o número atual
current_numero = None


@tool(description="""
      Use essa tool para buscar informações relevantes no banco de conhecimento da escola usando busca semântica. 
      Retorna os textos mais relacionados à pergunta do usuário.
      Use esta ferramenta quando a pessoa pedir informações relacionadas à categoria:

    - sobre_escola  
      
      Parametros para preencher:
      pergunta: a pergunta do usuário
      categoria: a categoria relacionada a pergunta do user (sobre_escola)
      """)
def tool_buscar_info(pergunta: str, categoria: str = 'sobre_escola') -> str:
    
    print(f"Pergunta: {pergunta}")
    print(f"Categoria: {categoria}")
    
    resultados = buscar_contexto_similar(
        pergunta=pergunta,
        categoria=categoria,
        limite=3,
        similaridade_minima=0.65
    )
    
    return formatar_contexto(resultados)

@tool(description="""

""")
def tool_buscar_arquivo():
    return

@tool(description="""
Atualiza os dados cadastrais do usuário no sistema da escola.

QUANDO USAR:
- Apenas após coletar TODAS as informações necessárias do usuário na conversa.
- Quando o usuário informar ou corrigir seus dados (nome, tipo, turma).

PARÂMETROS:
- nome: Nome completo do usuário (ex: "Maria Silva")
- tipo_usuario: Deve ser EXATAMENTE um destes valores: "aluno", "responsavel", "professor", "gestor", "funcionario", "outro"
- turma_serie: Turma e série do aluno (ex: "2º Ano A", "3º Ano B"). Use "N/A" se o usuário NÃO for aluno.

IMPORTANTE:
- NÃO chame esta função antes de perguntar e receber o nome do usuário.
- NÃO chame esta função antes de saber o tipo de usuário.
- NÃO chame esta função antes de saber a turma (se for aluno).
- NUNCA use o número de telefone como nome.
- NUNCA escreva a chamada desta função na resposta ao usuário.
""")
def tool_atualizar_user(nome: str, tipo_usuario: str, turma_serie: str) -> str:
    global current_numero
    numero = current_numero

    try:
        atualizar_user(numero, nome, tipo_usuario, turma_serie)
        return f"Dados atualizados com sucesso para o número {numero}."
    except Exception as e:
        print(f"❌ Erro na tool_atualizar_user: {e}")
        return f"Erro ao atualizar dados do usuário: {str(e)}"


tools = [tool_buscar_info, tool_buscar_arquivo, tool_atualizar_user]
tool_node = ToolNode(tools)
llm_com_tools = llm_groq.bind_tools(tools)


class Estado(TypedDict):
    mensagem: Annotated[list, add_messages]
    numero: str
    tipo: str
    prompt: Optional[str]


def node_salvar_usuario(state: Estado):
    numero = state["numero"]

    salvar_user(
        numero=numero,
        nome="user",
        tipo_usuario="indefinido",
        turma_serie=None,
        metadata={}
    )

    return state


def node_salvar_mensagem(state: Estado):
    mensagens = state["mensagem"]
    numero = state["numero"]
    tipo = state["tipo"]

    if mensagens:
        ultima = mensagens[-1]
        conteudo = ultima.content

        message_payload = {
            "type": tipo,
            "content": conteudo
        }

        salvar_mensagem(
            session_id=numero,
            message=message_payload
        )

    return state


def node_verificar_usuario(state):
    numero = state["numero"]

    existe = usuario_existe(numero)  # agora é síncrono

    if existe:
        print(f"✅ Usuário {numero} já existe")
        return "existente"
    else:
        print(f"🆕 Novo Usuário {numero}")
        return "novo"


def node_execute_tools(state: Estado):
    print("🛠️ Executando ferramentas...")
    last_message = state["mensagem"][-1]

    response = tool_node.invoke({"messages": [last_message]})

    for msg in response["messages"]:
        print(f"🔧 Resultado da ferramenta: {msg.content}")

    return {"mensagem": response["messages"]}


def node_enviar_mensagem(state):
    mensagem = state["mensagem"]
    numero = state["numero"]

    ultima_mensagem = mensagem[-1]
    texto = ultima_mensagem.content

    frases = fatiar_texto(texto)

    for frase in frases:
        enviar_texto(numero=numero, texto=frase, url=url, headers=headers)

    return state


def node_usar_tools(state: Estado) -> str:
    last_message = state["mensagem"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("🔍 Decisão: Chamar ferramentas.")
        return "sim"
    else:
        print("✅ Decisão: Finalizar e responder.")
        return "não"


def node_agente_assistente(state: Estado):
    global current_numero
    current_numero = state["numero"]  # seta o número antes de chamar o agente

    return agente_base(
        state=state,
        prompt_ia=prompt_ia,
        llm_model=llm_com_tools,
        get_historico_func=get_historico
    )


def node_salvar_mensagem_ai(state: Estado):
    """Salva a resposta da IA no banco de dados"""
    mensagens = state["mensagem"]
    numero = state["numero"]

    if mensagens:
        ultima = mensagens[-1]
        conteudo = ultima.content

        message_payload = {
            "type": "ai",
            "content": conteudo
        }

        salvar_mensagem(
            session_id=numero,
            message=message_payload
        )

    return state


# ==================== WORKFLOW ====================

workflow = StateGraph(Estado)

workflow.add_node("Verificar_User", lambda state: state)
workflow.add_node("Salvar_User", node_salvar_usuario)
workflow.add_node("Salvar_mensagem_human", node_salvar_mensagem)
workflow.add_node("Agente_Assistente", node_agente_assistente)
workflow.add_node("Execute_tools", node_execute_tools)
workflow.add_node("Enviar_mensagem", node_enviar_mensagem)
workflow.add_node("Salvar_mensagem_ai", node_salvar_mensagem_ai)  # CORRIGIDO

workflow.set_entry_point("Verificar_User")

workflow.add_conditional_edges("Verificar_User", node_verificar_usuario, {
    "novo": "Salvar_User",
    "existente": "Salvar_mensagem_human"
})

workflow.add_edge("Salvar_User", "Salvar_mensagem_human")
workflow.add_edge("Salvar_mensagem_human", "Agente_Assistente")

workflow.add_conditional_edges("Agente_Assistente", node_usar_tools, {
    "sim": "Execute_tools",
    "não": "Enviar_mensagem"
})

workflow.add_edge("Execute_tools", "Agente_Assistente")
workflow.add_edge("Enviar_mensagem", "Salvar_mensagem_ai")
workflow.add_edge("Salvar_mensagem_ai", END)

grafo = workflow.compile()