from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

print("Available Gemini models:")
print("="*60)
for model in client.models.list():
    if 'gemini' in model.name.lower() and 'generateContent' in str(model.supported_generation_methods):
        print(f"  - {model.name}")
