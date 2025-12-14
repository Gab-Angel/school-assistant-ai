import redis
import json
import asyncio
from typing import Callable, Awaitable
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configurações ---
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"), 
    port=6379, 
    password=os.getenv("SENHA_REDIS"), 
    db=0, 
    decode_responses=True
)
BUFFER_TIMEOUT = 5  # segundos

def adicionar_ao_buffer(numero: str, nova_mensagem: str):
    """
    Adiciona uma mensagem ao buffer de um número específico.
    Reinicia o timer de timeout a cada nova mensagem.
    """
    chave_conteudo = f"buffer:content:{numero}"
    chave_gatilho = f"buffer:trigger:{numero}"

    # Pega o buffer atual ou cria um novo
    mensagens_json = redis_client.get(chave_conteudo)
    mensagens = json.loads(mensagens_json) if mensagens_json else []
    
    mensagens.append(nova_mensagem)

    # Salva o conteúdo e reinicia o timer no gatilho
    redis_client.set(chave_conteudo, json.dumps(mensagens))
    redis_client.setex(chave_gatilho, BUFFER_TIMEOUT, 1)

async def ouvinte_de_expiracao(callback: Callable[[str, str], Awaitable[None]]):
    """
    Ouve os eventos de expiração do Redis de forma eficiente.
    Lembre-se de configurar o Redis com: CONFIG SET notify-keyspace-events Ex
    """
    print(">>> Ouvinte de expiração iniciado...")
    pubsub = redis_client.pubsub()
    canal = f"__keyevent@{redis_client.connection_pool.connection_kwargs['db']}__:expired"
    print(f"🔔 Inscrito no canal: {canal}")
    pubsub.subscribe(canal)

    for mensagem in pubsub.listen():
        print(f"📨 Mensagem recebida: {mensagem}")
        
        if mensagem['type'] == 'message' and mensagem['data'].startswith("buffer:trigger:"):
            print(f"✅ Gatilho detectado: {mensagem['data']}")
            # Extrai o número da chave do gatilho que expirou
            numero = mensagem['data'].split(":")[2]
            chave_conteudo = f"buffer:content:{numero}"
            
            # Pega as mensagens agrupadas
            mensagens_json = redis_client.get(chave_conteudo)
            if mensagens_json:
                # Junta tudo em um texto só
                mensagens_lista = json.loads(mensagens_json)
                texto_final = " ".join(filter(None, map(str, mensagens_lista)))
                
                print(f"🔄 Processando para {numero}: {texto_final}")
                # Chama a função principal do seu agente
                await callback(numero, texto_final)
                
                # Limpa o buffer
                redis_client.delete(chave_conteudo)
        
        await asyncio.sleep(0.01)

# Variável global para controlar se o ouvinte já está rodando
_ouvinte_ativo = False

def iniciar_ouvinte_background(callback: Callable[[str, str], Awaitable[None]]):
    """
    Função helper para iniciar o ouvinte em background usando asyncio.
    Previne múltiplas instâncias do ouvinte.
    """
    global _ouvinte_ativo
    
    if _ouvinte_ativo:
        print("⚠️ Ouvinte já está ativo, ignorando nova inicialização")
        return None
    
    def executar_ouvinte():
        global _ouvinte_ativo
        _ouvinte_ativo = True
        try:
            asyncio.run(ouvinte_de_expiracao(callback))
        finally:
            _ouvinte_ativo = False
    
    import threading
    thread = threading.Thread(target=executar_ouvinte, daemon=True)
    thread.start()
    return thread