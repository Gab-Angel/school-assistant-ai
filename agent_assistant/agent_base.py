from langchain_core.messages import SystemMessage


def agente_base(
    state,
    prompt_ia: str,
    llm_model,               # Ex: llm_com_tools
    get_historico_func       # Função de carregar histórico do Postgres
):
    numero = state["numero"]

    # Recupera histórico com função injetada (agora síncrona)
    mensagens_historico = get_historico_func(numero)

    # Junta com mensagens do state (mensagem atual)
    mensagens_historico.extend(state["mensagem"])

    print("🤖 Agente pensando...")

    system_prompt = (
        f"{prompt_ia}\n\n"
        f"IMPORTANTE: O número do usuário é {numero}. "
        f"Use sempre este número ao chamar ferramentas."
    )

    messages = [SystemMessage(content=system_prompt)] + mensagens_historico

    # Chamada do modelo
    response = llm_model.invoke(messages)

    return {
        "mensagem": [response],
        "tipo": "ai"
    }