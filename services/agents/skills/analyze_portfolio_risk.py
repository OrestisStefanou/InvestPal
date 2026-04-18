analyze_portfolio_risk_skill = """
## CORE LOGIC

### Step 0: Gather Portfolio Data

Retrieve all current holdings including:
* Asset names, tickers, quantities, current market value
* Asset classes (stocks, ETFs, crypto, bonds, cash)
* Sectors and geographies of each holding

Compute:
* Total portfolio value
* Weight of each position (position value / total value × 100)

---

## RISK DIMENSIONS

Assess the portfolio across the following risk dimensions in order:

---

### 1. CONCENTRATION RISK

**Position-level concentration:**

* Flag any single position > 10% of portfolio
* Flag any single position > 20% as high concentration
* Ideal: no single stock > 5–8% for a diversified portfolio

**Sector-level concentration:**

* Compute total weight per sector
* Flag any sector > 30% of portfolio
* Flag any sector > 50% as critical overexposure
* Acceptable sector weights vary by strategy (growth vs income vs balanced)

**Asset class concentration:**

* Compute weight by asset class: equities, fixed income, crypto, cash, alternatives
* Flag if >80% in a single asset class (unless user is explicitly a concentrated investor)
* Flag if crypto > 20% — elevated volatility risk
* Flag if cash > 30% — potential opportunity cost

---

### 2. DIVERSIFICATION QUALITY

**Geographic diversification:**

* Identify % in US vs international vs emerging markets
* Flag: >90% US-only = home country bias
* Flag: >30% in a single emerging market = concentrated EM risk

**Correlation risk:**

* Identify clusters of assets that tend to move together:
  * Multiple tech stocks (correlated)
  * Multiple crypto assets (highly correlated)
  * Sector ETFs + individual stocks in same sector (redundant)
* Warn when holdings appear to provide less diversification than they seem

**Style diversification:**

* Check balance of:
  * Growth vs Value
  * Large cap vs Mid/Small cap
  * Domestic vs International
* Flag if heavily skewed to one style without clear rationale

---

### 3. VOLATILITY RISK

Assess expected portfolio volatility:

* **Low volatility**: mostly bonds, dividend stocks, stable large-caps
* **Moderate volatility**: diversified equity portfolio, some growth
* **High volatility**: concentrated in growth/tech, significant crypto, small caps
* **Very high volatility**: >20% crypto, concentrated single-stock, leveraged positions

Adjust assessment based on user's:
* Risk tolerance (from user context)
* Time horizon (longer horizon → more tolerance for volatility)
* Investment goals (retirement → prefer lower volatility)

---

### 4. LIQUIDITY RISK

Assess ease of exiting positions:

* Large-cap stocks / major ETFs → high liquidity
* Small-cap stocks → moderate liquidity
* Crypto → varies; major coins (BTC, ETH) are liquid; altcoins may not be
* Real estate / private assets → illiquid

Flag:
* >20% in illiquid assets if user may need funds in <3 years
* Over-reliance on illiquid assets for short-term financial goals

---

### 5. DRAWDOWN RISK

Estimate potential maximum drawdown scenarios:

* **Bear market scenario** (equity market -30–40%):
  * Apply sector-specific drawdowns
  * Tech/growth: typically -40–60% in severe bear markets
  * Defensive sectors: typically -15–25%
  * Crypto: typically -60–80%+ in crypto winters

* **Recession scenario**:
  * Cyclicals hit hardest
  * Defensives (utilities, healthcare, consumer staples) hold better

State estimated portfolio drawdown range:
* e.g., "In a 2022-style correction, this portfolio could decline ~X–Y%"

---

### 6. INCOME & DIVIDEND RISK

If user relies on portfolio income:

* Identify dividend-paying holdings and yield
* Flag if dividend income is concentrated in 1–2 holdings
* Assess dividend sustainability (payout ratio, FCF coverage)
* Note: high yield stocks may signal distress, not income quality

---

## REBALANCING RECOMMENDATIONS

Based on findings, suggest:

1. **Positions to reduce** (overweight, concentrated, correlated)
2. **Areas underrepresented** (missing sectors, geographies, asset classes)
3. **Risk-adjusted alternatives** if applicable (e.g., "replace concentrated tech stock with broad tech ETF")
4. **Priority order**: address highest concentration risks first

Only make specific recommendations if sufficient data is available. Flag data gaps.

---

## ALIGNMENT WITH USER PROFILE

Cross-check risk profile against user context:

* **Risk tolerance**: Is current risk level consistent with stated tolerance?
* **Time horizon**: Does portfolio volatility match investment timeline?
* **Goals**: Does current allocation serve stated goals (growth, income, preservation)?

Flag mismatches explicitly:
* e.g., "You've indicated low risk tolerance, but 45% of your portfolio is in high-volatility growth stocks"

---

## ANALYST VERDICT

Must include:

1. **Overall risk rating**: "Conservative", "Moderate", "Aggressive", "Very Aggressive"
2. **Top 3 risks**: the most important issues to address
3. **Alignment score**: Does the portfolio match the user's stated goals and risk tolerance?
4. **Recommended actions**: prioritized list of rebalancing steps

---

## STYLE RULES

* Always contextualize risk against user's profile — not a generic investor
* Avoid alarmism: flag risks proportionally to severity
* Be specific: name the positions causing concentration, not just abstract warnings
* Acknowledge when portfolio is well-diversified — positive feedback matters
"""
