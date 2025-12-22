"""
Router pour calculateur de frais Etsy
Endpoint principal pour calcul des frais et marges
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

# Schemas
class FeeCalculationRequest(BaseModel):
    sale_price: float = Field(..., gt=0, description="Prix de vente du produit")
    production_cost: float = Field(0.0, ge=0, description="Coût de production")
    shipping_cost: float = Field(0.0, ge=0, description="Coût d'expédition")
    offsite_ads: bool = Field(False, description="Utilise Etsy Offsite Ads?")

class FeeBreakdown(BaseModel):
    transaction_fee: float
    listing_fee: float
    payment_processing: float
    offsite_ads: float
    total_fees: float

class FeeCalculationResponse(BaseModel):
    fees: FeeBreakdown
    net_revenue: float
    total_costs: float
    profit: float
    profit_margin: float

# Fonction de calcul (logique métier propriétaire)
def calculate_etsy_fees(
    sale_price: float,
    production_cost: float = 0.0,
    shipping_cost: float = 0.0,
    offsite_ads: bool = False
) -> FeeCalculationResponse:
    """
    Calcule tous les frais Etsy et les marges
    
    Frais Etsy 2024:
    - Transaction fee: 6.5% du prix de vente
    - Listing fee: $0.20 par produit listé
    - Payment processing: 3% + $0.25 du prix de vente
    - Offsite ads: 15% du prix de vente (si activé)
    
    Args:
        sale_price: Prix de vente
        production_cost: Coût de production
        shipping_cost: Coût d'expédition
        offsite_ads: Si Offsite Ads activé
        
    Returns:
        Détails des frais, revenus nets, profit et marge
    """
    # Calculs des frais
    transaction_fee = round(sale_price * 0.065, 2)
    listing_fee = 0.20
    payment_processing = round((sale_price * 0.03) + 0.25, 2)
    offsite_ads_fee = round(sale_price * 0.15, 2) if offsite_ads else 0.0
    
    total_fees = round(transaction_fee + listing_fee + payment_processing + offsite_ads_fee, 2)
    
    # Calculs de rentabilité
    net_revenue = round(sale_price - total_fees, 2)
    total_costs = round(production_cost + shipping_cost, 2)
    profit = round(net_revenue - total_costs, 2)
    profit_margin = round((profit / sale_price * 100), 1) if sale_price > 0 else 0.0
    
    return FeeCalculationResponse(
        fees=FeeBreakdown(
            transaction_fee=transaction_fee,
            listing_fee=listing_fee,
            payment_processing=payment_processing,
            offsite_ads=offsite_ads_fee,
            total_fees=total_fees
        ),
        net_revenue=net_revenue,
        total_costs=total_costs,
        profit=profit,
        profit_margin=profit_margin
    )

# Endpoint
@router.post("/calculate-fees", response_model=FeeCalculationResponse)
async def calculate_fees(request: FeeCalculationRequest):
    """
    Calcule les frais Etsy et la rentabilité
    
    **Exemple de requête:**
    ```json
    {
      "sale_price": 29.99,
      "production_cost": 12.0,
      "shipping_cost": 4.0,
      "offsite_ads": false
    }
    ```
    
    **Retourne:**
    - Détail de tous les frais Etsy
    - Revenu net après frais
    - Profit et marge bénéficiaire
    """
    try:
        result = calculate_etsy_fees(
            sale_price=request.sale_price,
            production_cost=request.production_cost,
            shipping_cost=request.shipping_cost,
            offsite_ads=request.offsite_ads
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating fees: {str(e)}")

@router.get("/fees/info")
async def get_fees_info():
    """
    Retourne les informations sur les frais Etsy actuels
    """
    return {
        "fees": {
            "transaction_fee": {
                "rate": "6.5%",
                "description": "Frais de transaction sur chaque vente"
            },
            "listing_fee": {
                "rate": "$0.20",
                "description": "Frais de mise en ligne par produit (valable 4 mois)"
            },
            "payment_processing": {
                "rate": "3% + $0.25",
                "description": "Frais de traitement des paiements"
            },
            "offsite_ads": {
                "rate": "15%",
                "description": "Commission sur ventes via publicités Etsy (optionnel)",
                "note": "Obligatoire si >$10k de ventes annuelles"
            }
        },
        "last_updated": "2024-12-19",
        "source": "https://www.etsy.com/legal/fees"
    }
