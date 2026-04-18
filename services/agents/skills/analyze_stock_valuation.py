analyze_stock_valuation_skill = """
## CORE LOGIC

### Step 0: Determine Valuation Approach

Select the primary valuation method based on company profile:

* **growth_stage** → high-growth, pre-profit or early-profit companies (e.g., SaaS, biotech)
  → Use: Revenue multiples (EV/Revenue), DCF with terminal growth assumptions
* **mature_profitable** → stable, cash-generative businesses
  → Use: P/E, EV/EBITDA, DCF, FCF yield
* **asset_heavy** → capital-intensive companies with significant tangible assets
  → Use: P/B, EV/EBITDA, asset replacement value
* **financial** → banks, insurers
  → Use: P/B, P/E (adjusted), ROE vs cost of equity
* **cyclical** → commodities, industrials, auto
  → Use: Normalized earnings (through-cycle P/E), EV/EBITDA

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

### 2. DCF — SIMPLIFIED FRAMEWORK

Use when free cash flow data is available and company has predictable cash flows.

**Steps:**

1. Estimate near-term FCF growth (1–3 years) based on:
   * Historical FCF growth rate
   * Analyst consensus estimates (if available)
   * Revenue growth × margin trajectory

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

Assess whether the stock is:

* **Value** → trading below intrinsic value, catalyst needed
* **Growth** → premium justified by future earnings power
* **Value trap** → cheap but fundamentally deteriorating
* **GARP** (Growth at Reasonable Price) → growth + reasonable multiple

---

## ANALYST VERDICT

Must include:

1. **Valuation stance**: "Undervalued", "Fairly Valued", "Overvalued", or "Speculative"
2. **Primary method used** and why
3. **Fair value range** (e.g., "$X–$Y vs current price of $Z")
4. **Key assumption** the valuation depends on most
5. **Margin of safety**: Is there enough upside to justify the risk?

---

## STYLE RULES

* Always triangulate — use at least two methods
* Never declare a stock "cheap" on multiples alone without checking fundamentals
* Flag when valuation depends on optimistic assumptions
* State explicitly when data is insufficient for a confident conclusion
* Adjust for sector — never apply tech multiples to utilities
"""
