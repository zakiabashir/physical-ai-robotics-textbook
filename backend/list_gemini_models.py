import os
os.environ["GEMINI_API_KEY"] = "AIzaSyD5WImup0-jUECh8F4HJr0VL8-XwWy_v6Q"

import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print("Available Gemini Models:")
print("=" * 50)

# List all available models
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"Model: {m.name}")
        print(f"Display Name: {m.display_name}")
        print(f"Description: {m.description}")
        print("-" * 50)