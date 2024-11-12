from transformers import AutoModelForCausalLM, AutoTokenizer

# Especifica el nombre del modelo que deseas descargar.
# Aquí estoy usando "EleutherAI/gpt-j-6B" como ejemplo. Cambia esto si necesitas otro modelo.
model_name = "EleutherAI/gpt-neo-2.7B"

# Descarga el tokenizer y el modelo.
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

print("Modelo y tokenizer descargados y listos para usar.")