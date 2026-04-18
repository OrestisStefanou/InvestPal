import enum

from services.agents.skills.analyze_balance_sheet import analyze_balance_sheet_skill
from services.agents.skills.analyze_cash_flow import analyze_cash_flow_skill
from services.agents.skills.analyze_income_statement import analyze_income_statement_skill


class SkillName(enum.Enum):
    ANALYZE_BALANCE_SHEET = "analyze_balance_sheet"
    ANALYZE_CASH_FLOW = "analyze_cash_flow"
    ANALYZE_INCOME_STATEMENT = "analyze_income_statement"


skills: dict[SkillName, str] = {
    SkillName.ANALYZE_BALANCE_SHEET: analyze_balance_sheet_skill,
    SkillName.ANALYZE_CASH_FLOW: analyze_cash_flow_skill,
    SkillName.ANALYZE_INCOME_STATEMENT: analyze_income_statement_skill,
}
