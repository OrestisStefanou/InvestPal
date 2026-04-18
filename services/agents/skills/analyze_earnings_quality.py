analyze_earnings_quality_skill = """
## CORE LOGIC

### Step 0: Establish Baseline

Collect for the most recent 2–4 reporting periods:
* Net income / EPS
* Operating cash flow (OCF)
* Free cash flow (FCF)
* Revenue
* Gross and operating margins
* Any non-recurring items disclosed

Goal: Determine whether reported earnings reflect true economic performance or are inflated/distorted.

---

## EARNINGS QUALITY DIMENSIONS

Analyze earnings across the following dimensions:

---

### 1. CASH CONVERSION (Most Important Signal)

**Accrual ratio** = (Net Income - OCF) / Average Total Assets

Interpret:
* Low/negative accrual → earnings are cash-backed → high quality
* High positive accrual → earnings are accrual-heavy → potential concern

**OCF vs Net Income:**

* OCF consistently > Net Income → strong quality (cash-backed earnings)
* OCF consistently < Net Income → earnings may not be converting to cash

  Red flags:
  * Net income growing while OCF is flat or declining
  * Large gap between net income and OCF without explanation
  * FCF consistently below reported earnings

Cause investigation:
* Rising accounts receivable (revenue recognized before cash received)
* Inventory buildup (costs deferred)
* Aggressive capitalization of expenses

---

### 2. REVENUE QUALITY

Assess whether revenue is real, recurring, and sustainable:

**Recurring vs one-time revenue:**
* Subscription / recurring → high quality
* One-time contracts, asset sales, licensing → lower quality
* Flag: Revenue spike driven by a single large deal

**Accounts Receivable (AR) growth:**
* AR growing faster than revenue → potential channel stuffing or aggressive recognition
* Days Sales Outstanding (DSO) = AR / (Revenue / 365)
  * Rising DSO → customers paying slower or revenue being recognized early

**Revenue recognition red flags:**
* Bill-and-hold arrangements
* Round-trip transactions
* Unusual revenue acceleration near quarter-end

---

### 3. EXPENSE MANAGEMENT & COST QUALITY

**Gross margin trends:**
* Stable or expanding → pricing power, cost discipline
* Compressing → competitive pressure or cost inflation

**Operating expense trends:**
* Are operating costs growing proportionally to revenue?
* Flag: Revenue slowing but expenses still growing — margin squeeze ahead

**Capitalization of expenses:**
* Companies can boost near-term earnings by capitalizing costs (R&D, software development) rather than expensing
* Rising intangible assets or capitalized development costs vs peers → investigate
* Flag: Large "Other Assets" growth without clear explanation

**D&A (Depreciation & Amortization) trends:**
* Rising D&A without corresponding asset growth → past over-investment
* Extending asset useful lives → lowers D&A, inflates earnings → red flag

---

### 4. NON-RECURRING ITEMS

Identify all one-time or non-recurring items:

Types:
* Restructuring charges
* Gains/losses on asset sales
* Write-downs and impairments
* Legal settlements
* Tax benefits or charges

Assessment:
* Occasional restructuring → normal
* **Recurring "one-time" charges → not truly one-time** → adjust adjusted earnings skeptically
* Large gains masking operating weakness → flag
* Impairments may signal prior overvaluation of assets (goodwill, investments)

"Adjusted EPS" scrutiny:
* Compare GAAP earnings vs "adjusted" earnings disclosed by management
* Large and consistent gap → management may be excluding real costs
* Stock-based compensation exclusion → real cost, real dilution — flag if large vs revenue

---

### 5. TAX QUALITY

**Effective tax rate:**
* Unusually low effective tax rate vs statutory rate → investigate
* Common causes: deferred tax benefits, tax credits, offshore structuring
* Flag: Earnings boosted by one-time tax benefit — strip it out for quality assessment

**Deferred tax liabilities:**
* Growing deferred tax liabilities → taxes will be paid later — not a long-term earnings booster

---

### 6. EARNINGS CONSISTENCY & PREDICTABILITY

Evaluate:
* Quarter-over-quarter and year-over-year consistency of earnings
* Frequency of earnings "beats" at exactly 1 cent or small amounts → potential earnings management
* Smooth earnings trajectory with little variance → possible smoothing

Red flags:
* Large swings in quarterly earnings without clear business cause
* Frequent restatements or audit adjustments
* Auditor changes → investigate reason
* Going concern notes in financial statements

---

### 7. EARNINGS TRANSCRIPT SIGNALS (if available)

When analyzing earnings call transcripts:

Listen for:
* Management tone on guidance: confident vs hedging
* Changes in language around key metrics (switching from GAAP to non-GAAP, or changing key metrics)
* Analyst pushback on specific line items
* Avoidance of specific questions

Positive signals:
* Management provides specific, quantitative guidance
* Acknowledges risks clearly
* FCF guidance alongside earnings guidance

Negative signals:
* Vague or overly optimistic language
* Shifting KPIs each quarter
* Blaming macro for company-specific problems

---

## SECTOR-SPECIFIC ADJUSTMENTS

### TECHNOLOGY (asset_light)
* Stock-based compensation is large — always include in true cost assessment
* Deferred revenue changes are important: growing deferred revenue = future revenue booked
* Watch: capitalizing software development costs

### FINANCIALS
* Loan loss provisions are the key earnings quality driver
* Under-provisioning inflates earnings → check historical provisioning vs actual losses
* Net interest margin consistency

### CAPITAL-INTENSIVE
* Depreciation policies matter significantly — asset life assumptions affect earnings
* Compare D&A as % of CapEx: ratio < 1 over long periods = underinvestment

### RETAIL
* Inventory valuation (FIFO vs LIFO, write-downs)
* Gross margin is primary quality indicator

---

## ANALYST VERDICT

Must include:

1. **Earnings quality rating**: "High", "Moderate", "Low", or "Questionable"
2. **Primary quality driver**: the most important positive or negative factor
3. **Adjusted earnings estimate**: if reported earnings appear materially distorted, provide a cleaner estimate
4. **Red flags found**: explicit list of any concerning signals with evidence
5. **Confidence level**: how reliable are these earnings as a basis for valuation?

---

## STYLE RULES

* Prioritize cash over accruals — always
* Be specific: name the exact line items causing concern
* Separate structural issues from temporary items
* Acknowledge when earnings appear clean and high-quality — avoid false skepticism
* Never dismiss "adjusted earnings" entirely — but always scrutinize what's being excluded
"""
