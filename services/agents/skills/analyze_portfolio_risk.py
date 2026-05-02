analyze_portfolio_risk_skill = """
## CORE LOGIC

### What Risk Means

Risk is NOT volatility. A stock that drops 50% while its intrinsic value remains
unchanged has become LESS risky -- the margin of safety has increased. Risk is:

1. **Permanent loss of capital** -- buying above intrinsic value, or holding a business
   whose intrinsic value is declining irreversibly
2. **Being forced to sell at the wrong time** -- through leverage, liquidity needs,
   or psychological pressure

Price fluctuations are only dangerous if they force action or reflect genuine
business deterioration. For a patient investor with a sound process, Mr. Market's
mood swings are opportunities, not threats.

### Step 0: Gather Portfolio Data

Retrieve all current holdings including:
* Asset names, tickers, quantities, current market value
* Asset classes (stocks, ETFs, crypto, bonds, cash)
* Sectors and geographies of each holding

Compute:
* Total portfolio value
* Weight of each position (position value / total value x 100)

---

## RISK DIMENSIONS

Assess the portfolio across the following dimensions, ordered by importance:

---

### 1. MARGIN OF SAFETY RISK (Most Important)

The margin of safety is the gap between what you paid and what the business is worth.
It is the single most important measure of investment risk.

**For each significant holding, assess:**

* Was the position purchased at a discount to estimated intrinsic value?
* Has the intrinsic value changed since purchase (business improvement or deterioration)?
* What is the current margin of safety (estimated intrinsic value vs current market price)?

**Classification:**

* Holdings with wide margin of safety (>30% below intrinsic value) → low risk
* Holdings near fair value → moderate risk
* Holdings above estimated intrinsic value → high risk -- the primary source of
  permanent capital loss

**Portfolio-level assessment:**

* What fraction of the portfolio was purchased with an adequate margin of safety?
* Are there positions that were once cheap but have appreciated beyond fair value?
  These should be candidates for trimming.

Note: If margin of safety cannot be assessed for a holding (insufficient data), flag
it as an unquantified risk rather than ignoring it.

---

### 2. BUSINESS QUALITY RISK

Not all businesses carry equal risk. The quality of the underlying business determines
how likely the intrinsic value is to hold up or grow over time.

**Franchise businesses** (wide moat, EPV >> asset value):
* Lower risk of permanent impairment
* Earnings protected by barriers to entry
* But: franchise erosion ("fade") is a real risk -- assess durability
* Dying franchises destroy value far more severely than dying competitive businesses

**Competitive businesses** (no moat, EPV ≈ asset value):
* Moderate risk -- earnings can fluctuate but asset values provide a floor
* Capital recoveries from shrinkage roughly offset lost earnings
* Growth neither helps nor hurts

**Poor management / value trap businesses** (asset value > EPV):
* Higher risk unless a catalyst for management change exists
* Growth actively destroys value
* Requires deep discount to BOTH asset value and EPV

**Portfolio-level assessment:**
* What fraction of the portfolio is in franchise vs competitive vs value-trap businesses?
* Is franchise fade risk concentrated (e.g., multiple tech franchises all vulnerable
  to the same disruption)?

---

### 3. LEVERAGE RISK (Company-Level)

Debt is the most common mechanism by which temporary business problems become
permanent capital losses. Graham and Dodd avoided highly leveraged firms for
good reason.

**For each holding, assess:**

* Debt-to-equity and net debt / EBITDA
* Interest coverage ratio
* Debt maturity profile (near-term maturities in a downturn = danger)
* Does the company have enough liquidity to survive 2-3 years of poor conditions?

**Portfolio-level assessment:**

* What fraction of the portfolio is in highly leveraged companies?
* In a recession scenario, which holdings face bankruptcy or severe distress risk?
* Leverage magnifies equity margin of safety calculations -- a 15% error in
  enterprise value can mean a 5x swing in equity value for a leveraged firm

---

### 4. CONCENTRATION RISK

Concentration magnifies both gains and losses. It is acceptable only when paired
with deep knowledge (circle of competence) and wide margins of safety.

**Position-level:**
* Flag any single position > 10% of portfolio
* Flag any single position > 20% as high concentration
* Concentrated positions are acceptable IF: the investor has deep expertise in the
  business AND the margin of safety is wide

**Sector-level:**
* Flag any sector > 30% of portfolio
* Assess whether sector concentration reflects specialization (deliberate, informed)
  or drift (accidental, uninformed)

**Asset class:**
* Flag if >80% in a single asset class
* Note: for a value investor, being >80% in equities is not inherently wrong if
  each position has an adequate margin of safety

---

### 5. LIQUIDITY RISK

Liquidity risk matters only when the investor may be forced to sell. It is a function
of both the portfolio and the investor's personal circumstances.

**Portfolio-level:**
* Large-cap stocks / major ETFs → high liquidity
* Small-cap stocks → moderate liquidity (but small-cap illiquidity often creates
  opportunity -- fewer analysts, institutional size bias)
* Crypto → varies; major coins liquid, altcoins may not be
* Real estate / private assets → illiquid

**Flag:**
* >20% in illiquid assets if user may need funds within 3 years
* Over-reliance on illiquid assets for short-term financial goals
* Margin or leveraged positions that could force sales at unfavorable prices

---

### 6. INCOME RISK

If the user relies on portfolio income:

* Identify dividend-paying holdings and yield
* Flag if dividend income is concentrated in 1-2 holdings
* Assess dividend sustainability (payout ratio, FCF coverage)
* High yield may signal distress, not income quality
* Prefer dividends backed by sustainable earnings power, not funded by debt or
  asset sales

---

## PRICE DECLINES IN CONTEXT

When a holding's price drops significantly:

**Ask: Has the intrinsic value changed?**

* If NO (business fundamentals intact) → risk has DECREASED because margin of
  safety is wider. This is an opportunity to add, not a reason to sell.
* If YES (business fundamentally impaired) → risk has increased. Reassess
  whether the revised intrinsic value still exceeds the new price.
* If UNCERTAIN → this is the critical situation. The research effort should focus
  on determining whether the decline reflects Mr. Market's mood or genuine
  business deterioration.

Historical drawdown estimates (bear market -30%, crypto -70%, etc.) are useful
for assessing whether the investor can psychologically and financially withstand
price declines without being forced to sell. They are NOT measures of investment risk.

---

## ALIGNMENT WITH USER PROFILE

Cross-check against user context:

* **Risk tolerance**: Does the investor have the temperament to hold through
  significant price declines without panicking? If not, wider margins of safety
  and less concentration are necessary -- not because the investments are riskier,
  but because the investor may be forced into bad decisions.
* **Time horizon**: Longer horizons allow more time for price to converge to value.
  Shorter horizons require wider margins of safety.
* **Goals**: Does the portfolio serve stated goals (growth, income, preservation)?
* **Circle of competence**: Are concentrated positions within the investor's area
  of expertise?

---

## ANALYST VERDICT

Must include:

1. **Overall risk assessment**: "Well-Protected", "Adequate", "Elevated", or "Dangerous"
2. **Top 3 risks**: the most important issues, prioritized by potential for
   permanent capital loss (not by volatility)
3. **Margin of safety status**: What fraction of the portfolio has adequate margin of safety?
4. **Alignment**: Does the portfolio match the user's circumstances and temperament?
5. **Recommended actions**: prioritized steps to reduce risk of permanent capital loss

---

## STYLE RULES

* Never equate price decline with risk -- always ask whether intrinsic value changed
* Risk is about permanent capital loss, not quarterly price fluctuations
* Concentration in well-understood, undervalued businesses is not inherently risky
* Leverage is the most common path from temporary problem to permanent loss
* Frame recommendations around margin of safety, not around diversification for
  its own sake
* Acknowledge when the portfolio is well-positioned -- not every assessment needs
  to find problems
"""
