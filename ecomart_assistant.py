from openai import OpenAI, APIError, APIConnectionError
from dotenv import load_dotenv
import os
import time
from helpers import carrega
from selecionar_persona import personas

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"
contexto = carrega('dados/ecomart.txt')

def create_thread():
    return cliente.beta.threads.create()

def create_assistant():
    assistant = cliente.beta.assistants.create(
        name="Atendende Ecomart",
        instructions=f"""
        Você é um chatbot de atendimento a clientes de um e-commerce. Você não deve responder perguntas que não sejam referentes aos dados do e-commerce informado!
        Seja conciso, dê respostas claras e objetivas. 
        Utilize o contexto e personas abaixo para gerar as respostas.

        ## Contexto: {contexto}

        ## Persona: {personas['neutro']}
        """,
        model=modelo
    )

    return assistant