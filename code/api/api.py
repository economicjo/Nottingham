from fastapi import FastAPI, UploadFile, File, HTTPException
import json
import requests

app = FastAPI()

# Función para enviar la consulta a LlamaGPT
def call_llama_gpt(firewall_data):
    # Formatea la pregunta para LlamaGPT
    question = f"Analyze the following firewall configuration for vulnerabilities: {firewall_data}"

    # Envía la solicitud a LlamaGPT en el endpoint OpenAI-compatible
    response = requests.post(
        "http://localhost:3001/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": "gpt-3.5-turbo",  # Usar el modelo correcto disponible en LlamaGPT
            "messages": [{"role": "user", "content": question}],
        }
    )
    
    # Verifica que la solicitud fue exitosa
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise HTTPException(status_code=500, detail="Error connecting to LlamaGPT")

# Endpoint para recibir el JSON y analizarlo con LlamaGPT
@app.post("/analyze_vulnerability")
async def analyze_vulnerability(file: UploadFile = File(...)):
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Please upload a JSON file.")

    # Leer el contenido del archivo JSON
    content = await file.read()
    try:
        firewall_config = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")

    # Enviar la configuración a LlamaGPT y recibir el análisis
    analysis_result = call_llama_gpt(firewall_config)
    
    return {"analysis": analysis_result}