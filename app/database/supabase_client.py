import os
from dotenv import load_dotenv

load_dotenv()

def get_supabase():
    """Simple Supabase client that won't crash"""
    try:
        from supabase import create_client
        
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Supabase credentials missing")
        
        client = create_client(url, key)
        print(f"✅ Supabase connected to: {url[:30]}...")
        return client
        
    except Exception as e:
        print(f"⚠️ Supabase error: {e}")
        raise