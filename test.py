import google.generativeai as genai

# Your NEW API key
API_KEY = "AIzaSyCVeKcJqXR5K2aGkVO1QVXSjrjn8Xgasdc"

genai.configure(api_key=API_KEY)

# Test with CORRECT model name
model_name = 'models/gemini-2.0-flash'
print(f"Testing: {model_name}")

try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("What is 2+2?")
    print(f"✅ SUCCESS!")
    print(f"Response: {response.text}")
    
    # Test conversation
    print(f"\n🤖 Conversation test:")
    response = model.generate_content("Hello! How are you?")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    
    # Try alternative
    print(f"\nTrying: models/gemini-flash-latest")
    try:
        model = genai.GenerativeModel('models/gemini-flash-latest')
        response = model.generate_content("Hello")
        print(f"✅ Alternative works: {response.text[:50]}...")
    except Exception as e2:
        print(f"❌ Also failed: {e2}")