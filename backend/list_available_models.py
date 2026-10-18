"""
List available Gemini models for this API key
"""

import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "")

# Test the ListModels endpoint
url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"

print(f"Fetching available models...")
print(f"URL: {url}\n")

try:
    with httpx.Client(timeout=10) as client:
        response = client.get(url)
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("Available Models:")
            print("="*60)
            
            if "models" in data:
                for model in data["models"]:
                    model_name = model.get("name", "Unknown").split("/")[-1]
                    supported_methods = model.get("supportedGenerationMethods", [])
                    print(f"\nModel: {model_name}")
                    print(f"  Full name: {model.get('name')}")
                    print(f"  Display name: {model.get('displayName', 'N/A')}")
                    print(f"  Supported methods: {', '.join(supported_methods)}")
            
            print(f"\n{'='*60}")
            print(f"Total models: {len(data.get('models', []))}")
        else:
            print("Error fetching models:")
            print(response.text)
except Exception as e:
    print(f"Exception: {e}")
