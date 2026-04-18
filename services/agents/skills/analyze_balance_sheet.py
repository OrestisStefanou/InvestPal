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

---

### Capital Structure

Assess:

* Sustainability of financing model relative to sector
* Flexibility under stress

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

1. Classification: "Strong", "Moderate", or "Risky"
2. Sector-aware reasoning:

   * “High leverage is acceptable given capital-intensive nature”
   * OR
   * “Leverage is elevated relative to typical technology companies”
3. One key insight:

   * The single most important takeaway

---

## STYLE RULES

* Always interpret in context of sector
* Avoid generic statements
* Explicitly mention when something is “normal for the industry”
* Be skeptical of outliers

---
"""