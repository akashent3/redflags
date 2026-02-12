import os
import google.generativeai as genai

# Ensure your API key is set
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit(1)

genai.configure(api_key=api_key)

print("Fetching available models...\n")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error fetching models: {e}")