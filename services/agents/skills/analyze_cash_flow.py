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

### Capital Allocation

Analyze:

* CapEx levels
* Dividends
* Share buybacks
* Debt repayment

---

### Liquidity & Runway

Assess:

* Cash reserves vs burn rate

Especially important for:

* Growth companies

---

### Trends

Focus on:

* Consistency of cash generation
* Improving or deteriorating FCF

---

### Red Flags (Context-Aware)

* asset_light → weak cash conversion
* capital_intensive → unsustainable CapEx
* retail → cash tied in inventory
* all → persistent negative OCF

---

## ANALYST VERDICT

Include:

1. Classification: "Strong", "Moderate", "Weak"
2. Sustainability of cash generation
3. Key insight (e.g., “profits not converting to cash”)

---

## STYLE RULES

* Cash > accounting profits (prioritize cash reality)
* Always compare profit vs cash flow
* Highlight sustainability
"""