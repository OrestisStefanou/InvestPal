analyze_management_commentary_skill = """
## CORE LOGIC

### Purpose

Management commentary is the one part of a disclosure that management chooses
freely. The numbers are constrained by accounting standards; the framing around
them is not. That makes commentary simultaneously the richest source of forward
information and the easiest place to be misled.

The task is not to summarise what management said. It is to work out what the
choice of words, metrics, and omissions reveals about what management actually
believes.

### What Commentary Can and Cannot Tell You

Commentary is **evidence about management's confidence and priorities**. It is
not evidence about the business. A CEO saying "demand is inflecting" tells you
what the CEO wants you to believe, not what demand is doing. Every commentary
claim must be pinned against a hard number before it counts as a finding.

The exception is the negative signal. Management rarely volunteers bad news, so
when it appears, it is usually understated rather than exaggerated. Treat
volunteered bad news as more reliable than volunteered good news.

---

## STEP 0: ASSEMBLE THE EVIDENCE BASE

Before analysing, establish what evidence you actually have. Commentary analysis
is valid at any level of this ladder, but the conclusion must be labelled with
the grade it rests on.

**Grade A -- primary record.** The filed narrative sections of the annual or
quarterly report, the management discussion and analysis, the shareholder
letter, the risk-factor section, and the segment disclosures. These are written
by management, filed under liability, and quotable.

**Grade B -- secondary reporting.** Contemporaneous coverage that paraphrases or
quotes management. Usable, but a paraphrase is not a quotation and must never be
presented as one.

**Grade C -- numeric residue.** No narrative at all, only what the numbers imply
about management behaviour:
* The guidance range itself: its width, its midpoint, whether it was raised,
  cut, reaffirmed, or withdrawn
* Changes in which metrics are reported, and changes in how a metric is defined
* Segment reclassification or a change in reporting structure
* The non-GAAP to GAAP bridge and what is being excluded this period
* Capital allocation actually executed: buyback pace, dividend changes, capex,
  headcount, acquisitions
* Insider transactions filed after the reporting date

**Grade D -- absent.** No usable evidence. Say so and stop; do not reconstruct
commentary from general knowledge of the company.

A grade-C-only analysis is legitimate and often sharp. Metric stability and
say-versus-do, two of the strongest dimensions below, are fully observable from
numbers alone. State the grade; do not pretend to a transcript you do not have.

---

## THE DELTA METHOD

The single most important technique. Commentary in isolation is nearly
uninformative because management always sounds broadly confident. Commentary is
informative **as a change against the prior period on the same axis**.

Always compare against at least one prior period:

| Axis | What a change reveals |
| --- | --- |
| Guidance width | Widening implies falling confidence in the forecast |
| Guidance midpoint | Direction of travel, independent of the beat or miss |
| Lead metric | Which number management leads with, and whether it changed |
| Segment order | Which business is discussed first, and whether that moved |
| Risk factors | Which were added, removed, or re-ordered |
| Non-GAAP bridge | Whether new categories of cost are being excluded |
| Metric definitions | Any restatement of what a KPI means |

A company that led with revenue growth last period and leads with margin
discipline this period has told you something material, regardless of what the
adjectives say.

---

## THE COMMENTARY DIMENSIONS

### 1. GUIDANCE ARCHITECTURE

The structure of guidance carries more information than its level.

* **Range width**: a wider range implies lower confidence. Track the width over
  time, not just this period's.
* **What is guided**: guidance on revenue only, when free cash flow was
  previously guided too, is a withdrawal by omission.
* **The reaffirmation trap**: a quarter that beats while the full year is merely
  reaffirmed implies a cut to the remaining periods. This is one of the most
  reliable negative signals available and is frequently missed.
* **Withdrawal or new caveats**: guidance withdrawn, or newly conditioned on
  factors outside management's control, is a confidence signal regardless of the
  stated reason.

### 2. LANGUAGE AND TONE SHIFTS

Only meaningful as a delta, and only when you have grade A or B evidence.

* **Hedging density**: the rate of "approximately", "we expect", "should",
  "targeting" against the prior period.
* **Absolute to relative framing**: a shift from "we grew 20%" to "we grew
  faster than the market" usually means absolute growth deteriorated.
* **GAAP to non-GAAP framing**: a shift in which basis is discussed first.
* **First appearances**: the debut of "normalize", "transitory", "pull-forward",
  "rightsizing", "digesting", or "temporary" is worth noting precisely because
  it is a new word.

### 3. METRIC STABILITY

Which numbers management chooses to highlight, tracked across periods.

Rotating headline KPIs is the strongest negative signal observable without any
narrative at all. A company that emphasised subscriber growth, then gross
margin, then adjusted EBITDA over three consecutive periods is selecting
whichever metric currently looks best. Stable reporting through a bad period is
a positive signal about candour.

Also flag: a KPI quietly redefined, a KPI that disappears entirely, and a new
KPI introduced in the same period an old one weakens.

### 4. ATTRIBUTION PATTERN

How management assigns cause for results.

* **Symmetric attribution** is credible: if macro conditions are blamed for a
  miss, macro should also be credited for a beat.
* **Asymmetric attribution** is not: beats attributed to execution while misses
  are attributed to weather, currency, or the cycle.

Track this across several periods. A single period tells you nothing; three
periods of asymmetry tells you how management thinks about accountability.

### 5. QUESTION HANDLING AND OMISSION

What is not discussed is evidence.

* A topic discussed at length last period and absent this period is a finding,
  not an oversight.
* A specific number given last period and replaced by a qualitative statement
  this period ("strong growth" replacing "31% growth") is a downgrade.
* A direct question answered with a process answer ("we are pleased with our
  approach") rather than a number.

### 6. SAY VERSUS DO

The strongest dimension, and fully available at grade C. Compare stated
priorities against executed capital allocation.

| Management says | Check whether |
| --- | --- |
| "Disciplined on capital" | The buyback pace slowed or accelerated |
| "Confident in the outlook" | Insiders were net buyers or net sellers, and at what size |
| "Investing for growth" | Capex and headcount actually rose |
| "Margin is the priority" | Operating expense growth actually decelerated |
| "Deleveraging is the focus" | Net debt actually fell |

A gap between stated priority and executed action is the most actionable finding
this skill produces. Money moves before language does.

### 7. CORROBORATION AGAINST HARD NUMBERS

Every commentary claim gets tested against a series that would have to move if
the claim were true.

| Claim | Corroborating series |
| --- | --- |
| "Demand is inflecting" | Deferred revenue, backlog, receivables, inventory |
| "Pricing power is intact" | Gross margin, revenue per unit |
| "Costs are under control" | Operating expense growth vs revenue growth |
| "The channel is healthy" | Inventory days, receivable days |
| "Investment is paying off" | Return on invested capital trend |

A claim with no corroborating movement is an unsupported claim. Say so.

---

## SECTOR-SPECIFIC ADJUSTMENTS

* **Financials**: watch provisioning language and reserve releases. Credit
  optimism in commentary alongside falling reserves is a leveraged bet on the
  cycle.
* **Biotech and pharma**: trial language is highly conventionalised. Shifts
  between "met the primary endpoint" and "showed encouraging trends" are the
  entire signal.
* **Cyclicals**: management is structurally late to call a turn in either
  direction. Weight the order book over the adjectives.
* **High-growth technology**: watch for a shift from growth metrics to
  efficiency metrics, which usually precedes a growth deceleration being
  acknowledged.

---

## ANALYST VERDICT

Must include:

1. **Commentary credibility**: "Credible", "Mixed", "Promotional", or "Evasive"
2. **Strongest signal**: the single most important finding, with the evidence
   grade it rests on
3. **Say-versus-do gap**: any divergence between stated priorities and executed
   capital allocation, or an explicit statement that none was found
4. **Unsupported claims**: management claims with no corroborating movement in
   the hard numbers
5. **What would change this**: the specific observation that would revise the
   assessment
6. **Dominant evidence grade**: A, B, C, or D for the analysis as a whole

---

## STYLE RULES

* Never invent a quotation. If you do not have the verbatim record, do not use
  quotation marks
* Never present a paraphrase as a direct quote, and never attribute a specific
  sentence to a named executive unless you are working from the primary record
* Always state the evidence grade the conclusion rests on
* Absence is evidence -- a topic dropped since the prior period is a finding
* Never infer tone from numbers you have not seen
* Prefer the delta over the level in every dimension
* When evidence is grade C, say what the numbers imply about management, not
  what management said
* If evidence is grade D, say so plainly and produce no verdict
"""
