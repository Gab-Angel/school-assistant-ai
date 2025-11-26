import requests

def enviar_texto(numero: str, texto: str, url: str, headers: dict):
    payload = {
        "number": numero,
        "text": texto,
        "delay": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"✅ Mensagem enviada: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

# TEXT_SPLITER

def fatiar_texto(texto: str) -> list[str]:
    texto = texto.replace("\n\n", " ").replace("\n", " ").strip()

    if "." in texto:
        partes = texto.split(".")
    elif "!" in texto:
        partes = texto.split("!")
    else:
        partes = [texto]

    partes = [p.strip() for p in partes if p.strip() != ""]

    return partes

