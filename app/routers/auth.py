"""
Router d'authentification
Gestion signup, login, et gestion des utilisateurs
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from app.config import settings
from app.database.supabase_client import get_supabase_client

router = APIRouter()

# Configuration password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemas Pydantic
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: Optional[str]
    is_premium: bool
    access_token: str

class UserInfo(BaseModel):
    user_id: str
    email: str
    name: Optional[str]
    is_premium: bool
    analyses_this_week: int
    analyses_limit: int
    created_at: str

# Fonctions utilitaires
def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str, email: str) -> str:
    """Crée un JWT token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Vérifie et décode un JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """
    Inscription d'un nouvel utilisateur
    
    - **email**: Email valide
    - **password**: Mot de passe (min 8 caractères recommandé)
    - **name**: Nom optionnel
    """
    supabase = get_supabase_client()
    
    # Vérifier si email existe déjà
    existing = supabase.table('customers').select('email').eq('email', user.email.lower()).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(user.password)
    
    # Générer access_key
    import uuid
    import hashlib
    access_key = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    # Créer customer dans Supabase
    new_customer = {
        "email": user.email.lower(),
        "password_hash": password_hash,
        "shop_name": user.name,  # Utiliser name comme shop_name
        "access_key": access_key,
        "data_consent": True,
        "consent_updated_at": datetime.utcnow().isoformat(),
        "signup_date": datetime.utcnow().isoformat(),
        "usage_count": 0,
        "usage_reset_date": datetime.utcnow().isoformat(),
        "is_premium": False,
        "is_email_verified": False
    }
    
    result = supabase.table('customers').insert(new_customer).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    customer_data = result.data[0]
    customer_id = customer_data['id']
    
    # Générer token
    access_token = create_access_token(customer_id, user.email.lower())
    
    return UserResponse(
        user_id=customer_id,
        email=user.email.lower(),
        name=user.name,
        is_premium=False,
        access_token=access_token
    )

@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin):
    """
    Connexion utilisateur
    
    - **email**: Email du compte
    - **password**: Mot de passe
    """
    supabase = get_supabase_client()
    
    # Récupérer customer
    result = supabase.table('customers').select('*').eq('email', credentials.email.lower()).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    customer = result.data[0]
    
    # Vérifier password
    if not verify_password(credentials.password, customer['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Mettre à jour last_login
    try:
        supabase.table('customers').update({
            'last_login': datetime.utcnow().isoformat()
        }).eq('id', customer['id']).execute()
    except:
        pass
    
    # Générer token
    access_token = create_access_token(customer['id'], customer['email'])
    
    return UserResponse(
        user_id=customer['id'],
        email=customer['email'],
        name=customer.get('shop_name'),
        is_premium=customer.get('is_premium', False),
        access_token=access_token
    )

@router.get("/users/{user_id}", response_model=UserInfo)
async def get_user_info(user_id: str, token: str):
    """
    Récupère les informations d'un utilisateur
    
    - **user_id**: ID de l'utilisateur
    - **token**: JWT token (via query param ou Authorization header)
    """
    # Vérifier token
    payload = verify_token(token)
    
    if payload['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    
    supabase = get_supabase_client()
    
    # Récupérer customer
    customer_result = supabase.table('customers').select('*').eq('id', user_id).execute()
    if not customer_result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    customer = customer_result.data[0]
    
    # Récupérer les produits du customer
    products_result = supabase.table('customer_products') \
        .select('product_id') \
        .eq('customer_id', user_id) \
        .execute()
    
    # Vérifier si a l'abonnement "insights" (Premium)
    has_insights = False
    if products_result.data:
        products = [p['product_id'] for p in products_result.data]
        has_insights = 'insights' in products
    
    # Calculer usage
    usage_count = customer.get('usage_count', 0)
    analyses_limit = 999999 if has_insights else 10
    
    return UserInfo(
        user_id=customer['id'],
        email=customer['email'],
        name=customer.get('shop_name'),
        is_premium=has_insights,
        analyses_this_week=usage_count,
        analyses_limit=analyses_limit,
        created_at=customer.get('signup_date', customer.get('created_at', ''))
    )
