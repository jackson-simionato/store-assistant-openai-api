from openai import OpenAI, APIError, APIConnectionError
from dotenv import load_dotenv
import os
import time
from helpers import carrega

load_dotenv()

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"

politicas = carrega('dados/politicas_ecomart.txt')
produtos = carrega('dados/produtos_ecomart.txt')
dados_basicos = carrega('dados/dados_ecomart.txt')

def selecionar_documento(user_prompt):
    max_retries = 3
    dados_default = "dados_basicos"

    for attempt in range(max_retries):
        try:
            system_prompt = f"""
            A empresa Ecomart possui três documentos principais que você deve consultar antes de responder a mensagem:

            # Documento 1: Informações básicas ({dados_basicos})
            # Documento 2: Políticas da empresa ({politicas})
            # Documento 3: Produtos disponíveis ({produtos})

            Avalie o prompt do usuário e retorne o documento mais adequado para responder a mensagem. Retorne 'dados_basicos', 'politicas' ou 'produtos'. Retorne apenas essas strings sem nada mais!
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
                model=modelo
            )
            return response.choices[0].message.content.lower()
        except APIError as e:
            print(f"OpenAI API Error: {e}")
        except APIConnectionError as e:
            print(f"Network Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(1)  # Wait before retry
    return dados_default

def get_documento(user_prompt):
    documento = selecionar_documento(user_prompt)
    if documento == 'politicas':
        return politicas + '\n' + dados_basicos
    elif documento == 'produtos':
        return produtos + '\n' + dados_basicos
    else:
        return dados_basicos