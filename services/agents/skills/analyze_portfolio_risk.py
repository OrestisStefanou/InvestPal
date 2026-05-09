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

### Other Forms of Risk That Affect Investor Behavior

While permanent loss is the primary risk, several secondary risks shape how
investors actually behave -- and surface as portfolio problems if ignored:

* **Falling short of one's goal** -- subjective, depends on the investor's
  spending or actuarial requirements. A 6% return is a windfall for one
  investor and a crisis for another.
* **Underperformance / benchmark risk** -- the risk of trailing peers or an
  index. Tempts investors to chase consensus and abandon discipline at exactly
  the wrong times.
* **Career / agency risk** -- when the manager and the capital owner are
  different, the manager's incentive is asymmetric: limited upside from gains,
  large downside from underperformance. Pushes managers toward conformity.
* **Unconventionality risk** -- pain of looking different. Often the price of
  alpha, since "unconventional" portfolios are required to outperform.
* **Illiquidity risk** -- inability to convert an asset to cash at a fair price
  on the schedule needed.

These are not the dominant risks for a long-horizon investor with a sound
process, but they are the risks that produce the BEHAVIORAL mistakes
(panic-selling at lows, capitulating to bubbles, reaching for return) which
then become permanent capital losses.

### The Perversity of Risk

Risk is highest when investors believe it is lowest. A widely held belief that
"this is safe" drives prices up, drives risk premiums down, and reduces the
margin of safety -- precisely making the asset risky. Conversely, when
everyone agrees an asset is risky, their unwillingness to buy lowers price
until the margin of safety becomes generous.

Implications for portfolio review:
* High-quality assets at consensus-favorite prices can be among the riskiest
  holdings in the portfolio.
* Low-quality, controversial, or scorned assets can be the safest holdings if
  bought with sufficient margin of safety.
* The temperature of the broader market matters. In late-stage bull markets
  the same portfolio carries more risk than in depressed environments,
  because the inputs (prices, sentiment, leverage) are themselves elevated.

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

### 7. CORRELATION RISK / HIDDEN COMMON FACTORS

Diversification is effective only when holdings respond differently to the
same shock. A portfolio of "30 different names" can behave like a single
position if all 30 share a hidden common factor.

Look for hidden correlations that ordinary diversification analysis misses:

* **Macro factor**: are most positions implicitly long the same macro variable
  -- low interest rates, weak USD, easy credit, high oil price, or risk-on
  sentiment?
* **Liquidity factor**: how much of the portfolio is in instruments that
  become illiquid simultaneously in stress (small-caps, high yield credit,
  EM equities, certain crypto, private positions)?
* **Leverage factor**: are multiple holdings dependent on continued access to
  cheap credit at the corporate level? In a credit crunch they fall together.
* **Theme factor**: nominally different companies can be the same thematic
  bet (e.g., 8 different "AI infrastructure" plays).
* **Investor base factor**: holdings popular with the same type of forced
  seller move together. ETF-heavy small-caps, hedge-fund-favorite names,
  retail momentum darlings all cluster.

Stress-test correlation: in past crises, has this style of holding moved
toward correlation 1 with other holdings in the portfolio? If yes, the
nominal diversification overstates real diversification.

Failure of imagination is the most common analytical error in portfolio
construction. Allow explicitly for outcomes outside the recent historical
range, including:
* Drawdowns larger than any in the modern data
* Correlations rising toward 1 in stress
* Liquidity drying up across normally liquid markets
* "Improbable disaster" events that have not occurred but could

---

### 8. FORCED-SELLING RISK

The worst outcome in investing is being forced to sell into a depressed
market. The absence of margin debt is necessary but not sufficient.

Identify portfolio configurations that risk forced selling:
* **Direct leverage**: margin loans, derivatives requiring collateral, debt
  service tied to portfolio income.
* **Liquidity mismatch**: known cash needs (tuition, home purchase, business
  funding) within 1-3 years held in long-duration or volatile assets.
* **Psychological breakpoint**: position size or portfolio drawdown level
  beyond which the investor (or family / spouse / committee) will demand
  liquidation regardless of fundamentals. This is real and must be modelled
  honestly.
* **Mandate / rating dependencies**: bonds that flip out of investment grade,
  funds with redemption gates triggered by AUM thresholds, positions held
  only because of style classifications that may shift.

The defensive posture is to ensure the portfolio can ride out adverse
conditions without any of these triggering. The aggressive flip side: be
positioned to BE the buyer when others are forced sellers. That requires
unencumbered capital, long-term capital, and a strong stomach.

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

## ASYMMETRY AND THE QUALITY OF RISK BEARING

The defining mark of a skillful investor is not the level of return but the
asymmetry of return: capturing more of the upside than the downside relative
to a passive benchmark of equivalent style.

When reviewing the portfolio, ask:
* In an adverse scenario (recession, market drawdown, sentiment shift), how
  much would this portfolio lose relative to the broad market?
* In a favorable scenario, how much would it gain relative to the broad
  market?
* Is the upside-capture greater than the downside-capture? Asymmetric
  participation is the only reliable signature of skill.

A portfolio that wins in good times and loses equally hard in bad times has
high beta but no alpha. The risk borne is producing return, but the risk is
not being intelligently selected. Reframe positions so that aggregate
asymmetry is favorable -- typically by trimming the most stretched names and
adding positions where margin of safety is widest.

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
* The perversity of risk: what feels safe in late-cycle exuberance often is
  not, and what feels dangerous in panic often offers the largest margin of
  safety. Lean against the consensus reading of risk.
* Risk control is invisible when it is not needed. Most years are good years,
  and risk control adds nothing in good years. Its value shows only when the
  tide goes out. Do not abandon it because it has not been "earning its keep."
* Ensure that for every "what could go right" scenario examined, an equally
  rigorous "what could go wrong" scenario has been examined -- including
  outcomes outside the recent historical range.
"""
