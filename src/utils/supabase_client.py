"""
Supabase client configuration for blockchain forensics tool.
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        Client: Configured Supabase client
    """
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
    
    if not url or not key:
        raise ValueError("Supabase URL and key must be set in environment variables")
    
    return create_client(url, key)

# Initialize client
supabase: Client = get_supabase_client()