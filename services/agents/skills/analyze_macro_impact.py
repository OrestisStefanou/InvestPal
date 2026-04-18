analyze_macro_impact_skill = """
## CORE LOGIC

### Step 0: Gather Current Macro Context

Retrieve current readings for key economic indicators:
* Interest rates (central bank policy rate, 10Y Treasury yield)
* Inflation (CPI, PCE)
* GDP growth (current and forecast)
* Unemployment rate
* Manufacturing and services PMI
* Consumer sentiment / confidence index
* Yield curve shape (normal, flat, inverted)
* Credit spreads (investment grade and high yield)
* Commodity prices (oil, gold, copper) if relevant
* USD strength (DXY) for international holdings

Identify the current macro **regime** before proceeding.

---

## MACRO REGIME IDENTIFICATION

Classify the current environment into one of these regimes:

### 1. EXPANSION (growth up, inflation moderate)
* Strong GDP, low unemployment, moderate inflation, rising earnings
* Generally favorable for equities, especially cyclicals and growth
* Central bank: accommodative or neutral

### 2. OVERHEATING (growth up, inflation high)
* Strong GDP but inflation rising uncomfortably
* Central bank: tightening cycle
* Risk: policy mistake → recession
* Favors: real assets, commodities, value over growth

### 3. STAGFLATION (growth down, inflation high)
* Worst macro regime for most assets
* Real returns erode; bonds and growth stocks hit hardest
* Favors: commodities, energy, inflation-linked bonds, gold

### 4. RECESSION (growth down, inflation falling)
* Earnings decline, credit stress, unemployment rising
* Central bank: easing or about to ease
* Defensives outperform; cyclicals, small caps, high yield hit hardest
* Later in recession: growth assets may begin recovering in anticipation of recovery

### 5. RECOVERY (growth recovering, inflation low)
* Earnings rebounding, monetary policy still accommodative
* Broad equity rally typical; cyclicals and growth lead
* Small caps often outperform early in recovery

### 6. RATE PLATEAU / UNCERTAINTY
* Central bank near peak rates, direction unclear
* Markets sensitive to inflation data and Fed language
* Sector rotation common; high uncertainty on timing

State the regime and provide supporting evidence from current indicators.

---

## INTEREST RATE IMPACT ANALYSIS

Interest rates are the most powerful macro driver. Analyze their impact:

### On Equity Valuations:
* Rising rates → higher discount rate → lower present value of future earnings → multiples compress
* Most impacted: long-duration assets (high-growth, high-multiple stocks)
* Least impacted: near-term earners, value stocks, dividend payers
* Rate-sensitive sectors (most affected by rising rates):
  * Technology / Growth → negative (high duration)
  * Real Estate (REITs) → negative (higher cap rates, higher financing costs)
  * Utilities → negative (bond-like, dividend yield less attractive)
* Rate-sensitive sectors (may benefit from rising rates):
  * Financials (banks) → positive (wider net interest margins)
  * Insurance → positive (higher investment returns on float)

### On Fixed Income (if applicable):
* Rising rates → existing bond prices fall (inverse relationship)
* Longer duration bonds: more sensitive to rate changes
* Short-duration / floating rate: less affected
* High yield spreads: watch for widening = increasing credit stress

### On Crypto:
* Highly correlated with risk appetite
* Rising rates / tightening → risk-off → crypto typically sells off
* Easing cycle → risk-on → crypto benefits

---

## INFLATION IMPACT ANALYSIS

### High inflation environment:

**Favored:**
* Commodities (oil, metals, agricultural)
* Energy stocks
* Real assets (real estate, infrastructure)
* Companies with strong pricing power (wide moats)
* TIPS / inflation-linked bonds

**Hurt:**
* Fixed income (purchasing power eroded)
* Growth stocks (higher discount rates, margin compression)
* Consumer discretionary (cost of living pressure on consumers)
* Companies with thin margins and no pricing power

### Low/falling inflation environment:

**Favored:**
* Growth stocks (lower rates, lower discount rates)
* Long-duration bonds
* Consumer discretionary (more disposable income)

---

## GDP & ECONOMIC CYCLE IMPACT

Map asset classes and sectors to economic cycle phase:

| Sector | Expansion | Peak | Recession | Recovery |
|--------|-----------|------|-----------|----------|
| Consumer Discretionary | ++ | + | -- | + |
| Consumer Staples | + | + | ++ | + |
| Financials | ++ | + | -- | + |
| Healthcare | + | ++ | ++ | + |
| Industrials | ++ | + | -- | ++ |
| Technology | ++ | + | - | ++ |
| Energy | + | ++ | - | + |
| Materials | ++ | + | -- | ++ |
| Real Estate | + | - | - | + |
| Utilities | - | + | ++ | - |
| Communication Services | + | + | - | + |

Apply this table to assess whether current holdings are positioned for the macro regime.

---

## CURRENCY & INTERNATIONAL IMPACT

If user holds international assets or companies with significant foreign revenue:

* **Strong USD** → headwind for US multinationals (foreign revenue worth less when repatriated)
* **Weak USD** → tailwind for US multinationals, headwind for USD-denominated commodities
* Emerging markets: particularly sensitive to USD strength (dollar-denominated debt burden)
* Check: Does the company hedge currency exposure?

---

## PORTFOLIO IMPACT ASSESSMENT

After establishing the macro context, assess the user's specific portfolio:

1. **Identify macro-sensitive positions**: Which holdings are most exposed to the current macro regime?
2. **Alignment check**: Does the current portfolio positioning align with the macro environment?
3. **Stress test**: In the most likely adverse scenario, which holdings would be hit hardest?
4. **Opportunities**: Are there sectors or assets that typically outperform in the current regime that are underrepresented?

---

## MACRO RISK FLAGS

Flag the following conditions when present:

* Inverted yield curve → historically precedes recession (12-18 month lag)
* Credit spread widening → financial stress increasing
* PMI below 50 → manufacturing contraction
* Consumer confidence falling sharply → spending slowdown risk
* Commodity price spike (especially oil) → inflation reacceleration risk
* Central bank policy error signals → watch for aggressive language changes

---

## ANALYST VERDICT

Must include:

1. **Current macro regime**: clearly stated with supporting evidence
2. **Key macro risk**: the single most important macro factor for the user's portfolio right now
3. **Portfolio alignment**: does current allocation fit the macro environment?
4. **Recommended adjustments** (if any): specific sector tilts or asset class shifts suggested by the macro picture
5. **Time horizon context**: macro impacts play out over different timeframes — distinguish short-term (months) vs structural (years)

---

## STYLE RULES

* Always start with the regime — macro analysis without regime context is meaningless
* Be specific about which holdings are affected and how
* Distinguish cyclical macro risks from structural secular trends
* Avoid macro determinism — acknowledge uncertainty and multiple scenarios
* Frame macro in terms of the user's goals and time horizon, not abstract theory
"""
