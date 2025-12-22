# 🚀 Etsy Dashboard API

API backend privée pour Etsy Dashboard - Calculs financiers, analyses et recommandations IA.

## 📋 Description

Backend FastAPI qui gère :
- ✅ Authentification utilisateurs (JWT)
- ✅ Calculs de frais Etsy et marges
- 🚧 Analyses CSV (finance, customer, SEO)
- 🚧 Recommandations IA Premium
- 🚧 Gestion abonnements Stripe

**Status:** Phase 1 MVP (Semaines 1-2)

## 🏗️ Architecture

```
Frontend (Streamlit) ←→ API (FastAPI) ←→ Database (Supabase)
```

## 🔧 Installation

### 1. Clone et setup

```bash
git clone https://github.com/YOUR_USERNAME/etsydashboard-api.git
cd etsydashboard-api
```

### 2. Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

```bash
cp .env.example .env
# Éditer .env avec vos credentials Supabase
```

**Variables requises:**
- `SUPABASE_URL`: URL de votre projet Supabase
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key (pas anon key)
- `JWT_SECRET`: Secret pour JWT tokens (générer une clé aléatoire)
- `API_SECRET_KEY`: Secret général API

## 🚀 Lancement

### Mode développement

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible sur `http://localhost:8000`

### Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📡 Endpoints disponibles (Phase 1)

### Health Check
```bash
GET /health
```

### Authentication

**Register**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe"
}
```

**Login**
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Get User Info**
```bash
GET /api/auth/users/{user_id}?token={jwt_token}
```

### Fees Calculator

**Calculate Etsy Fees**
```bash
POST /api/calculate-fees
Content-Type: application/json

{
  "sale_price": 29.99,
  "production_cost": 12.0,
  "shipping_cost": 4.0,
  "offsite_ads": false
}
```

**Get Fees Info**
```bash
GET /api/fees/info
```

## 🗄️ Base de données

### Configuration Supabase

L'API utilise ta base de données Supabase **existante** avec la table `customers`.

**Pas besoin de créer de nouvelles tables !** On adapte juste la structure existante.

### Script de migration

Exécute le fichier `supabase_migration.sql` dans ton SQL Editor Supabase :

1. Va sur [supabase.com](https://supabase.com) → Ton projet
2. SQL Editor (menu gauche)
3. Copie-colle le contenu de `supabase_migration.sql`
4. Run

**Ce que fait le script :**
- ✅ Ajoute `password_hash` à la table `customers`
- ✅ Ajoute `is_premium` (optionnel, pour cache)
- ✅ Ajoute `stripe_customer_id` (pour Phase 3)
- ✅ Crée des fonctions SQL pour gérer l'usage
- ✅ Crée les index pour la performance

### Structure finale de `customers`

```
customers
├── id (UUID) ✅ existe
├── email (VARCHAR) ✅ existe
├── shop_name (VARCHAR) ✅ existe → utilisé comme "name" dans API
├── access_key (VARCHAR) ✅ existe → pour Streamlit
├── password_hash (VARCHAR) 🆕 ajouté → pour API auth
├── data_consent (BOOLEAN) ✅ existe
├── usage_count (INTEGER) ✅ existe
├── usage_reset_date (TIMESTAMP) ✅ existe
├── is_premium (BOOLEAN) 🆕 ajouté
├── stripe_customer_id (VARCHAR) 🆕 ajouté
├── signup_date (TIMESTAMP) ✅ existe
└── last_login (TIMESTAMP) ✅ existe ou ajouté
```

### Tables liées (déjà existantes)

- `customer_products` → Gère les abonnements (insights, finance, etc.)
- `products` → Liste des produits disponibles
- `training_data` → Données collectées anonymisées

## 🧪 Tests

### Test manuel avec curl

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Calculate fees
curl -X POST http://localhost:8000/api/calculate-fees \
  -H "Content-Type: application/json" \
  -d '{"sale_price":29.99,"production_cost":12.0,"shipping_cost":4.0,"offsite_ads":false}'
```

## 📦 Déploiement

### Railway.app (recommandé)

1. **Créer compte Railway**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialiser projet**
   ```bash
   railway init
   ```

3. **Configurer variables d'environnement**
   - Aller dans Railway Dashboard
   - Settings → Variables
   - Ajouter toutes les variables du `.env`

4. **Déployer**
   ```bash
   railway up
   ```

### Alternative : Render.com

1. Connecter le repo GitHub
2. Configurer les variables d'environnement
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🔐 Sécurité

- ✅ Passwords hashés avec bcrypt (cost factor 12)
- ✅ JWT tokens avec expiration (24h)
- ✅ CORS configuré (whitelist seulement)
- ✅ Input validation (Pydantic)
- ✅ Rate limiting (à implémenter Phase 4)

## 📈 Roadmap

### ✅ Phase 1 : MVP (Semaines 1-2)
- [x] Setup FastAPI + Supabase
- [x] Endpoints auth (signup, login)
- [x] Endpoint calculate-fees
- [ ] Analyse basique CSV (finance)
- [ ] Déploiement Railway

### 🚧 Phase 2 : Dashboards (Semaines 3-4)
- [ ] Analyse customer intelligence
- [ ] Scoring SEO
- [ ] Endpoints dashboard data
- [ ] Gestion usage (10/week limit)

### 🔜 Phase 3 : Premium (Semaines 5-6)
- [ ] Intégration Stripe
- [ ] Webhooks subscription
- [ ] Recommandations IA (Claude API)
- [ ] Tests end-to-end

### 🔮 Phase 4 : Optimisation (Semaines 7-8)
- [ ] Caching Redis
- [ ] Rate limiting
- [ ] Tests unitaires
- [ ] Documentation API complète

## 📝 Notes de développement

- **Logging**: Tous les requests sont loggés avec temps de réponse
- **Error handling**: Global exception handler configuré
- **Documentation**: Auto-générée par FastAPI (Swagger)
- **Type checking**: Pydantic pour validation des données

## 🤝 Contribution

Ce repo est privé - Développement interne uniquement.

## 📧 Contact

Pour questions techniques : [votre email]

---

**Version:** 1.0.0  
**Dernière MAJ:** 19 décembre 2024
