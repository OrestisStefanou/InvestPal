analyze_stock_valuation_skill = """
## CORE LOGIC

### Step 0: Determine Valuation Approach

**Graham & Dodd Hierarchy (preferred order of reliability):**

1. **Asset Value** — the most reliable estimate. What would it cost to reproduce this
   business's assets? For viable businesses, use reproduction/replacement cost.
   For non-viable businesses, use liquidation value.
2. **Earnings Power Value (EPV)** — second most reliable. What is the value of
   current sustainable earnings, assuming no growth? EPV = Adjusted earnings / cost of capital.
3. **Growth** — least reliable. Only relevant for franchise businesses (EPV >> Asset Value)
   with sustainable competitive advantages. For competitive businesses, growth neither
   creates nor destroys value and should be IGNORED in valuation.

**Then select complementary methods based on company profile:**

* **growth_stage** → high-growth, pre-profit or early-profit companies (e.g., SaaS, biotech)
  → Use: Revenue multiples (EV/Revenue), return-based franchise analysis if barriers to entry exist
  → Caution: these are lottery-ticket stocks — systematically overvalued as a group
* **mature_profitable** → stable, cash-generative businesses
  → Use: EPV, P/E, EV/EBITDA, FCF yield
* **asset_heavy** → capital-intensive companies with significant tangible assets
  → Use: Asset reproduction value, P/B, EV/EBITDA
* **financial** → banks, insurers
  → Use: P/B, P/E (adjusted), ROE vs cost of equity (enterprise value not meaningful for financials)
* **cyclical** → commodities, industrials, auto
  → Use: Asset reproduction value (most stable for cyclicals), normalized earnings (through-cycle P/E), EV/EBITDA

Always apply at least two methods. Triangulate — do not rely on a single multiple.

---

## VALUATION METHODS

### 1. COMPARABLE MULTIPLES (Relative Valuation)

Collect current multiples for the company:

* P/E (Price-to-Earnings)
* EV/EBITDA (Enterprise Value to EBITDA)
* EV/Revenue
* P/B (Price-to-Book) — especially for financials and asset-heavy
* P/FCF (Price-to-Free-Cash-Flow) — for mature cash generators

**Interpretation rules:**

* Compare against:
  1. Historical average of the same company (3–5 year range)
  2. Sector/industry peer median
* Premium justified by:
  * Superior growth rate
  * Higher margins
  * Stronger competitive moat
  * Better capital allocation
* Discount warranted by:
  * Slowing growth
  * Margin deterioration
  * Higher leverage
  * Competitive threats

Red flags:
* Multiples far above historical average without fundamental improvement
* Premium vs peers that cannot be explained by growth or quality
* Negative earnings making P/E meaningless — rely on EV/Revenue or EV/EBITDA

---

### 2. EARNINGS POWER VALUE (EPV) — GRAHAM & DODD APPROACH

The preferred method for most established businesses. Values the company based on
current sustainable earnings without speculating about future growth.

**Steps:**

1. Calculate **average operating margin** over 7-15 years (spanning 1-2 business cycles)
2. Multiply by current revenue to get sustainable operating income
3. Apply average tax rate to get **NOPAT** (net operating profit after taxes)
4. Adjust for **depreciation vs maintenance CapEx** gap:
   * Find low/no-growth periods — total CapEx then ≈ maintenance CapEx
   * If maintenance CapEx < accounting depreciation → add difference to earnings
   * If maintenance CapEx > accounting depreciation → subtract difference
5. Adjust for recurring "one-time" charges (average over 5+ years if they recur)
6. **EPV (enterprise)** = Adjusted earnings power / cost of capital
7. **EPV (equity)** = Enterprise EPV + excess cash + non-operating assets - debt - legacy liabilities

**Cost of capital estimation:**
* Low risk equity: 6-8% (utilities, stable consumer staples)
* Moderate risk equity: 8-10% (general services, industrials)
* High risk equity: 10-13% (cyclicals, commodities, tech)
* Do NOT rely on beta-based CAPM — estimation errors are too large to be useful

### 2b. DCF — USE WITH CAUTION

Appropriate ONLY for short-term, well-defined cash flows (event-based investing,
liquidations, reorganizations) or as a secondary check. For long-horizon investments,
DCF suffers from three fundamental problems:
* Ignores balance sheet information
* Terminal value (most uncertain component) dominates total value
* Mixes reliable near-term estimates with unreliable far-future projections

If used:

1. Estimate near-term FCF growth (1–3 years) based on:
   * Historical FCF growth rate
   * Analyst consensus estimates (if available)
   * Revenue growth x margin trajectory

2. Apply terminal growth rate:
   * Mature business: 2–3%
   * Growth business: 3–5%
   * Declining business: 0–1%

3. Use discount rate:
   * Low risk (investment grade, stable cash flows): 8–10%
   * Medium risk (moderate leverage, cyclical): 10–12%
   * High risk (early stage, high leverage): 12–15%+

4. Sensitivity check:
   * What happens if growth is 2% lower than assumed?
   * What happens if discount rate is 2% higher?
   * Flag if valuation is highly sensitive to assumptions
   * Flag if terminal value exceeds 60% of total — the valuation rests on
     the least reliable component

**Output:** Implied fair value range vs current price
→ Interpret: >20% upside = potentially undervalued; >20% downside = potentially overvalued

---

### 3. FCF YIELD (for mature companies)

FCF Yield = FCF per share / Current Price

Interpret:
* >5% → attractive for mature business
* 2–5% → fair
* <2% → expensive relative to cash generation
* Compare to risk-free rate (10Y Treasury yield) as a benchmark

---

### 4. PEG RATIO (for growth companies)

PEG = P/E ÷ Earnings Growth Rate

Interpret:
* <1 → potentially undervalued relative to growth
* 1 → fair value
* >2 → expensive relative to growth
* Note: Less useful for companies with negative earnings

---

## SECTOR-SPECIFIC ADJUSTMENTS

### TECHNOLOGY (asset_light / growth_stage)

* EV/Revenue is primary for pre-profit companies
* EV/EBITDA and P/FCF for profitable tech
* High multiples justifiable ONLY with:
  * High revenue growth (>20% YoY)
  * Expanding margins
  * Large addressable market
* Red flag: High P/E + decelerating growth + margin compression

---

### FINANCIALS (banks, insurers)

* P/B is primary
  * P/B > 1 justified when ROE > cost of equity
  * P/B < 1 suggests market expects value destruction
* Adjusted P/E (exclude one-off credit provisions)
* Avoid EV/EBITDA — not meaningful for financials

---

### CAPITAL-INTENSIVE (utilities, energy, industrials)

* EV/EBITDA is primary (strips out depreciation differences)
* P/B meaningful (asset replacement value)
* For energy: also consider EV/reserves, EV/production
* Accept lower multiples due to slower growth
* Dividend yield matters: compare to sector and risk-free rate

---

### CYCLICALS (industrials, auto, commodities)

* Use normalized/through-cycle earnings — avoid peak earnings P/E
* EV/EBITDA on normalized basis
* Watch for mean-reversion: high current earnings may be cyclical peak
* Flag: P/E appears cheap at earnings peak — deceptive

---

## GROWTH VS VALUE CONTEXT

### Graham & Dodd Framework for Growth

**Growth creates value ONLY for franchise businesses** — those with sustainable
competitive advantages (EPV >> Asset Value). For competitive businesses where
EPV ≈ Asset Value, growth neither creates nor destroys value.

Classify the company:

* **Case A (AV > EPV)** → poor management or non-viable business. Growth DESTROYS
  value. Investment requires management change catalyst. Classic "value trap."
* **Case B (AV ≈ EPV)** → competitive business, capable management. Growth is
  IRRELEVANT to valuation. Value on assets and EPV alone.
* **Case C (EPV >> AV)** → franchise business with barriers to entry. Growth CREATES
  value. Use return-based analysis: Total return = cash yield + organic growth +
  active reinvestment return. Account for franchise fade.

Assess whether the stock is:

* **Value** → trading below intrinsic value (AV or EPV), catalyst may be needed
* **Franchise growth** → premium justified by sustainable competitive advantages and
  value-creating growth (Case C only)
* **Value trap** → asset-rich but management destroys value (Case A without catalyst)
* **GARP** (Growth at Reasonable Price) → franchise stock at reasonable return spread
  above cost of capital

---

## ANALYST VERDICT

Must include:

1. **Valuation stance**: "Undervalued", "Fairly Valued", "Overvalued", or "Speculative"
2. **Primary method used** and why (prefer EPV/AV over DCF for long-horizon assets)
3. **Fair value range** (e.g., "$X-$Y vs current price of $Z")
4. **Case classification**: A (value trap), B (competitive), or C (franchise)
5. **Key assumption** the valuation depends on most
6. **Margin of safety**: Is there enough upside to justify the risk? Graham's minimum: 33%.
   For franchise stocks, express as return spread above cost of capital minus fade rate.

---

## STYLE RULES

* Always triangulate — use at least two methods, preferably AV and EPV
* Never declare a stock "cheap" on multiples alone without checking fundamentals
* Flag when valuation depends on optimistic assumptions
* State explicitly when data is insufficient for a confident conclusion
* Adjust for sector — never apply tech multiples to utilities
* Never pay for growth in a competitive business (Case B) — it creates no value
* Be skeptical of DCF valuations where terminal value dominates (>60% of total)
* Always distinguish between enterprise and equity margin of safety
* Remember: 80-90% of active fund managers underperform index funds. The bar for
  claiming a stock is mispriced is high — you must explain why you are on the right
  side of the trade
"""
