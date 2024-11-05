import openai

# Define el endpoint local de la API
openai.api_base = "http://localhost:8000/v1"  # Reemplaza con el puerto correcto si es diferente

# Realiza una consulta
response = openai.Completion.create(
    model="Llama-3.2-3B-Instruct",
    prompt="¿Cuál es la capital de Francia?",
    max_tokens=50
)

print(response.choices[0].text.strip())