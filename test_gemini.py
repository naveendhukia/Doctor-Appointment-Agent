import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

print("Finding available Gemini models...")
print("=" * 60)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file!")
    exit(1)

print("✅ API Key found\n")

try:
    client = genai.Client(api_key=api_key)
    
    # List all models
    print("Available models:")
    print("-" * 60)
    
    models = client.models.list()
    
    available_models = []
    for model in models:
        print(f"  • {model.name}")
        available_models.append(model.name)
    
    print("\n" + "=" * 60)
    
    # Try to use the first model that contains 'flash'
    flash_models = [m for m in available_models if 'flash' in m.lower()]
    
    if flash_models:
        test_model = flash_models[0]
        print(f"🧪 Testing with: {test_model}")
        print("-" * 60)
        
        response = client.models.generate_content(
            model=test_model,
            contents='Say "Hello, I am working!"'
        )
        
        print(f"✅ Response: {response.text}")
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS! Use this model name in your agent:")
        print(f"   {test_model}")
        print("=" * 60)
    else:
        print("⚠️  No 'flash' models found. Available models listed above.")
        print("Try using the first model from the list.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTrying simple model names instead...")
    
    # Fallback: try common model names
    models_to_try = [
        'models/gemini-1.5-flash',
        'models/gemini-1.5-flash-latest',
        'models/gemini-1.5-pro',
        'models/gemini-pro',
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
    ]
    
    for model_name in models_to_try:
        try:
            print(f"\n🧪 Trying: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents='Say "Hello, I am working!"'
            )
            print(f"✅ SUCCESS with {model_name}!")
            print(f"Response: {response.text}")
            print(f"\n" + "=" * 60)
            print(f"Use this model: {model_name}")
            print("=" * 60)
            break
        except Exception as e2:
            print(f"❌ Failed: {str(e2)[:100]}")
            continue