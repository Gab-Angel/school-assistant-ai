from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq

load_dotenv()

# CONEXÃO COM EVOLUTION
base_url_evo = os.getenv("BASE_URL_EVO")
instance_token = os.getenv("API_KEY_EVO") 
instance_name = os.getenv("INSTANCE_NAME")

url_sendText = f"{base_url_evo}/message/sendText/{instance_name}"
url_sendMedia = f"{base_url_evo}/message/sendMedia/{instance_name}" 
headers = {
    "Content-Type": "application/json",
    "apikey": instance_token
}

# CONEXÃO COM A GROQ 
llm_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="openai/gpt-oss-120b", temperature=0)

# MODELS
# openai/gpt-oss-120b
# llama-3.3-70b-versatile