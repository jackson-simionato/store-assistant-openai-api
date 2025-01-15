from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import carrega
from selecionar_persona import get_persona
from selecionar_documento import get_documento
from ecomart_assistant import create_thread, create_assistant, get_assistant_json

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"

app = Flask(__name__)
app.secret_key = 'alura'

assistant_json = get_assistant_json()
thread_id = assistant_json['thread_id']
assistant_id = assistant_json['assistant_id']
files_ids = assistant_json['file_ids']
vector_store_id = assistant_json['vector_store_id']

def bot(user_prompt):
    maximo_tentativas = 1

    for tentativa in range(maximo_tentativas):
        try:
            cliente.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_prompt
            )

            run = cliente.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            while run.status !=  'completed':
                run = cliente.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

            message_history = list(cliente.beta.threads.messages.list(thread_id=thread_id).data)
            response = message_history[0]
            return response
        except Exception as erro:
            if tentativa == maximo_tentativas - 1:
                    return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)

@app.route('/chat', methods=['POST'])
def chat():
    user_prompt = request.json['msg']
    response = bot(user_prompt)
    response_text = response.content[0].text.value
    return response_text

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
