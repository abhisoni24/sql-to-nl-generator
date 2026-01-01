
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_models():
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: No API key found.")
        return

    client = genai.Client(api_key=api_key)
    
    print("Listing available models...")
    try:
        if hasattr(client.models, 'list'):
             # Pager object
            for m in client.models.list(config={'page_size': 100}):
                print(f"- {m.name}")
                if hasattr(m, 'supported_generation_methods'):
                    print(f"  Supported methods: {m.supported_generation_methods}")
                else:
                    print(f"  (Metadata not fully available: {dir(m)})")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
