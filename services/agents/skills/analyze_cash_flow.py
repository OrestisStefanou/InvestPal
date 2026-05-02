analyze_cash_flow_skill = """
## CORE LOGIC

### Step 0: Sector Profile Mapping

* asset_light → technology
* capital_intensive → utilities, energy, industrials
* financial_structure → financials
* inventory_driven → retail
* default → other

---

## SECTOR-SPECIFIC RULES

### 1. ASSET-LIGHT (technology)

Expect:

* Strong operating cash flow
* High free cash flow

Red flags:

* Profits without cash flow
* Declining cash conversion

Focus:

* Cash conversion (earnings → cash)

---

### 2. CAPITAL-INTENSIVE (utilities, energy)

Expect:

* High capital expenditures (CapEx)
* Lower free cash flow

Accept:

* Negative FCF if investments are stable and planned

Focus:

* Sustainability of CapEx
* Financing of investments

---

### 3. FINANCIALS

Adjust:

* Cash flow statement is less informative

Focus:

* Broad cash trends
* Avoid over-reliance on FCF

---

### 4. INVENTORY-DRIVEN (retail)

Focus:

* Working capital changes

Red flags:

* Inventory absorbing cash
* Weak operating cash flow despite profits

---

## METRIC INTERPRETATION

### Cash Generation

* Operating Cash Flow (OCF)
* Free Cash Flow (FCF) = OCF - CapEx

Interpret:

* Positive and growing → strong
* Negative → depends on sector and growth stage

---

### Cash Quality

Evaluate:

* OCF vs Net Income

Interpret:

* OCF < Net Income → potential earnings quality issue
* OCF > Net Income → strong cash conversion

---

### Maintenance CapEx vs Growth CapEx (Critical Distinction)

Total CapEx reported on the cash flow statement includes BOTH:
* **Maintenance CapEx** -- investment needed to restore assets to start-of-year condition
  (true economic depreciation)
* **Growth CapEx** -- investment to expand capacity, enter new markets, develop new products

This distinction is essential because:
* **FCF = OCF - Total CapEx** understates distributable cash for growing companies
  (it includes growth investment alongside maintenance)
* **Owner Earnings** (Buffett's preferred measure) = Net Income + D&A - Maintenance CapEx.
  This is the cash actually available for distribution or reinvestment at management's
  discretion.
* The gap between accounting depreciation and maintenance CapEx directly affects
  earnings power calculations

**Method A -- Zero-growth periods:**
* Find periods when the company (or comparable peers) had minimal revenue growth
* Total CapEx in those periods ≈ maintenance CapEx (since growth CapEx should be near zero)
* Compare this figure to accounting depreciation in the same period

**Method B -- Capital intensity ratio:**
* Calculate capital intensity = Net fixed assets / Revenue (average over several years)
* Growth CapEx ≈ Revenue growth x capital intensity ratio
* Maintenance CapEx ≈ Total CapEx - Growth CapEx

**Interpretation:**
* If maintenance CapEx < accounting D&A → company is spending LESS to maintain
  assets than accounting charges. True earnings power is HIGHER than reported.
  Common causes: equipment prices falling due to technology, buildings depreciating
  on paper faster than they deteriorate physically.
* If maintenance CapEx > accounting D&A → company is spending MORE to maintain
  assets than accounting charges. True earnings power is LOWER than reported.
  Common causes: inflation in construction/equipment costs, deferred maintenance
  catching up.
* If maintenance CapEx ≈ accounting D&A → reported earnings are a reasonable proxy
  for distributable cash.

---

### Capital Allocation Quality

How management deploys cash beyond maintenance is a critical driver of long-term
value creation:

**Returns on reinvested capital:**
* Compare ROIC on growth investments to cost of capital
* ROIC > cost of capital → management is creating value through reinvestment
* ROIC < cost of capital → management is destroying value (common in Case A businesses)
* ROIC ≈ cost of capital → reinvestment is neutral (typical for competitive businesses)

**Allocation priorities (evaluate the pattern):**
* Dividends → returning cash to owners. Appropriate when reinvestment opportunities
  are limited or earn below cost of capital.
* Share buybacks → only value-creating if done below intrinsic value. Buybacks above
  intrinsic value transfer wealth from continuing to departing shareholders.
* Debt repayment → reduces leverage risk. Especially valuable for companies near
  distress thresholds.
* Growth investment → only valuable for franchise businesses investing within or
  adjacent to their competitive advantages.
* Acquisitions → scrutinize price paid vs value received. Many acquisitions destroy
  value through overpayment (goodwill on the balance sheet often represents
  overpayment, not reproducible economic value).

---

### Trends

Focus on:

* Consistency of cash generation
* Improving or deteriorating FCF
* Maintenance CapEx trend vs D&A trend (are they converging or diverging?)
* Changes in capital allocation priorities over time

---

### Red Flags (Context-Aware)

* asset_light → weak cash conversion
* capital_intensive → unsustainable CapEx, maintenance CapEx significantly exceeding D&A
* retail → cash tied in inventory
* all → persistent negative OCF, acquisitions funded by debt with ROIC below cost of capital,
  buybacks at prices above intrinsic value

---

## ANALYST VERDICT

Include:

1. Classification: "Strong", "Moderate", "Weak"
2. Sustainability of cash generation
3. **Maintenance CapEx assessment**: Is accounting D&A a reasonable proxy for true
   maintenance costs? If not, what is the estimated gap?
4. **Capital allocation quality**: Is management creating or destroying value with
   reinvested cash?
5. Key insight (e.g., "profits not converting to cash" or "true earnings power is
   higher than reported due to excess depreciation")

---

## STYLE RULES

* Cash > accounting profits (prioritize cash reality)
* Always compare profit vs cash flow
* Always distinguish maintenance from growth CapEx when data permits
* Never use EBITDA as a proxy for cash earnings -- it assumes zero maintenance cost
* Evaluate buybacks and acquisitions by whether they were done at prices creating value
* Highlight sustainability
"""
