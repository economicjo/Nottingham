import os
import json
import requests

# Directorio de los JSON
JSON_DIR = "/mnt/c/Users/djbur/Desktop/Nottingham/code/script"
API_URL = "http://127.0.0.1:8000/v1/completions"

# Filtro para archivos JSON de firewall
def is_firewall_json(file_name):
    return "firewall" in file_name.lower() and file_name.endswith('.json')

# Función para dividir un JSON en fragmentos
def split_json(data, chunk_size=512):
    data_str = json.dumps(data)
    tokens = [data_str[i:i + chunk_size] for i in range(0, len(data_str), chunk_size)]
    return tokens

# Función para analizar un fragmento JSON de firewall
def analyze_firewall_chunk(chunk):
    response = requests.post(API_URL, json={
        "model": "gpt2",
        "prompt": f"Analiza el siguiente fragmento de configuración de firewall:\n{chunk}",
        "max_tokens": 100
    })
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al analizar fragmento: {response.text}")
        return None

# Función para analizar un JSON de firewall
def analyze_firewall_json(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)
    
    results = []
    for chunk in split_json(json_data):
        result = analyze_firewall_chunk(chunk)
        if result:
            results.append(result)
    return results

# Procesa todos los JSON de firewall
def process_firewall_jsons():
    final_results = []
    for file_name in os.listdir(JSON_DIR):
        if is_firewall_json(file_name):
            file_path = os.path.join(JSON_DIR, file_name)
            print(f"Analizando {file_path}...")
            analysis_result = analyze_firewall_json(file_path)
            if analysis_result:
                final_results.append({"file": file_name, "analysis": analysis_result})
    return final_results

# Ejecuta el análisis y muestra resultados
if __name__ == "__main__":
    firewall_analysis_results = process_firewall_jsons()
    for result in firewall_analysis_results:
        print(f"Archivo: {result['file']}")
        print("Análisis:", result['analysis'])
        print("-" * 50)