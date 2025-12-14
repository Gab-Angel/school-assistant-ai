from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from langchain_core.messages import HumanMessage
from agent_assistant.main import grafo
from redis_past.buffer_redis import adicionar_ao_buffer, ouvinte_de_expiracao
from agent_assistant.audio_transcription import audio_transcription
import uvicorn
import asyncio
from postgres_pgvector.create_tables_vector import create_tables_pgvector


mensagens_processadas = set()

async def processar_mensagens_agrupadas(numero: str, texto_final: str):
    try:
        hash_mensagem = hash(f"{numero}:{texto_final}")
        
        if hash_mensagem in mensagens_processadas:
            print(f"⚠️ Mensagem duplicada ignorada para {numero}")
            return
        
        mensagens_processadas.add(hash_mensagem)
        
        print(f"📦 Processando buffer para: {numero}")
        print(f"💬 Texto agrupado: {texto_final}")
        
        entrada = {
            "numero": numero,
            "mensagem": [HumanMessage(content=texto_final)],
            "tipo": "human"
        }
        grafo.invoke(entrada)
        
        print(f"✅ Mensagens processadas com sucesso para {numero}")
        
        mensagens_processadas.discard(hash_mensagem)
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagens agrupadas: {e}")
        mensagens_processadas.discard(hash_mensagem)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Inicializando aplicação...")

    # CRIA TABELAS AUTOMATICAMENTE
    create_tables_pgvector()

    print("🟢 Banco pronto!")

    task = asyncio.create_task(
        ouvinte_de_expiracao(processar_mensagens_agrupadas)
    )

    print("✅ Ouvinte iniciado!")
    yield

    print("🛑 Encerrando aplicação...")
    task.cancel()


app = FastAPI(lifespan=lifespan)

async def processar_mensagens_agrupadas(numero: str, texto_final: str):
    try:
        hash_mensagem = hash(f"{numero}:{texto_final}")
        
        if hash_mensagem in mensagens_processadas:
            print(f"⚠️ Mensagem duplicada ignorada para {numero}")
            return
        
        mensagens_processadas.add(hash_mensagem)
        
        print(f"📦 Processando buffer para: {numero}")
        print(f"💬 Texto agrupado: {texto_final}")
        
        entrada = {
            "numero": numero,
            "mensagem": [HumanMessage(content=texto_final)],
            "tipo": "human"
        }
        grafo.invoke(entrada)
        
        print(f"✅ Mensagens processadas com sucesso para {numero}")
        
        mensagens_processadas.discard(hash_mensagem)
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagens agrupadas: {e}")
        mensagens_processadas.discard(hash_mensagem)

@app.post("/webhook")
async def webhook(request: Request):
    try:
        dados = await request.json()
        messageType = dados['data'].get('messageType')
        #print(dados)
        
        if dados:
            if messageType == 'conversation':
                mensagem = dados['data']["message"].get("conversation")
                
            elif messageType == 'audioMessage':
                base64 = dados['data']["message"].get("base64")
                print("Processando Audio...")
                result = audio_transcription(audio_base64=base64)
                mensagem = result["text"]
            else:
                mensagem = None
            
            remoteJid = dados['data']["key"].get("remoteJid")
            """if "@lid" in remoteJid:
                numero = remoteJid
            else:"""
            numero = remoteJid.split('@')[0]
        
            print(f"📲 Mensagem de: {numero}")
            print(f"💬 Conteúdo: {mensagem}")
            
            adicionar_ao_buffer(numero, mensagem)
            print(f"➕ Mensagem adicionada ao buffer para {numero}")
            
            return JSONResponse(
                content={"status": "mensagem adicionada ao buffer"},
                status_code=200
            )
        else:
            print("⚠️ Payload do webhook não continha os dados esperados.")
            return JSONResponse(
                content={"status": "payload invalido"},
                status_code=400
            )
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        raise HTTPException(status_code=500, detail="erro interno")

if __name__ == "__main__":
    print("🌐 Iniciando servidor FastAPI...")
    uvicorn.run(
        "app:app",  
        host="0.0.0.0",
        port=8001,
        reload=True
    )