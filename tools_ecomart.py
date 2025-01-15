from openai import OpenAI
from dotenv import load_dotenv
import os, json
from helpers import carrega
from selecionar_persona import personas

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"

list_tools = [
    {"type": "file_search"}
]