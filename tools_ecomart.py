from openai import OpenAI
from dotenv import load_dotenv
import os, json
from helpers import carrega
from selecionar_persona import personas

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"

list_tools = [
    {"type": "file_search"},
    {
        "type": "function",
        "function": {
            "name": "validar_codigo_promocional",
            "description": "Valide um código promocional com base nas diretrizes de Descontos e Promoções do EcoMart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string",
                        "description": "O código promocional a ser validado, com sufixo, por exemplo CUPOM_ECO",
                    },
                    "validade": {
                        "type": "string",
                        "description": f"A validade do cupom, caso seja válido e esteja associado às políticas. Formato: DD/MM/AAAA"
                    }
                },
                "required": ["codigo", "validade"]
            }
        }
    }
]
def validar_codigo_promocional(args):
    codigo = args.get('codigo')
    validade = args.get('validade')

    return f"O código promocional {codigo} é válido e expira em {validade}."

list_functions = {
    "validar_codigo_promocional": validar_codigo_promocional
}