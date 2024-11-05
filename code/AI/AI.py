import openai
import json

openai.api_key = "YOUR_OPENAI_API_KEY"

def analyze_json_for_security(json_data):
    # Construye el mensaje de entrada para GPT-4
    prompt = f"Analiza el siguiente JSON para identificar posibles fallas de seguridad y haz recomendaciones:\n{json.dumps(json_data)}"

    # Realiza la solicitud a la API de OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # Extrae y devuelve la respuesta de GPT-4
    return response['choices'][0]['message']['content']