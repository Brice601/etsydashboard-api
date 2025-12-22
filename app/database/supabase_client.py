"""
Client Supabase
Gestion de la connexion à la base de données Supabase
"""
from supabase import create_client, Client
from app.config import settings
from typing import Optional

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Retourne une instance du client Supabase (singleton)
    
    Returns:
        Client Supabase configuré
    
    Raises:
        ValueError: Si les credentials Supabase ne sont pas configurés
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
            )
        
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
    
    return _supabase_client

def test_connection() -> bool:
    """
    Test la connexion à Supabase
    
    Returns:
        True si connexion réussie, False sinon
    """
    try:
        client = get_supabase_client()
        # Test simple : récupérer la liste des tables
        result = client.table('users').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection test failed: {e}")
        return False
