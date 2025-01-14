from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import carrega
from selecionar_persona import get_persona
from selecionar_documento import get_documento
from ecomart_assistant import create_thread, create_assistant

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"

app = Flask(__name__)
app.secret_key = 'alura'

assistant = create_assistant()
thread = create_thread()

def bot(user_prompt):
    maximo_tentativas = 1

    for tentativa in range(maximo_tentativas):
        try:
            system_prompt = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce. 
            Você não deve responder perguntas que não sejam dados do e-commerce informado!
            Seja conciso, dê respostas claras e objetivas.
            Utilize o contexto e a personalidade abaixo para gerar as respostas.
            # Contexto: {contexto}

            # Personalidade: {persona}
            """
            response = cliente.chat.completions.create(
                messages=[
                        {
                                "role": "system",
                                "content": system_prompt
                        },
                        {
                                "role": "user",
                                "content": user_prompt
                        }
                ],
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                model = modelo)
            return response.choices[0].message.content
        except Exception as erro:
            if tentativa == maximo_tentativas - 1:
                    return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)

@app.route('/chat', methods=['POST'])
def chat():
    user_prompt = request.json['msg']
    response = bot(user_prompt)
    return response

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True)
