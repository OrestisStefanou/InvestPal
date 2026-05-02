analyze_income_statement_skill = """
## CORE LOGIC

### Step 0: Sector Profile Mapping

* asset_light → technology, some healthcare
* capital_intensive → utilities, energy, industrials
* financial_structure → financials
* inventory_driven → retail
* default → other

---

## SECTOR-SPECIFIC RULES

### 1. ASSET-LIGHT (technology)

Expect:

* High margins
* Scalable cost structure

Red flags:

* Declining margins
* High operating expenses without growth

Focus:

* Operating leverage
* Margin expansion

---

### 2. CAPITAL-INTENSIVE (utilities, energy, industrials)

Expect:

* Lower margins
* Stable but slower growth

Focus:

* Margin stability (not absolute level)
* Cost control

---

### 3. FINANCIALS

Adjust:

* Revenue = interest income + fees
* Margins behave differently

Focus:

* Net interest trends (if available)
* Consistency of earnings

Avoid:

* Comparing margins directly with non-financial sectors

---

### 4. INVENTORY-DRIVEN (retail)

Focus:

* Gross margin trends
* Cost of goods sold (COGS)

Red flags:

* Shrinking gross margins
* Rising costs without pricing power

---

## METRIC INTERPRETATION

### Profitability

* Gross Margin = (Revenue - COGS) / Revenue
* Operating Margin = Operating Income / Revenue
* Net Margin = Net Income / Revenue

Adjust expectations by sector:

* Tech → high margins expected
* Utilities → lower but stable margins acceptable

---

### Sustainable Earnings Power (Graham & Dodd Approach)

The goal is not to measure this quarter's margins but to estimate **sustainable
distributable earnings** -- what this business can reliably earn over a full
economic cycle.

**Calculating sustainable margins:**

1. Collect operating margins over 7-15 years (spanning at least one full business cycle,
   ideally two)
2. If margins show a **secular trend with an identifiable economic cause** (e.g.,
   industry consolidation improving pricing, technology shift changing cost
   structure), use the most recent margin adjusted for cyclical position
3. If margins show a trend with **no identifiable cause**, use the arithmetic mean --
   do NOT extrapolate trends. Extrapolation is forecasting, and forecasts
   systematically mislead.
4. Apply the sustainable margin to **current revenue** (unless revenue itself is
   highly cyclical, in which case use average sustainable revenue)
5. The result is an estimate of sustainable operating earnings

**Common pitfalls:**
* Using peak margins during an expansion → overstates earnings power
* Using trough margins during a recession → understates earnings power
* Extrapolating a recent margin improvement into the indefinite future →
  the most common and costly mistake in equity analysis

---

### Growth

Evaluate:

* Revenue growth consistency
* Earnings growth vs revenue

Interpret:

* Earnings growing faster than revenue → efficiency or operating leverage
* Revenue growing without profits → risk, especially if management is
  spending on growth that earns below cost of capital

**Value investing perspective on growth:**
* Revenue growth in a **competitive business** (no moat) does not create value --
  it merely attracts entry and competition until returns fall to cost of capital
* Revenue growth in a **franchise business** creates value only when invested
  within or adjacent to protected markets
* Declining revenue in a competitive business is not catastrophic if capital
  recoveries offset lost earnings

---

### Expense Quality and Hidden Investments

**Overhead expense analysis:**
* Operating expenses (R&D, marketing, SGA) can be manipulated up or down by
  management to distort current earnings
* Cutting R&D raises operating income today but may impair future earnings power.
  Flag unexplained drops in R&D as % of revenue.
* Rising SGA faster than revenue → loss of operating discipline OR investment in
  growth (determine which)

**Growth-related expenses buried in operating costs:**
* R&D, marketing, and hiring that exceeds the level needed to maintain the
  current business is effectively investment, not cost
* For growing companies, these "excess" expenses reduce reported margins but
  represent investment in intangible assets (product portfolios, customer bases,
  trained workforce)
* When comparing margins across companies, adjust for differences in growth
  investment disguised as operating expense
* A company spending 18% of revenue on R&D while growing at 20% has different
  economics than one spending 18% on R&D while growing at 3%

**Pricing power assessment:**
* Can the company raise prices to offset cost increases? This is the income
  statement signature of a franchise business.
* Stable or expanding gross margins during periods of input cost inflation → pricing power
* Compressing gross margins during cost pressure → no pricing power, competitive business
* Pricing power is the most reliable indicator of sustainable margins

---

### Efficiency

Analyze:

* Operating expense trends
* Cost discipline
* Returns on invested capital (ROIC) -- the ultimate measure of whether revenue
  and margins translate into value creation

---

### Earnings Quality

Evaluate:

* One-off gains/losses
* Volatility in net income

Flag:

* Earnings not supported by core operations
* Recurring "one-time" charges (if they happen every year, they are not one-time)

---

### Trends

Focus on:

* Margin expansion or compression
* Growth sustainability
* Whether margin trends reflect cyclical factors or structural changes

---

### Red Flags (Context-Aware)

* asset_light → falling margins, R&D cuts to boost short-term earnings
* capital_intensive → unstable earnings, margins at cyclical extremes
* retail → margin compression, loss of pricing power
* all → inconsistent earnings, large one-offs, earnings growing while revenue stagnates

---

## ANALYST VERDICT

Include:

1. Classification: "Strong", "Moderate", "Weak"
2. Sector-aware interpretation
3. Key driver of performance
4. **Sustainable margin estimate**: What is the best estimate of through-cycle
   operating margin? Is the current margin above, below, or at sustainable levels?
5. **Pricing power assessment**: Does the company demonstrate ability to maintain
   or raise prices? (strong indicator of franchise status)

---

## STYLE RULES

* Focus on drivers, not just metrics
* Always explain "why margins are changing"
* Highlight sustainability of earnings
* Use through-cycle averages, not single-period snapshots, for assessing earnings power
* Distinguish between margin changes that are cyclical (temporary) and structural
  (permanent)
* Never extrapolate recent margin trends without an identifiable economic cause
"""
