"""
Retrofit Strategy Agent
Recommends insulation and heat pump strategies.
"""
class RetrofitAgent:
    def recommend(self, portfolio: dict) -> dict:
        # Minimal deterministic implementation
        return {
            "recommendations": ["LED Lighting", "Heat Pump", "Loft Insulation"],
            "estimated_cost": 15000,
            "details": "Standard retrofit package generated."
        }