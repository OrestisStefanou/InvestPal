analyze_balance_sheet_skill = """
## CORE LOGIC

### Step 0: Determine Sector Profile

Map industry into one of the following behavior profiles:

* asset_light → technology, some healthcare
* capital_intensive → utilities, energy, industrials
* financial_structure → financials (banks, insurers)
* inventory_driven → retail
* default → other

---

## SECTOR-SPECIFIC RULES

### 1. ASSET-LIGHT (e.g., technology)

Interpretation adjustments:

* Expect:

  * Low debt
  * High cash reserves
  * High margins
* Red flags:

  * Rising debt
  * Low liquidity
* Asset quality:

  * Intangibles are normal but monitor goodwill growth

Modify behavior:

* Be stricter on leverage
* Emphasize cash position

---

### 2. CAPITAL-INTENSIVE (e.g., utilities, energy, industrials)

Interpretation adjustments:

* Expect:

  * High debt levels
  * Large fixed assets
* Accept:

  * Higher debt-to-equity ratios
* Focus:

  * Stability of capital structure, not absolute debt

Modify behavior:

* Do NOT flag high debt alone as a red flag
* Evaluate whether debt appears sustainable

---

### 3. FINANCIAL STRUCTURE (e.g., banks, insurers)

Interpretation adjustments:

* DO NOT rely on:

  * Standard debt-to-equity interpretation
* Recognize:

  * Liabilities (deposits) are core to the business

Modify behavior:

* Skip or de-emphasize:

  * Debt-to-equity conclusions
* Focus instead on:

  * Balance sheet composition
  * Asset quality (loan book risks if visible)

---

### 4. INVENTORY-DRIVEN (e.g., retail)

Interpretation adjustments:

* Focus on:

  * Inventory as % of current assets
* Risk:

  * High current ratio driven by inventory is misleading

Modify behavior:

* Downgrade liquidity assessment if inventory dominates
* Highlight working capital efficiency

---

### 5. DEFAULT (other sectors)

* Apply standard rules
* Add caveat: “Interpretation may vary by industry”

---

## METRIC INTERPRETATION (ADJUSTED BY SECTOR)

### Liquidity

* Current Ratio:

  * <1 → risk
  * 1–1.5 → adequate
  * > 1.5 → strong
* Override:

  * inventory-heavy → reduce quality of liquidity
  * asset-light → expect higher ratios

---

### Solvency

* Debt-to-Equity:

  * asset_light → >1.5 = concern
  * capital_intensive → up to ~2–3 may be acceptable
  * financial_structure → not meaningful

---

### Asset Quality

Evaluate:

* Intangibles %:

  * asset_light → acceptable
  * others → potential concern if high
* Receivables growth:

  * flag if rising faster than expected

**Graham & Dodd Asset Reproduction Cost Assessment:**

When evaluating balance sheet strength, consider the gap between book values and
reproduction costs:

* **Goodwill (accounting):** Often represents overpayment in past acquisitions, not
  reproducible economic value. Treat accounting goodwill with skepticism — a new
  entrant does not need to reproduce acquisition premiums. Estimate the underlying
  intangible assets (product portfolio, customer base, trained workforce) from first
  principles instead.
* **Intangible assets not on the balance sheet:** Many companies have significant
  unrecorded intangible assets — product portfolios (estimate as R&D spend x years
  of product life), customer relationships (revenue acquisition costs), trained workforce
  (recruitment and training costs), organizational infrastructure (1-3 years of admin costs).
  These are real assets that a competitor must reproduce to enter the business.
* **PP&E book vs reproduction value:** Land may be worth far more than book (inflation,
  economic growth). Buildings depreciate slower than accounting assumes. Equipment prices
  may be falling (technology-driven), making replacement cheaper than original cost.
  Estimate equipment at ~50% of original cost x price trend adjustment.
* **LIFO reserve:** If the company uses LIFO accounting for inventory, the stated book
  value may understate reproduction cost. The LIFO reserve (disclosed in footnotes)
  should be added back.

---

### Capital Structure

Assess:

* Sustainability of financing model relative to sector
* Flexibility under stress
* **Net asset value comparison:** Does the market price reflect a reasonable premium or
  discount to estimated net asset reproduction value? A market price significantly below
  reproduction cost may signal opportunity (or management quality concerns).

---

### Trends

Prioritize:

* Changes that contradict sector norms

  * e.g., rising debt in tech
  * declining equity in banks
  * inventory buildup in retail

---

### Red Flags (Context-Aware)

Flag only if abnormal *for the sector*:

* asset_light → rising leverage, falling cash
* capital_intensive → unstable debt growth
* financials → deteriorating asset mix
* retail → inventory buildup
* all → negative equity, liquidity stress

---

## ANALYST VERDICT

Must include:

1. Classification: “Strong”, “Moderate”, or “Risky”
2. Sector-aware reasoning:

   * “High leverage is acceptable given capital-intensive nature”
   * OR
   * “Leverage is elevated relative to typical technology companies”
3. One key insight:

   * The single most important takeaway
4. **Reproduction cost assessment** (where data permits):

   * Are book values likely to understate or overstate true asset reproduction costs?
   * Are there significant unrecorded intangible assets?
   * What is the estimated gap between book equity and reproduction cost net asset value?

---

## STYLE RULES

* Always interpret in context of sector
* Avoid generic statements
* Explicitly mention when something is “normal for the industry”
* Be skeptical of outliers

---
"""