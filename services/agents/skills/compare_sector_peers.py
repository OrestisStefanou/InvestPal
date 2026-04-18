compare_sector_peers_skill = """
## CORE LOGIC

### Step 0: Define the Peer Group

Identify the target company and its relevant peer group:

1. **Same sector and industry**: Use the company's sector/industry classification
2. **Similar business model**: Revenue model should be comparable (e.g., SaaS vs perpetual license are different even in same sector)
3. **Comparable size**: Prefer peers within 1–3x of target's market cap (unless comparing to sector leaders intentionally)
4. **Geographic relevance**: Prefer same primary market when applicable

Aim for 3–6 meaningful peers. More is not better — quality of comparability matters.

Note limitations: Flag when peer selection is difficult (e.g., unique business models, niche markets).

---

## COMPARISON FRAMEWORK

Analyze the target company vs peers across four categories:

---

### 1. GROWTH METRICS

Compare:
* Revenue growth (YoY %, 3-year CAGR if available)
* Earnings / EPS growth
* FCF growth

Interpretation:
* Target growing faster than median peer → growth premium may be justified
* Target growing slower than peers → investigate: market share loss, saturation, or deliberate slowdown?
* Deceleration trend → flag even if absolute growth still looks high

Assign relative ranking:
* "Above peers", "In-line with peers", "Below peers"

---

### 2. PROFITABILITY METRICS

Compare:
* Gross margin
* Operating margin
* Net margin
* Return on Equity (ROE)
* Return on Invested Capital (ROIC) — best measure of capital efficiency

Interpretation:
* Higher margins → pricing power, competitive moat, or superior cost structure
* Margin gap widening vs peers → structural advantage or disadvantage
* ROIC > WACC → company is creating value; ROIC < WACC → destroying value

Sector-specific adjustments:
* asset_light: focus on operating and net margins, FCF margins
* capital_intensive: focus on ROIC, EBITDA margins (strips out D&A differences)
* financial: focus on ROE, net interest margin, efficiency ratio
* retail: focus on gross margin and operating leverage

---

### 3. VALUATION MULTIPLES

Compare target's multiples vs peer median:

* P/E (if profitable)
* EV/EBITDA
* EV/Revenue (especially for growth or pre-profit companies)
* P/FCF or FCF yield
* P/B (for asset-heavy or financial companies)

Interpretation matrix:

| Target vs Peers | Quality vs Peers | Conclusion |
|----------------|-----------------|------------|
| Premium valuation | Superior fundamentals | Justified premium |
| Premium valuation | In-line fundamentals | Potentially overvalued |
| Premium valuation | Inferior fundamentals | Overvalued — red flag |
| Discount valuation | Superior fundamentals | Potential opportunity |
| Discount valuation | In-line fundamentals | Fairly valued / value |
| Discount valuation | Inferior fundamentals | Value trap risk |

Always explain the premium or discount — do not just report the number.

---

### 4. BALANCE SHEET & FINANCIAL HEALTH

Compare:
* Debt-to-Equity or Net Debt / EBITDA
* Current ratio / quick ratio
* Interest coverage ratio

Interpretation:
* Target with lower leverage → financial flexibility advantage
* Target with higher leverage → risk if cash flows weaken; may be acceptable if intentional (e.g., leveraged buyout, capital return program)
* Flagging: Significantly more debt than peers without a clear strategic rationale

---

## COMPETITIVE POSITIONING ASSESSMENT

Beyond the numbers, assess qualitative competitive position:

### Market Share & Growth Trajectory
* Is the company gaining or losing market share relative to peers?
* Is it growing into new markets while peers are saturating existing ones?

### Moat Indicators (from financials)
* **Pricing power**: Gross margins stable or expanding despite cost pressures → moat
* **Switching costs**: High recurring revenue, low churn signals → moat
* **Scale advantages**: Lower cost per unit vs peers at same or larger scale → moat
* **Network effects**: Platforms with engagement metrics growing faster than peers → moat

### Capital Allocation Quality
* Compare capital return programs: dividends + buybacks as % of FCF
* R&D / CapEx as % of revenue — is investment proportional to growth?
* Acquisition history: have past acquisitions created or destroyed value?

---

## RELATIVE RANKING SUMMARY

After all analyses, produce a structured ranking:

| Metric | Target | Peer Median | Rank vs Peers |
|--------|--------|-------------|---------------|
| Revenue growth | X% | Y% | Above / In-line / Below |
| Operating margin | X% | Y% | Above / In-line / Below |
| EV/EBITDA | Xx | Yx | Premium / Fair / Discount |
| Net debt/EBITDA | Xx | Yx | Lower / Similar / Higher |
| ROIC | X% | Y% | Above / In-line / Below |

Provide an overall relative standing: "Top quartile", "Above average", "Average", "Below average"

---

## ANALYST VERDICT

Must include:

1. **Competitive position**: "Leader", "Above Average", "In-line", "Laggard"
2. **Valuation vs peers**: "Premium justified", "Fairly valued vs peers", "Expensive vs peers", "Cheap vs peers"
3. **Key differentiator**: the single most important factor that separates this company from peers
4. **Risk of peer comparison**: flag any limitations in the peer group selected
5. **Actionable takeaway**: What does this comparison imply for the investment decision?

---

## STYLE RULES

* Always name specific peers used in the comparison — never be vague
* Flag when peer group is limited or imperfect
* Explain *why* a premium or discount exists, not just that it exists
* Use the table format for the ranking summary — structured comparisons are clearer
* Never declare a company the "best" in its sector from metrics alone — identify specific advantages
"""
