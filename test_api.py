#!/usr/bin/env python3
"""
Script de test rapide pour vérifier que l'API fonctionne
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    return response.status_code == 200

def test_calculate_fees():
    """Test calculate fees endpoint"""
    print("\n🔍 Testing /api/calculate-fees...")
    payload = {
        "sale_price": 29.99,
        "production_cost": 12.0,
        "shipping_cost": 4.0,
        "offsite_ads": False
    }
    response = requests.post(
        f"{BASE_URL}/api/calculate-fees",
        json=payload
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    print("\n🔍 Testing /api/auth/register...")
    payload = {
        "email": f"test{int(requests.time.time())}@example.com",
        "password": "testpass123",
        "name": "Test User"
    }
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=payload
    )
    print(f"   Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"   User ID: {data['user_id']}")
        print(f"   Token: {data['access_token'][:20]}...")
        return True, data
    else:
        print(f"   Error: {response.json()}")
        return False, None

def main():
    print("=" * 50)
    print("🚀 ETSY DASHBOARD API - TEST SUITE")
    print("=" * 50)
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    # Test 2: Calculate fees
    results.append(("Calculate Fees", test_calculate_fees()))
    
    # Test 3: Register (requiert Supabase configuré)
    try:
        success, data = test_register()
        results.append(("User Registration", success))
    except Exception as e:
        print(f"   ⚠️  Erreur (Supabase peut-être non configuré): {e}")
        results.append(("User Registration", False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, s in results if s)
    print(f"\n{passed}/{total} tests passés")
    
    if passed == total:
        print("\n🎉 Tous les tests sont OK!")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API.")
        print("   Assurez-vous que le serveur est lancé:")
        print("   uvicorn app.main:app --reload")
