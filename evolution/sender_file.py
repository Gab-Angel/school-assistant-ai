import requests
from agent_assistant.integrations import url_sendMedia, headers

def enviar_arquivo_whatsapp(numero, mediaType, fileName, media, caption=""):
    payload = {
        "number": numero,
        "mediatype": mediaType,
        "fileName": fileName,
        "media": media,
        "delay": 2000,
        "presence": "composing"
    }

    resposta = requests.post(url_sendMedia, json=payload, headers=headers)
    
    if resposta.status_code not in [200, 201]:
        raise Exception(f"Erro ao enviar arquivo: {resposta.status_code}")

    return resposta.json()