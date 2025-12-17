import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """Working Gemini client with CORRECT model"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("❌ GOOGLE_API_KEY missing from .env")
        
        # Clean the key
        api_key = api_key.strip().strip('"').strip("'")
        
        print(f"🔑 Using Gemini key: {api_key[:15]}...")
        
        try:
            # Configure
            genai.configure(api_key=api_key)
            
            # ✅ USE THE WORKING MODEL from your test:
            # 'models/gemini-flash-latest' - THIS ONE WORKS!
            model_name = 'models/gemini-flash-latest'
            
            print(f"📦 Loading model: {model_name}")
            self.model = genai.GenerativeModel(model_name)
            
            # Quick test
            test_response = self.model.generate_content("Say 'API test successful'")
            print(f"✅ {model_name} ready! Test: '{test_response.text}'")
            
        except Exception as e:
            print(f"❌ Model error: {e}")
            raise
    
    async def process_message_stream(self, session_id: str, message: str, websocket):
        """Get REAL Gemini response"""
        print(f"🤖 Gemini processing: '{message}'")
        
        # Send thinking indicator
        await websocket.send_json({
            "type": "system",
            "message": "🤖 Gemini AI is thinking..."
        })
        
        try:
            # Get REAL Gemini response
            response = self.model.generate_content(
                f"""You are a helpful AI assistant. Respond to this user message:
                
                "{message}"
                
                Keep your response concise and helpful.""",
                generation_config={
                    'max_output_tokens': 200,
                    'temperature': 0.7,
                }
            )
            
            ai_text = response.text
            
            # Send the complete response
            await websocket.send_json({
                "type": "ai_message",
                "content": ai_text
            })
            
            await websocket.send_json({
                "type": "ai_message_end"
            })
            
            print(f"✅ REAL Gemini response: '{ai_text[:50]}...'")
            
            # Return True if tool should be called
            tool_keywords = ['calculate', 'math', 'compute', 'solve', '+', '-', '*', '/']
            return any(keyword in message.lower() for keyword in tool_keywords)
            
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            
            # Send fallback response
            fallback = "I'm your AI assistant. (Temporary API limit reached)"
            await websocket.send_json({
                "type": "ai_message",
                "content": fallback
            })
            
            await websocket.send_json({
                "type": "ai_message_end"
            })
            
            return False