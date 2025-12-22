-- =========================================
-- ADAPTATION SUPABASE POUR API BACKEND
-- =========================================
-- Ce script adapte la table 'customers' existante pour l'API
-- Il n'y a PAS besoin de créer de nouvelles tables

-- =========================================
-- ÉTAPE 1 : Ajouter les colonnes manquantes
-- =========================================

-- Ajouter password_hash pour l'authentification API
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Ajouter is_premium (déjà géré par customer_products mais utile pour cache)
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT false;

-- Ajouter stripe_customer_id pour Phase 3
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255);

-- Ajouter last_login si pas déjà présent
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

-- =========================================
-- ÉTAPE 2 : Vérifier les colonnes existantes
-- =========================================

-- Ces colonnes devraient déjà exister dans ta table customers :
-- ✅ id (UUID)
-- ✅ email (VARCHAR)
-- ✅ shop_name (VARCHAR) → utilisé comme "name" dans l'API
-- ✅ access_key (VARCHAR) → pour Streamlit
-- ✅ data_consent (BOOLEAN)
-- ✅ consent_updated_at (TIMESTAMP)
-- ✅ signup_date (TIMESTAMP)
-- ✅ usage_count (INTEGER)
-- ✅ usage_reset_date (TIMESTAMP)
-- ✅ is_email_verified (BOOLEAN)

-- Vérifier la structure de ta table :
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'customers'
ORDER BY ordinal_position;

-- =========================================
-- ÉTAPE 3 : Index pour performance
-- =========================================

-- Index sur email (devrait déjà exister mais on s'assure)
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);

-- Index sur access_key pour recherches rapides
CREATE INDEX IF NOT EXISTS idx_customers_access_key ON customers(access_key);

-- Index sur password_hash pour authentification
CREATE INDEX IF NOT EXISTS idx_customers_password ON customers(password_hash) WHERE password_hash IS NOT NULL;

-- =========================================
-- ÉTAPE 4 : Fonction helper pour reset usage hebdomadaire
-- =========================================

-- Cette fonction vérifie et reset le compteur usage_count si nécessaire
CREATE OR REPLACE FUNCTION check_and_reset_usage(customer_uuid UUID)
RETURNS TABLE(usage_count INT, usage_limit INT, reset_needed BOOLEAN) AS $$
DECLARE
    current_count INT;
    reset_date TIMESTAMP;
    days_since_reset INT;
    has_insights BOOLEAN;
BEGIN
    -- Récupérer les infos du customer
    SELECT c.usage_count, c.usage_reset_date INTO current_count, reset_date
    FROM customers c
    WHERE c.id = customer_uuid;
    
    -- Vérifier si a l'abonnement insights
    SELECT EXISTS(
        SELECT 1 FROM customer_products 
        WHERE customer_id = customer_uuid AND product_id = 'insights'
    ) INTO has_insights;
    
    -- Si premium, pas de limite
    IF has_insights THEN
        RETURN QUERY SELECT current_count, 999999, false;
        RETURN;
    END IF;
    
    -- Calculer jours depuis reset
    days_since_reset := EXTRACT(DAY FROM NOW() - reset_date);
    
    -- Reset si 7 jours écoulés
    IF days_since_reset >= 7 THEN
        UPDATE customers 
        SET usage_count = 0, usage_reset_date = NOW()
        WHERE id = customer_uuid;
        
        RETURN QUERY SELECT 0, 10, true;
    ELSE
        RETURN QUERY SELECT current_count, 10, false;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =========================================
-- ÉTAPE 5 : Fonction pour incrémenter usage
-- =========================================

-- Fonction appelée après chaque analyse réussie
CREATE OR REPLACE FUNCTION increment_usage(customer_uuid UUID)
RETURNS void AS $$
DECLARE
    has_insights BOOLEAN;
BEGIN
    -- Vérifier si a insights (pas de limite si oui)
    SELECT EXISTS(
        SELECT 1 FROM customer_products 
        WHERE customer_id = customer_uuid AND product_id = 'insights'
    ) INTO has_insights;
    
    -- Ne pas incrémenter si premium
    IF NOT has_insights THEN
        UPDATE customers 
        SET usage_count = usage_count + 1
        WHERE id = customer_uuid;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =========================================
-- ÉTAPE 6 : RLS (Row Level Security) - Optionnel
-- =========================================

-- Si tu veux activer RLS plus tard (Phase 4 sécurité avancée)
-- ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Policy pour que les users ne voient que leurs données
-- CREATE POLICY "Users can view own data" ON customers
--     FOR SELECT USING (auth.uid() = id);

-- CREATE POLICY "Users can update own data" ON customers
--     FOR UPDATE USING (auth.uid() = id);

-- =========================================
-- ÉTAPE 7 : Vérifications finales
-- =========================================

-- Vérifier que tout est OK
SELECT 
    COUNT(*) as total_customers,
    COUNT(password_hash) as with_password,
    COUNT(CASE WHEN is_premium = true THEN 1 END) as premium_count
FROM customers;

-- Vérifier les index
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE tablename = 'customers';

-- =========================================
-- NOTES IMPORTANTES
-- =========================================

-- 1. MIGRATION DES USERS EXISTANTS
-- Les customers existants n'ont pas de password_hash.
-- Ils devront soit :
--   a) Se créer un nouveau compte via l'API (recommandé)
--   b) Utiliser un système de "reset password" (Phase 2)

-- 2. COMPATIBILITÉ STREAMLIT
-- Le frontend Streamlit continue d'utiliser 'access_key'
-- L'API utilise 'password_hash' + JWT tokens
-- Les deux systèmes coexistent sans problème

-- 3. PRODUIT "INSIGHTS"
-- Pour vérifier si un user est Premium, l'API check :
--   SELECT * FROM customer_products 
--   WHERE customer_id = X AND product_id = 'insights'

-- 4. USAGE TRACKING
-- usage_count et usage_reset_date sont déjà dans customers
-- Pas besoin de table usage_tracking séparée

-- =========================================
-- FIN DU SCRIPT
-- =========================================

-- Pour tester l'API après ce script :
-- 1. Exécute tout ce SQL dans Supabase SQL Editor
-- 2. Configure .env avec SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY
-- 3. Lance l'API : uvicorn app.main:app --reload
-- 4. Teste : http://localhost:8000/docs
