import json
from flask import Flask,render_template, request, Response
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from helpers import carrega
from selecionar_persona import get_persona
from selecionar_documento import get_documento
from ecomart_assistant import create_thread, create_assistant, get_assistant_json
from tools_ecomart import list_tools, list_functions
import uuid

from vision_ecomart import analyze_image

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o"

app = Flask(__name__)
app.secret_key = 'alura'

assistant_json = get_assistant_json()
thread_id = assistant_json['thread_id']
assistant_id = assistant_json['assistant_id']

# Global variables to control the status of the conversation
STATUS_COMPLETED = 'completed'
STATUS_REQUIRES_ACTION = 'requires_action'
UPLOAD_FOLDER = 'dados/images'
path_image_sent = None

def bot(user_prompt):
    global path_image_sent
    maximo_tentativas = 1

    for tentativa in range(maximo_tentativas):
        try:
             # Check if there's an active run
            active_runs = cliente.beta.threads.runs.list(thread_id=thread_id).data

            if active_runs:
                active_run = active_runs[0]
                print(f"Waiting for active run to complete. Current status: {active_run.status}")
                sleep(1)
                active_run = cliente.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=active_run.id
                )

            personalidade = get_persona(user_prompt)

            cliente.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=f"Assuma de agora em diante a personalidade abaixo e ignore as personalidades anteriores:\n{personalidade}"
            )

            vision_response = ""
            if path_image_sent != None:
                vision_response = analyze_image(path_image_sent)
                vision_response = vision_response + ". Na resposta final ao usuário, interprete a análise da imagem e forneça uma resposta adequada de acordo com o contexto do cliente"
                os.remove(path_image_sent)
                path_image_sent = None
            
            print(vision_response)

            cliente.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_prompt + '\n' + vision_response
            )

            run = cliente.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            while run.status !=  STATUS_COMPLETED:
                run = cliente.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                print(f"Status da conversa: {run.status}")
                sleep(1)

                if run.status == STATUS_REQUIRES_ACTION:
                    print(f"Status da conversa: {run.status}")
                    tools_activated = run.required_action.submit_tool_outputs.tool_calls
                    tools_activated_responses = []

                    for tool in tools_activated:
                        tool_name = tool.function.name
                        selected_function = list_functions[tool_name]
                        function_args = json.loads(tool.function.arguments)
                        print(f"Tool '{tool_name}' activated with arguments: {function_args}")
                        function_response = selected_function(function_args)
                        tools_activated_responses.append({'tool_call_id': tool.id,
                                                        'output': function_response})
                        
                    run = cliente.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tools_activated_responses
                    )

            message_history = list(cliente.beta.threads.messages.list(thread_id=thread_id).data)
            response = message_history[0]
            return response
        except Exception as erro:
            if tentativa == maximo_tentativas - 1:
                    return "Erro no GPT: %s" % erro
            print('Erro de comunicação com OpenAI:', erro)
            sleep(1)

@app.route('/upload_imagem', methods=['POST'])
def upload_imagem():
    global path_image_sent
    if 'imagem' in request.files:
        image = request.files['imagem']

        id_image = str(uuid.uuid4()) + os.path.splitext(image.filename)[1]
        path_image_file = os.path.join(UPLOAD_FOLDER, id_image)
        image.save(path_image_file)
        path_image_sent = path_image_file

        return 'Imagem salva com sucesso', 200 
    return 'Nenhum arquivo enviado!', 400

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
