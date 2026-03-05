"""
ESG Orchestrator
Coordinates specialized agents for ESG analysis.
"""
from .risk_agent import RiskAgent
from .retrofit_agent import RetrofitAgent
from .finance_agent import FinancialAgent

class ESGOrchestrator:
    def __init__(self):
        self.risk_agent = RiskAgent()
        self.retrofit_agent = RetrofitAgent()
        self.financial_agent = FinancialAgent()

    def run(self, portfolio: dict, segment: str) -> dict:
        """
        Executes all agents and aggregates results.
        Matches the signature expected by app/tabs/ai_advisor.py.
        """
        risk = self.risk_agent.analyze(portfolio)
        retrofit = self.retrofit_agent.recommend(portfolio)
        financial = self.financial_agent.evaluate(portfolio)

        return {
            "risk": risk,
            "retrofit": retrofit,
            "financial": financial,
            "segment": segment,
            "meta": {
                "status": "complete",
                "agent_count": 3
            }
        }