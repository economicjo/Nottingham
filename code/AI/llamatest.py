import os
import json
import webbrowser
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Configura tu API Key de OpenAI
client = OpenAI(api_key="")

# Directorio de los JSON
JSON_DIR = "/mnt/c/Users/djbur/Desktop/Nottingham/code/script"

app = Flask(__name__)

def auto_analyze_all_jsons():
    all_json_data = []
    for file_name in os.listdir(JSON_DIR):
        if file_name.endswith(".json") and "firewall" in file_name.lower():
            file_path = os.path.join(JSON_DIR, file_name)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                all_json_data.append({file_name: json_data})
    
    prompt = "Analiza los siguientes archivos JSON de configuración de firewall y proporciona recomendaciones específicas de seguridad para cada uno:\n\n"
    for json_item in all_json_data:
        for file_name, data in json_item.items():
            prompt += f"Archivo: {file_name}\n{json.dumps(data, indent=2)}\n\n"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    analysis_result = response.choices[0].message.content

    # Formatear en HTML para mejor legibilidad
    formatted_analysis = "<p>" + analysis_result.replace("\n", "</p><p>") + "</p>"
    return {"analysis": formatted_analysis}

# Ruta inicial para mostrar el análisis y la interfaz de chat
@app.route('/')
def index():
    analysis_result = auto_analyze_all_jsons()
    return render_template('chat.html', initial_analysis=analysis_result)

# Ruta para manejar las preguntas de seguimiento en el chat
@app.route('/ask', methods=['POST'])
def ask_question():
    conversation_history = request.json.get("conversation_history")

    # Crear el prompt completo con todo el historial de la conversación
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": conversation_history}
        ],
    )
    answer = response.choices[0].message.content
    return jsonify({"answer": answer})

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=False)