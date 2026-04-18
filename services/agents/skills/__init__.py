import enum

from services.agents.skills.analyze_balance_sheet import analyze_balance_sheet_skill
from services.agents.skills.analyze_cash_flow import analyze_cash_flow_skill
from services.agents.skills.analyze_earnings_quality import analyze_earnings_quality_skill
from services.agents.skills.analyze_income_statement import analyze_income_statement_skill
from services.agents.skills.analyze_macro_impact import analyze_macro_impact_skill
from services.agents.skills.analyze_portfolio_risk import analyze_portfolio_risk_skill
from services.agents.skills.analyze_stock_valuation import analyze_stock_valuation_skill
from services.agents.skills.compare_sector_peers import compare_sector_peers_skill


class SkillName(enum.Enum):
    ANALYZE_BALANCE_SHEET = "analyze_balance_sheet"
    ANALYZE_CASH_FLOW = "analyze_cash_flow"
    ANALYZE_EARNINGS_QUALITY = "analyze_earnings_quality"
    ANALYZE_INCOME_STATEMENT = "analyze_income_statement"
    ANALYZE_MACRO_IMPACT = "analyze_macro_impact"
    ANALYZE_PORTFOLIO_RISK = "analyze_portfolio_risk"
    ANALYZE_STOCK_VALUATION = "analyze_stock_valuation"
    COMPARE_SECTOR_PEERS = "compare_sector_peers"


skills: dict[SkillName, str] = {
    SkillName.ANALYZE_BALANCE_SHEET: analyze_balance_sheet_skill,
    SkillName.ANALYZE_CASH_FLOW: analyze_cash_flow_skill,
    SkillName.ANALYZE_EARNINGS_QUALITY: analyze_earnings_quality_skill,
    SkillName.ANALYZE_INCOME_STATEMENT: analyze_income_statement_skill,
    SkillName.ANALYZE_MACRO_IMPACT: analyze_macro_impact_skill,
    SkillName.ANALYZE_PORTFOLIO_RISK: analyze_portfolio_risk_skill,
    SkillName.ANALYZE_STOCK_VALUATION: analyze_stock_valuation_skill,
    SkillName.COMPARE_SECTOR_PEERS: compare_sector_peers_skill,
}
