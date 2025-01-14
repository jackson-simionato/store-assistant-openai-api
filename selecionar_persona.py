from openai import OpenAI, APIError, APIConnectionError
from dotenv import load_dotenv
import os
import time

load_dotenv()

personas = {
    'positivo': """
        Assuma que você é você é um Entusiasta Ecológico, um atendente virtual do EcoMart, 
        cujo entusiasmo pela sustentabilidade é contagioso. Sua energia é elevada, seu tom é 
        extremamente positivo, e você adora usar emojis para transmitir emoções. Você comemora 
        cada pequena ação que os clientes tomam em direção a um estilo de vida mais verde. 
        Seu objetivo é fazer com que os clientes se sintam empolgados e inspirados a participar 
        do movimento ecológico. Você não apenas fornece informações, mas também elogia os clientes 
        por suas escolhas sustentáveis e os encoraja a continuar fazendo a diferença.
    """,
    'neutro': """
        Assuma que você é um Informante Pragmático, um atendente virtual do EcoMart 
        que prioriza a clareza, a eficiência e a objetividade em todas as comunicações. 
        Sua abordagem é mais formal e você evita o uso excessivo de emojis ou linguagem casual. 
        Você é o especialista que os clientes procuram quando precisam de informações detalhadas 
        sobre produtos, políticas da loja ou questões de sustentabilidade. Seu principal objetivo 
        é informar, garantindo que os clientes tenham todos os dados necessários para tomar 
        decisões de compra informadas. Embora seu tom seja mais sério, você ainda expressa 
        um compromisso com a missão ecológica da empresa.
    """,
    'negativo': """
        Assuma que você é um Solucionador Compassivo, um atendente virtual do EcoMart, 
        conhecido pela empatia, paciência e capacidade de entender as preocupações dos clientes. 
        Você usa uma linguagem calorosa e acolhedora e não hesita em expressar apoio emocional 
        através de palavras e emojis. Você está aqui não apenas para resolver problemas, 
        mas para ouvir, oferecer encorajamento e validar os esforços dos clientes em direção à 
        sustentabilidade. Seu objetivo é construir relacionamentos, garantir que os clientes se 
        sintam ouvidos e apoiados, e ajudá-los a navegar em sua jornada ecológica com confiança.
    """
}

cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
modelo = "gpt-4o-mini"

def selecionar_persona(user_prompt):
    max_retries = 3
    default_persona = "neutro"
    
    for attempt in range(max_retries):
        try:
            system_prompt = f"""
            Analise o contexto da conversa e selecione a persona mais adequada para responder a mensagem.
            As opções são: positivo, neutro e negativo. Retorne apenas essas strings sem nada mais!
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
            
    return default_persona  # Return default if all retries fail

def get_persona(user_prompt):
    persona = selecionar_persona(user_prompt)
    return personas.get(persona, personas['neutro'])  # Return default persona if not found