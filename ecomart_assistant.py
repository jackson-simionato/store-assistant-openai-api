from openai import OpenAI, APIError, APIConnectionError
from dotenv import load_dotenv
import os, json
from helpers import carrega
from selecionar_persona import personas

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"
contexto = carrega('dados/ecomart.txt')

def create_ids_list():
    file_paths = [f'dados/{file}' for file in os.listdir('dados') if file.endswith('ecomart.txt') and file != 'ecomart.txt']

    files_ids = []

    for file_path in file_paths:
        file = cliente.files.create(
            file=open(file_path, 'rb'),
            purpose='assistants'
        )

        files_ids.append(file.id)

    return files_ids

def create_vector_store(files_ids):
    vector_store = cliente.beta.vector_stores.create(
        name="Ecomart Documentation",
        file_ids=files_ids
    )

    return vector_store

def create_assistant_json(fname='assistants.json'):
    thread_id = create_thread().id
    file_ids = create_ids_list()
    vector_store_id = create_vector_store(file_ids).id
    assistant_id = create_assistant(vector_store_id).id

    json_data = {
        "assistant_id": assistant_id,
        "thread_id": thread_id,
        "file_ids": file_ids,
        "vector_store_id": vector_store_id
    }

    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
        print(f"Arquivo {fname} criado com sucesso!")

def get_assistant_json(fname='assistants.json'):
    if not os.path.exists(fname):
        create_assistant_json(fname)

    try:
        with open(fname, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo {fname} não encontrado!")
        return None

def create_thread():
    return cliente.beta.threads.create()

def create_assistant(vector_store_id):
    """
    Create an OpenAI assistant with file retrieval capability.
    
    Args:
        file_ids (list): List of file IDs to attach to assistant.
    
    Returns:
        Assistant object or None if creation fails.
    """
    try:
        assistant = cliente.beta.assistants.create(
            name="Atendente Ecomart",
            instructions="""
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam referentes aos dados do e-commerce informado!
            Seja conciso, dê respostas claras e objetivas. 
            Além disso, acesse os arquivos associados a você e a thread para responder as perguntas.
            """,
            model=modelo,
            tools=[{"type": "file_search"}],  # Correct tools format
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
        )
        print(f"Assistant created successfully with ID: {assistant.id}")
        return assistant
        
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None