"""
Orchestrator for multi-agent ESG analysis.
"""
from .risk_agent import RiskAgent
from .retrofit_agent import RetrofitAgent
from .financial_agent import FinancialAgent

class ESGOrchestrator:
    """
    Coordinates specialized agents for ESG analysis.
    """

    def __init__(self):
        self.risk_agent = RiskAgent()
        self.retrofit_agent = RetrofitAgent()
        self.financial_agent = FinancialAgent()

    def analyze(self, input_data: dict) -> dict:
        risk = self.risk_agent.analyze(input_data)
        retrofit = self.retrofit_agent.recommend(input_data)
        financial = self.financial_agent.evaluate(input_data)

        return {
            "risk": risk,
            "retrofit": retrofit,
            "financial": financial
        }