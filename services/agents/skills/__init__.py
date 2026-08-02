import enum

from services.agents.skills.analyze_balance_sheet import analyze_balance_sheet_skill
from services.agents.skills.analyze_cash_flow import analyze_cash_flow_skill
from services.agents.skills.analyze_earnings_quality import (
    analyze_earnings_quality_skill,
)
from services.agents.skills.analyze_income_statement import (
    analyze_income_statement_skill,
)
from services.agents.skills.analyze_macro_impact import analyze_macro_impact_skill
from services.agents.skills.analyze_management_commentary import (
    analyze_management_commentary_skill,
)
from services.agents.skills.analyze_portfolio_risk import analyze_portfolio_risk_skill
from services.agents.skills.analyze_stock_valuation import analyze_stock_valuation_skill
from services.agents.skills.apply_second_level_thinking import (
    apply_second_level_thinking_skill,
)
from services.agents.skills.assess_competitive_moat import assess_competitive_moat_skill
from services.agents.skills.assess_market_sentiment import assess_market_sentiment_skill
from services.agents.skills.calculate_intrinsic_value import (
    calculate_intrinsic_value_skill,
)
from services.agents.skills.compare_sector_peers import compare_sector_peers_skill
from services.agents.skills.evaluate_investment_theme import (
    evaluate_investment_theme_skill,
)
from services.agents.skills.evaluate_margin_of_safety import (
    evaluate_margin_of_safety_skill,
)


class SkillName(enum.Enum):
    ANALYZE_BALANCE_SHEET = "analyze_balance_sheet"
    ANALYZE_CASH_FLOW = "analyze_cash_flow"
    ANALYZE_EARNINGS_QUALITY = "analyze_earnings_quality"
    ANALYZE_INCOME_STATEMENT = "analyze_income_statement"
    ANALYZE_MACRO_IMPACT = "analyze_macro_impact"
    ANALYZE_MANAGEMENT_COMMENTARY = "analyze_management_commentary"
    ANALYZE_PORTFOLIO_RISK = "analyze_portfolio_risk"
    ANALYZE_STOCK_VALUATION = "analyze_stock_valuation"
    APPLY_SECOND_LEVEL_THINKING = "apply_second_level_thinking"
    ASSESS_COMPETITIVE_MOAT = "assess_competitive_moat"
    ASSESS_MARKET_SENTIMENT = "assess_market_sentiment"
    CALCULATE_INTRINSIC_VALUE = "calculate_intrinsic_value"
    COMPARE_SECTOR_PEERS = "compare_sector_peers"
    EVALUATE_INVESTMENT_THEME = "evaluate_investment_theme"
    EVALUATE_MARGIN_OF_SAFETY = "evaluate_margin_of_safety"


# Description should be short, it should contain what the skill is and when to use
skill_descriptions: dict[SkillName, str] = {
    SkillName.ANALYZE_BALANCE_SHEET: (
        "Analyzes a company's balance sheet by sector profile, evaluating liquidity, solvency, "
        "asset quality (reproduction cost vs. book value), and capital structure trends. "
        "Use when the user asks about a company's financial strength, asset backing, or balance sheet health."
    ),
    SkillName.ANALYZE_CASH_FLOW: (
        "Analyzes cash generation (OCF and FCF), cash quality, capital allocation decisions, and the "
        "maintenance vs. growth CapEx gap to determine owner earnings. Use when the user asks about "
        "a company's cash flow health, CapEx efficiency, or how management deploys cash."
    ),
    SkillName.ANALYZE_EARNINGS_QUALITY: (
        "Evaluates reported earnings across eight dimensions — cash conversion, revenue quality, cost "
        "quality, non-recurring items, tax quality, earnings consistency, transcript signals, and EPV "
        "adjustments (maintenance CapEx vs. depreciation) — to detect distortions and estimate sustainable "
        "distributable earnings. Use when the user needs to verify the reliability of reported earnings "
        "or derive adjusted earnings power before valuation."
    ),
    SkillName.ANALYZE_INCOME_STATEMENT: (
        "Analyzes profitability metrics, growth quality, pricing power, and hidden growth-related "
        "investments to determine sustainable operating income using 7–15 year margin averaging. "
        "Use when the user asks about a company's through-cycle operational efficiency, margin "
        "sustainability, or pricing power."
    ),
    SkillName.ANALYZE_MACRO_IMPACT: (
        "Supplementary skill that assesses how macroeconomic conditions affect a specific company's "
        "fundamentals — calibrating whether current earnings are above or below sustainable levels, "
        "adjusting cost of capital, and checking industry viability. Use when the user asks how interest "
        "rates, recession, inflation, or the credit cycle impact a specific stock or holding."
    ),
    SkillName.ANALYZE_MANAGEMENT_COMMENTARY: (
        "Interprets what management is signalling about a business — guidance architecture, tone and "
        "language shifts, metric stability, attribution patterns, and the gap between stated priorities "
        "and executed capital allocation — grading how strong the underlying evidence is. Use when the "
        "user asks what management said about the quarter, how credible guidance is, or whether "
        "management's tone or priorities have changed."
    ),
    SkillName.ANALYZE_PORTFOLIO_RISK: (
        "Evaluates a portfolio's aggregate risk of permanent capital loss across eight dimensions: "
        "margin of safety, business quality, leverage, concentration, liquidity, income risk, hidden "
        "correlations, and forced-selling exposure. Use when the user asks about their overall portfolio "
        "risk, whether they are properly diversified, or how the portfolio would survive a downturn."
    ),
    SkillName.ANALYZE_STOCK_VALUATION: (
        "Triangulates asset reproduction value, EPV, multiples, PEG, FCF yield, and (cautiously) DCF "
        "while accounting for market psychology, forced buying/selling, and popularity-driven mispricing. "
        "Use when the user asks whether a stock is cheap or expensive, wants a valuation assessment, or "
        "needs to understand price vs. intrinsic value."
    ),
    SkillName.APPLY_SECOND_LEVEL_THINKING: (
        "Meta-check that stress-tests an investment thesis against consensus to identify informational, "
        "analytical, behavioral, or structural edge via a 9-point checklist. Use when the user is "
        "considering a buy/sell decision and needs a contrarian stress-test of the thesis before acting."
    ),
    SkillName.ASSESS_COMPETITIVE_MOAT: (
        "Determines whether a company is a franchise or competitive business by comparing EPV to asset "
        "value (Case A/B/C), then analyzes barriers to entry — customer captivity, cost advantages, "
        "economies of scale, and network effects — and estimates moat durability via half-life and fade "
        "rate. Use when the user asks about a company's competitive advantages, moat strength, or "
        "whether its growth will create or destroy value."
    ),
    SkillName.ASSESS_MARKET_SENTIMENT: (
        "Diagnoses broad market-wide temperature by tracking the economic cycle, credit cycle, investor "
        "psychology pendulum, and bull/bear market stages using a 22-item heated-vs-cold checklist. "
        "Use when the user asks about overall market conditions, whether it's a good time to invest, or "
        "how to position between defensive and aggressive stances."
    ),
    SkillName.CALCULATE_INTRINSIC_VALUE: (
        "Performs deep Graham & Dodd valuation: calculates net asset reproduction/liquidation value, "
        "earnings power value (EPV) via a 9-step process, and return-based franchise growth value, then "
        "triangulates them and runs reasonableness checks. Use when the user asks for a company's "
        "intrinsic value, fair value estimate, or a detailed bottom-up valuation."
    ),
    SkillName.COMPARE_SECTOR_PEERS: (
        "Compares a target company to 3–6 sector peers across growth, profitability, valuation multiples, "
        "and balance sheet health, then ranks competitive standing. Use when the user asks how a company "
        "stacks up against competitors or wants to explain relative valuation premiums or discounts."
    ),
    SkillName.EVALUATE_INVESTMENT_THEME: (
        "Turns an investment theme into a falsifiable claim, maps its value chain to derive a candidate "
        "set rather than recall one, tests which link actually captures the economics, and checks how "
        "much of the theme is already in the price. Use when the user asks for investment ideas around a "
        "trend, theme, or narrative, or asks which companies benefit from a given development."
    ),
    SkillName.EVALUATE_MARGIN_OF_SAFETY: (
        "Applies defensive-investing discipline to a single position or proposed trade, checking margin "
        "of safety adequacy, upside/downside asymmetry (≥2:1), forced-selling resilience, tail-scenario "
        "survival, return reasonableness, and common pitfalls. Use when the user asks whether a specific "
        "trade idea is safe enough, wants to stress-test a position, or needs to validate entry price "
        "discipline."
    ),
}


skills: dict[SkillName, str] = {
    SkillName.ANALYZE_BALANCE_SHEET: analyze_balance_sheet_skill,
    SkillName.ANALYZE_CASH_FLOW: analyze_cash_flow_skill,
    SkillName.ANALYZE_EARNINGS_QUALITY: analyze_earnings_quality_skill,
    SkillName.ANALYZE_INCOME_STATEMENT: analyze_income_statement_skill,
    SkillName.ANALYZE_MACRO_IMPACT: analyze_macro_impact_skill,
    SkillName.ANALYZE_MANAGEMENT_COMMENTARY: analyze_management_commentary_skill,
    SkillName.ANALYZE_PORTFOLIO_RISK: analyze_portfolio_risk_skill,
    SkillName.ANALYZE_STOCK_VALUATION: analyze_stock_valuation_skill,
    SkillName.APPLY_SECOND_LEVEL_THINKING: apply_second_level_thinking_skill,
    SkillName.ASSESS_COMPETITIVE_MOAT: assess_competitive_moat_skill,
    SkillName.ASSESS_MARKET_SENTIMENT: assess_market_sentiment_skill,
    SkillName.CALCULATE_INTRINSIC_VALUE: calculate_intrinsic_value_skill,
    SkillName.COMPARE_SECTOR_PEERS: compare_sector_peers_skill,
    SkillName.EVALUATE_INVESTMENT_THEME: evaluate_investment_theme_skill,
    SkillName.EVALUATE_MARGIN_OF_SAFETY: evaluate_margin_of_safety_skill,
}
