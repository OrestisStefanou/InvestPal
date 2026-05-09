calculate_intrinsic_value_skill = """
## CORE LOGIC

### Purpose

Calculate a company's intrinsic value using the three-element Graham & Dodd
framework: (1) Asset Value, (2) Earnings Power Value (EPV), (3) Growth value
(only for franchise businesses). Then compare to market price to determine
margin of safety.

This approach is superior to one-size-fits-all DCF because it:
* Segregates information by reliability (most to least certain)
* Incorporates balance sheet data that DCF ignores
* Integrates strategic judgments about competitive position
* Avoids contaminating reliable near-term data with speculative far-future projections

---

## ELEMENT 1: ASSET VALUE (Most Reliable)

### Step 1a: Determine Strategic Context

Before valuing assets, make a strategic judgment:
* **Viable business** → value assets at reproduction/replacement cost
* **Non-viable business (terminal decline)** → value assets at liquidation value

### Step 1b: Calculate Net Asset Value

**For viable businesses (reproduction cost approach):**

Work down the balance sheet, adjusting each item:

| Asset | Adjustment |
|-------|-----------|
| Cash and equivalents | Accept at book value |
| Marketable securities | Mark to current market value |
| Accounts receivable | Add back bad debt allowance (new entrant would face higher bad debts) |
| Inventory | Add LIFO reserve if applicable; reduce if days-of-inventory is abnormally high; adjust for obsolescence |
| Prepaid expenses | Accept at book value (small, properly measured) |
| Deferred tax assets | Discount to present value if non-current |
| Land | Adjust to current market/appraisal value (often far above book) |
| Buildings and structures | Adjust for inflation and economic growth; reduce less than accounting depreciation (real economic lives often exceed accounting lives) |
| Equipment | Estimate at ~50% of original cost x price trend adjustment (equipment prices often falling ~4% per year) |
| Construction in progress | Accept at book value (currently being reproduced) |
| Goodwill (accounting) | Set to ZERO -- represents historical acquisition premiums, not reproduction cost |
| Intangibles (accounting) | Set to ZERO -- estimate from first principles instead |

**Intangible asset reproduction costs (estimate separately):**

| Intangible | Estimation Method |
|-----------|-------------------|
| Product portfolio / R&D | Annual R&D spend x years of R&D embodied in current products (typically 3-7 years) |
| Customer base / revenue | Cost per dollar of revenue acquisition (internal brand-building cost / success rate, OR acquisition cost of comparable revenue, OR sales agency commissions) |
| Trained workforce | Recruitment and training costs (search firm fees, onboarding investment) |
| Organizational infrastructure | 1-3 years of administrative costs for ramp-up |

**Liabilities:**
* Current non-debt liabilities: accept at book value (must be paid)
* Long-term operational liabilities: book value, discount if long-dated in high-rate environments
* Legacy liabilities (pensions, environmental, litigation): verify against footnote disclosures; obtain independent estimate if material and company has reputation for accounting manipulation
* Debt: book value, adjusted for interest rate changes if material (use market price of comparable debt)

**Net Asset Value = Adjusted Assets - Adjusted Liabilities**

### For non-viable businesses (liquidation value):

| Asset | Typical Recovery |
|-------|-----------------|
| Cash | 100% |
| Marketable securities | 100% (if liquid) |
| Accounts receivable | 80-85% of book (after allowance) |
| Inventory (commodity-like) | 50-70% |
| Inventory (specialized/fashion) | 0-30% |
| Generic PP&E (office buildings) | 50-80% |
| Specialized PP&E (chemical plants) | 10-45% |
| Goodwill | 0% |
| Intangibles | 0% (unless tied to profitable independent operations) |

---

## ELEMENT 2: EARNINGS POWER VALUE (Second Most Reliable)

### Step 2a: Calculate Sustainable Earnings Power

EPV is the value of current earnings, properly adjusted, assuming NO growth.
It equals: **Adjusted After-Tax Earnings / Cost of Capital**

**Detailed earnings power calculation:**

1. **Start with current revenue** (unless highly cyclical, then use average sustainable revenue)

2. **Calculate average operating margin**
   * Use 7-15 year average that spans at least one full business cycle
   * If margins show a secular trend with an identifiable economic cause
     (e.g., industry restructuring, technology shift), use the most recent
     margin adjusted for cyclical position
   * If the trend has no identifiable cause, use the arithmetic mean
   * Do NOT extrapolate trends -- that is forecasting, not measuring current
     earnings power

3. **Sustainable operating income** = Current revenue x average operating margin

4. **Adjust for unconsolidated operations** if material (add/subtract equity
   earnings from subsidiaries, joint ventures, minority interests)

5. **Apply average tax rate** (use average since most recent major tax law change,
   typically 3-5 years)
   * Use accrued taxes, not cash taxes (cash tax discrepancies depend on
     growth; EPV assumes no growth)
   * Sustainable NOPAT = Adjusted operating income x (1 - average tax rate)

6. **Adjust for depreciation vs maintenance CapEx**
   * This is the MOST IMPORTANT adjustment
   * Accounting depreciation often differs significantly from true economic
     depreciation (maintenance capital expense)
   * **Method A:** Find periods of zero/low growth in the company's history.
     Total CapEx in those periods ≈ maintenance CapEx. Compare to
     accounting depreciation.
   * **Method B:** Estimate growth CapEx = revenue growth x capital intensity
     ratio (fixed assets / revenue). Subtract from total CapEx to get
     maintenance CapEx.
   * If maintenance CapEx < accounting depreciation: add the difference
     to earnings (accounting overstates costs)
   * If maintenance CapEx > accounting depreciation: subtract the difference
     (accounting understates costs)
   * NEVER use EBITDA as a shortcut -- assuming zero depreciation is almost
     always wrong

7. **Adjust for "one-time" charges**
   * If one-time charges recur regularly (annually or nearly so), they are
     NOT one-time. Calculate the average annual ratio of these charges to
     pre-adjustment earnings over 5+ years and reduce current earnings
     proportionally.
   * Even truly independent one-time events, if they recur as a regular
     feature of management's performance, represent a reduction in
     distributable earnings.

8. **Adjust for growth-related expenses buried in operations**
   * Growing firms may spend on R&D, marketing, hiring above maintenance
     levels. The excess above maintenance is growth investment, not a current
     cost. Add it back to calculate distributable earnings.
   * Shrinking firms may underinvest (cutting R&D, raising prices at expense
     of market position). Subtract the shortfall.

9. **Final Earnings Power** = Adjusted sustainable after-tax operating earnings

### Step 2b: Determine Cost of Capital

**Equity cost of capital ranges:**
* Low risk (utilities, stable consumer staples, all-equity financed): 6-8%
* Moderate risk (general services, stable industrials): 8-10%
* High risk (cyclicals, commodities, technology): 10-13%
* Upper bound: venture capital returns (13-14% in recent years)
* Lower bound: investment-grade bond yields + ~1%

**Debt cost of capital:**
* Use yield on publicly traded debt of comparable risk
* After-tax cost = pre-tax yield x (1 - corporate tax rate)
* If company has excessive leverage, cap debt weight at a "safe" level
  (~20-30%) where it would not impair operations

**WACC** = (weight of debt x after-tax cost of debt) + (weight of equity x cost of equity)

**Do NOT use beta-based CAPM.** The estimation errors in beta (plus/minus 0.5)
combined with uncertainty in the market risk premium (3-7%) produce cost of capital
ranges too wide to be useful. The qualitative risk categorization above is more reliable.

### Step 2c: Calculate EPV

* **Enterprise EPV** = Earnings Power / Cost of Capital
* **Equity EPV** = Enterprise EPV + excess cash and non-operating assets - debt and
  legacy liabilities (pensions, environmental, litigation)

Note: "Excess" cash = total cash minus ~0,25-0,50% of revenue (operational cash needs)

---

## ELEMENT 3: GROWTH VALUE (Least Reliable -- Franchise Businesses Only)

### Step 3a: Determine if Growth Creates Value

Growth creates value ONLY for franchise businesses (Case C: EPV >> Asset Value).

* **Case A (AV > EPV):** Growth destroys value. Do NOT add growth premium.
* **Case B (AV ≈ EPV):** Growth is irrelevant. Do NOT add growth premium.
* **Case C (EPV >> AV):** Growth may create value. Proceed to Step 3b.

### Step 3b: Return-Based Franchise Valuation

For franchise businesses, estimate RETURNS rather than trying to calculate a precise
intrinsic value (which would require unreliable far-future cash flow projections).

**Total expected return = Cash return + Organic growth + Active reinvestment return**

#### Cash Return
* Cash return = Total distributions (dividends + net buybacks) / Market price
* Distributions are funded from earnings power, so:
  Cash return ≈ Payout ratio x (Earnings power / Market price)

#### Organic Growth Return
* Growth that arises naturally from market conditions without active investment
* Estimate from: historical real revenue growth rate + expected inflation
* Working capital needed to support organic growth reduces distributable earnings
* Organic growth return ≈ expected nominal earnings growth rate

#### Active Reinvestment Return
* Retained earnings reinvested in growth initiatives (acquisitions, new products, expansion)
* Reinvestment amount = Earnings power - distributions - organic growth investment
* Value creation factor = Expected return on reinvestment / cost of capital
* Active reinvestment return = (Reinvestment amount x Value creation factor) / Market price
* Value creation factor > 1 only within franchise-protected markets

**Benchmark return** = Cash return + Organic growth + Active reinvestment return

**Compare to cost of capital:**
* Benchmark return > cost of capital + fade rate → attractive investment
* Benchmark return ≈ cost of capital → fairly valued
* Benchmark return < cost of capital → overvalued

### Step 3c: Account for Franchise Fade

* Estimate franchise half-life (years until 50% probability of franchise impairment)
* Annual fade rate ≈ 72 / half-life
* Fade rate must be covered by the margin of safety in returns
* Very durable franchise (50+ yr half-life): ~1-1,5% annual fade
* Durable franchise (25-50 yr): ~1,5-3% annual fade
* Moderate franchise (15-25 yr): ~3-5% annual fade
* Fragile franchise (<15 yr): >5% annual fade

---

## TRIANGULATION AND MARGIN OF SAFETY

### Triangulating Between Asset Value and EPV

* For Case B businesses: average the two estimates, weighting toward the
  more reliable one
  * Cyclical/commodity businesses with unstable earnings → weight toward AV
  * Service businesses with stable earnings but intangible-heavy assets → weight toward EPV
* Both estimates should be mutually supporting. Large divergence requires
  investigation (management quality? accounting manipulation? strategic misassessment?)

### Margin of Safety Calculation

**For non-franchise businesses (Case A and B):**

Margin of Safety = (Intrinsic Value - Market Price) / Intrinsic Value

* Target: >33% (Graham's minimum); ideally ~50%
* Intrinsic value = triangulated AV/EPV estimate

**For franchise businesses (Case C):**

Margin of Safety = Benchmark Return - Cost of Capital - Fade Rate

* Target: >2-3% after deducting fade rate
* Also verify that the enterprise margin of safety (not just equity) is adequate
  -- leverage can create illusory equity bargains

### Why Margin of Safety Matters Beyond a Single Number

The margin of safety exists to absorb three things, all of which routinely
materialize:

1. **Errors in the valuation itself** -- inputs that turn out to be wrong:
   normalized margins too high, cost of capital too low, capex requirements
   understated, hidden liabilities discovered later.
2. **Adverse fundamental change** -- the business you valued is not
   necessarily the business you own three years later. Markets shift,
   technology disrupts, regulation tightens, management changes.
3. **Adverse macro / sentiment shifts** -- the price can decline well below
   intrinsic value before recovering. Margin of safety ensures the valuation
   error or the sentiment overshoot does not turn into permanent loss.

A 33% margin of safety is not "33% guaranteed return." It is a buffer against
all three sources of error simultaneously. If even one materializes, the
remaining buffer protects you. If none materializes, the realized return
exceeds the margin -- but that should be treated as a bonus, not the central
case.

### Strongly Held vs Loosely Held Estimates

A correctly-derived intrinsic value is useful only if held with sufficient
conviction to act on it. The hardest moments in investing -- buying as a
position falls, holding through extended underperformance, refusing to chase
a popular winner -- require a strongly held view.

Sources of strong conviction:
* The estimate is built from multiple independent methods that triangulate
  (AV and EPV, not a single DCF).
* The most reliable element (asset value) anchors the estimate; growth
  contributes only when the franchise case is established.
* The key inputs are derived from observable history (margins, capex,
  asset values), not from forecasts.
* Sensitivity analysis has been performed; the range of intrinsic value is
  understood, not pretended to be a single point.
* The thesis has explicit failure modes -- if X happens, the estimate is
  invalidated. This is what keeps strong conviction from becoming dogma.

A loosely held estimate is worse than no estimate at all. It will not help
you average down through a 30% decline; it will not stop you from
capitulating to bubble euphoria. Either commit to the work required for a
strongly held view, or pass on the position.

An incorrect estimate held strongly is even worse. The defence against this
is intellectual honesty about failure modes and willingness to revise when
the evidence demands it -- distinct from emotional capitulation under price
pressure alone.

### Enterprise vs Equity Margin of Safety

* For highly leveraged companies, ALWAYS check the enterprise margin of safety
* Enterprise market value = Market cap - excess cash + debt
* Enterprise intrinsic value = EPV (before adding cash / subtracting debt)
* Enterprise margin of safety is more reliable because valuation errors relate
  to enterprise size, not equity size
* Example: A 15% error in a $800m enterprise value is $120m. If net debt is
  $650m, equity value swings from $150m to $30m -- a 5x range. The equity
  "bargain" is an illusion created by leverage.

---

## OUTPUT FORMAT

Present the valuation as a structured summary:

### Valuation Summary Table

| Component | Value |
|-----------|-------|
| Net Asset Value (reproduction cost) | $X |
| Earnings Power Value (enterprise) | $X |
| Equity EPV (after debt, plus excess assets) | $X |
| Case Classification | A / B / C |
| Growth Value (if Case C) | Return-based assessment |
| Intrinsic Value Range | $X - $Y |
| Current Market Price | $Z |
| Margin of Safety | X% |

### Key Assumptions

List the 3-5 most important assumptions and their sensitivity:
* What if the operating margin is 2% lower?
* What if the cost of capital is 1% higher?
* What if growth is 2% lower?

---

## REASONABLENESS CHECKS

Before publishing an intrinsic value, sanity-check it against these tests:

1. **"Too good to be true" test**: if the implied return is far above the
   reasonable range for the asset class (single digits to low double digits
   for equities, with cyclical exceptions), demand a satisfying explanation.
   Higher returns require one of: extremely depressed entry environment,
   exceptional skill, real risk borne, leverage, or luck. If none apply,
   reconsider.
2. **"Why me?" test**: if the asset is so clearly mispriced, why is it
   available at this price? Who is the seller, why are they selling,
   why has no one else corrected this? A satisfying answer is required
   (forced seller, headline aversion, mandate exclusion, complexity barrier,
   structural illiquidity). Vague answers usually mean you are missing
   something.
3. **Implied consensus test**: the current market price implies a particular
   set of operating assumptions. Back into them. How does your assumption
   set differ? In which specific variable, and why are you more correct?
4. **Survivorship and base rate test**: the asset class itself has historical
   base rates for return. Does your estimate fall within plausible bounds for
   the asset class, or does it require this specific name to be an extreme
   outlier?

If the valuation cannot survive these tests, it is more likely the analyst
who is mistaken than the market.

---

## ANALYST VERDICT

Must include:

1. **Intrinsic value range**: low, base, and high estimates
2. **Case classification**: A (value trap), B (competitive), or C (franchise)
3. **Margin of safety**: percentage for non-franchise; return spread for franchise
4. **Investment conclusion**: "Attractive at current price", "Fairly valued",
   "Overvalued", or "Insufficient margin of safety"
5. **Key risk**: the single factor most likely to invalidate the valuation
6. **Catalyst** (if Case A): what would unlock value?
7. **Reasonableness assessment**: does the estimate pass the "too good to be
   true" and "why me?" tests, and what is the explanation if it appears to
   show extreme mispricing?
8. **Conviction level**: high / medium / low, with the criteria from
   "Strongly Held vs Loosely Held Estimates" as basis. State explicitly the
   single development that would invalidate the valuation.

---

## STYLE RULES

* Always present Asset Value and EPV separately before combining
* Never calculate intrinsic value using ONLY a DCF model
* Never assume growth creates value without first establishing franchise status
* Be explicit about the reliability of each estimate (AV most reliable, EPV second, growth least)
* State the cost of capital used and justify the risk category
* Flag when depreciation adjustments are material
* Distinguish between equity and enterprise valuations -- never mix them
* Do not present false precision: round to appropriate significant figures
* Always state the margin of safety relative to the estimated intrinsic value
* Distinguish a strongly-held estimate (multiple methods, observable inputs,
  explicit failure modes) from a loosely-held one. A loosely-held estimate
  cannot support contrarian action -- and contrarian action is where the
  return comes from.
* Never identify a "bottom" prospectively. Bottoms are visible only in
  retrospect. The investor's job is not to time the bottom but to buy when
  margin of safety is wide and to keep buying as price falls if intrinsic
  value is unchanged. Insisting on perfection -- buying only at the bottom
  -- causes investors to miss the opportunity entirely.
"""
