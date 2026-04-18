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

### Growth

Evaluate:

* Revenue growth consistency
* Earnings growth vs revenue

Interpret:

* Earnings growing faster than revenue → efficiency
* Revenue growing without profits → risk

---

### Efficiency

Analyze:

* Operating expense trends
* Cost discipline

---

### Earnings Quality

Evaluate:

* One-off gains/losses
* Volatility in net income

Flag:

* Earnings not supported by core operations

---

### Trends

Focus on:

* Margin expansion or compression
* Growth sustainability

---

### Red Flags (Context-Aware)

* asset_light → falling margins
* capital_intensive → unstable earnings
* retail → margin compression
* all → inconsistent earnings, large one-offs

---

## ANALYST VERDICT

Include:

1. Classification: "Strong", "Moderate", "Weak"
2. Sector-aware interpretation
3. Key driver of performance

---

## STYLE RULES

* Focus on drivers, not just metrics
* Always explain “why margins are changing”
* Highlight sustainability of earnings
"""