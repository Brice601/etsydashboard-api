"""
Configuration de l'application
Gestion des variables d'environnement et settings globaux
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Configuration globale de l'API"""
    
    # Environnement
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "dev-secret-key-change-in-prod")
    API_KEY: str = os.getenv("API_KEY", "dev-api-key")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-prod")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8501",  # Streamlit local
        "https://etsydashboard.streamlit.app",  # Production
        "https://etsydashboard.com",  # Custom domain si configuré
    ]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Stripe (pour Phase 3)
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Anthropic (pour Premium features Phase 3)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instance globale des settings
settings = Settings()

# Validation au démarrage
def validate_settings():
    """Valide que les settings critiques sont configurés"""
    critical_settings = [
        ("SUPABASE_URL", settings.SUPABASE_URL),
        ("SUPABASE_KEY", settings.SUPABASE_KEY),
    ]
    
    missing = [name for name, value in critical_settings if not value]
    
    if missing and settings.ENVIRONMENT == "production":
        raise ValueError(f"Missing critical settings in production: {', '.join(missing)}")
    
    if missing and settings.DEBUG:
        print(f"⚠️  Warning: Missing settings (OK in dev): {', '.join(missing)}")

# Valider au chargement du module
validate_settings()
