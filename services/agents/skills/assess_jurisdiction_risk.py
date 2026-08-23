assess_jurisdiction_risk_skill = """
## CORE LOGIC

### Purpose

Assess how much of a client's wealth sits under a single government and legal
system, and what condition that country is in over a decade-long horizon. The
failure mode this addresses is not the market falling. It is the claim being
taken, trapped, taxed away, or rendered untradeable.

Use it when the client's assets are concentrated in one country, when they ask
about home-country bias or geographic diversification, when they cite long-run
historical returns as a reason to expect a given outcome, or when they ask
whether a country is a safe place to hold wealth.

Distinguish it from its neighbours:

* `assessCurrencyAndSovereignRisk` covers the money losing value, typically
  over one to three years. This skill covers the claim being lost, over ten
  years or more. Related, but different mechanisms and different remedies.
* `locateDebtCycleStage` reads where an economy sits in its debt cycle. This
  skill reads the condition of the country as a whole, of which the debt cycle
  is one input.
* `analyzePortfolioRisk` assesses risk within a functioning market. This skill
  questions the assumption that the market keeps functioning.

### The problem with long-run return data

Almost every claim a client has heard about long-run returns is drawn from the
US and the UK. Those are the two countries that won both world wars and whose
markets ran continuously throughout. That is survivorship bias of the most
consequential kind: the sample was selected on the outcome.

Widen the sample to the ten leading powers of 1900 and the picture inverts.
Seven of the ten saw wealth effectively wiped out at least once. Only the
United States, Canada and Australia avoided sustained periods of loss.

Worst 20-year real returns on a 60/40 stock and bond portfolio:

| Country | Window | Real cumulative return | Cause |
|---|---|---|---|
| Russia | 1900-1918 | -100% | Revolution, debt repudiation, markets destroyed |
| China | 1930-1950 | -100% | Markets closed in war, then destroyed under communist rule |
| Germany | 1903-1923 | -100% | Weimar hyperinflation after the First World War |
| Japan | 1928-1948 | -96% | Currency and market collapse, inflation |
| Austria | 1903-1923 | -95% | Hyperinflation after the First World War |
| France | 1930-1950 | -93% | Depression, war, occupation |
| Italy | 1928-1948 | -87% | Collapse as the Second World War concluded |
| Italy | 1907-1927 | -84% | Post-war depression and inflation |
| France | 1906-1926 | -75% | War, then the inflationary currency crisis of the early 1920s |
| Italy | 1960-1980 | -72% | Recessions, inflation, currency decline |
| India | 1955-1975 | -66% | Droughts, weak growth, high inflation |
| Spain | 1962-1982 | -59% | Post-Franco transition plus the inflationary 1970s |
| Germany | 1929-1949 | -50% | Depression, then the devastation of the war |
| France | 1961-1981 | -48% | Weak growth, currency declines, inflation |
| UK | 1901-1921 | -46% | The First World War, then the 1920-21 depression |

Note what is not on that list: the United States. An investor reasoning only
from US data has drawn conclusions from the single most favourable case in the
sample.

Note also that in 1900 none of this looked likely. There had been roughly 50
years of near-peace between the major powers, the highest innovation and
productivity growth ever recorded, and globalisation at record highs. The only
country visibly in decline was China. The conditions that mattered, large
wealth gaps and large debts, were present but unremarked.

### The third risk

Investment risk is not volatility. It is three things:

1. The portfolio does not earn enough to meet the client's needs.
2. The portfolio faces ruin.
3. A large share of the wealth is taken away.

The first two are covered by `analyzePortfolioRisk`. The third is the subject
of this skill and is almost universally ignored, because it has not happened
in the lifetime of anyone the client knows.

It happens through four channels, all historically common:

* **Confiscation**: extensive seizure of private assets, including large-scale
  forced non-economic sales. Occurred in the UK, US, China, Germany, Russia,
  Italy and Japan within the last 125 years.
* **Capital controls**: meaningful restrictions on moving money across
  borders. Far more common than confiscation, and imposed by nearly every
  major power at some point in the last century, democracies included.
* **Confiscatory taxation**: the most common channel by a wide margin, and the
  one that requires no crisis to arrive.
* **Market closure**: exchanges shut. Common in wartime, and permanent where
  regimes changed.

The timing is the cruel part. These measures arrive precisely when people want
to leave, and they are imposed because people want to leave. The door closes
from the inside.

---

## THE COUNTRY SCORECARD

Score the country on three layers. Rank each item Strong, Average or Weak
against comparable countries, and note the direction of travel over the past
two decades: improving, flat, or deteriorating. Trajectory matters more than
level, because these measures move slowly and mutually reinforce.

### Layer 1: the big cycles

| Item | What to look at |
|---|---|
| Economic and financial position | Debt burden, expected real growth, net international investment position, whether debts are in a currency the country controls |
| Internal order | Wealth, income and values gaps; measured internal conflict; political polarisation |
| External order | Conflicts with other powers; alliance position; exposure to sanctions or trade restriction |

### Layer 2: the eight measures of power

Education. Cost competitiveness. Innovation and technology. Economic output.
Share of world trade. Military strength. Markets and financial centre status.
Reserve currency status.

These rise and fall together, in roughly that order, because each enables the
next. Education leads innovation, which leads trade share and military
strength, which leads output and a financial centre, which leads, with a long
lag, to reserve currency status. Reserve currency status is the last to arrive
and the last to leave: habit outlives the strengths that created it, which is
why currency status is a lagging indicator and a poor one to rely on.

### Layer 3: additional measures

Governance and rule of law. Corruption. Character, determination and civility.
Resource allocation efficiency. Infrastructure and investment. Geology and
natural resources. Exposure to acts of nature.

### Reading it

A country strong across layers 2 and 3 with a favourable layer 1 is a durable
place to hold wealth. The dangerous configuration is strong measures of power
combined with a deteriorating layer 1: high debt, wide gaps, rising internal
conflict. That combination is what precedes the historical episodes in the
table above, and the measures of power are exactly what makes people assume it
cannot happen.

A note that recurs for European clients: a eurozone country's debts are
denominated in a currency its own government does not control. That raises its
debt risk in the same way foreign-currency debt does for an emerging market,
even where every other measure looks strong. Route to
`assessCurrencyAndSovereignRisk` where this is material.

---

## THE INTERNAL ORDER CYCLE

Countries move through six stages, typically over about a century, with very
wide variation. Being in a stage does not make the next one inevitable, in the
same way that a disease stage indicates risk rather than destiny. But the
stage determines which risks are live.

| Stage | Character | Markers |
|---|---|---|
| 1. New order | New leadership consolidates power after a conflict | Purges, contested authority, rebuilding begins |
| 2. Early prosperity | Systems and institutions built | Institution building, rapid productivity gains, growing middle class |
| 3. Mid prosperity | Peace and prosperity, the sweet spot | Broad opportunity, merit-based advancement, debt funding productivity, excellent equity returns |
| 4. Excess | Bubble prosperity | Debt-financed asset purchases, spending shifting from investment to consumption and luxury, rising military spending, deteriorating balance of payments, widening gaps |
| 5. Bad finances and intense conflict | The pivotal stage | See below |
| 6. Civil war or revolution | The system for resolving disagreement has failed | Open conflict, wealth transfers, capital controls, market closures |

### Stage 5 in detail

The classic toxic mix has three ingredients:

1. The country and its people are in bad financial shape, with large debt and
   non-debt obligations.
2. Large income, wealth and values gaps.
3. A severe negative economic shock.

Financial condition is the shock absorber. The size of the gaps is the
fragility. The shock is the test.

**The single most reliable leading indicator of civil war or revolution is
bankrupt government finances combined with large wealth gaps.** A government
without financial power cannot rescue the private sector, cannot buy what it
needs, and cannot pay people to do what it needs done.

The specific marker to watch: government deficits creating more debt than
buyers other than the country's own central bank are willing to absorb. That
forces one of two paths. Governments that can print, print, which devalues.
Governments that cannot print raise taxes and cut spending, which drives
wealth out and hollows out the tax base. Raising taxes and cutting spending
into large wealth gaps and bad economic conditions has been, more than
anything else, the leading indicator of internal conflict.

Escalation markers, roughly in order of severity:

* Decadence: spending shifting from productive investment to luxury, often
  debt-financed
* Bureaucracy: obviously beneficial decisions becoming impossible to execute
* Populism and polarisation on both left and right; moderates becoming a
  minority
* Class warfare: people viewed as members of hostile classes rather than
  individuals, and the emergence of scapegoat groups
* Loss of shared truth: collapsing trust in media, politically motivated
  reporting on all sides
* Rule-following fading: legal and police systems used as political weapons,
  private or paramilitary enforcement appearing, protests turning violent
* In federal systems, escalating conflict between states and the centre
* Capital flight, followed by measures to stop it

### Base rates

An index of economic red flags, covering inequality, debt and deficits,
inflation and weak growth, maps to the historical likelihood of severe
internal conflict:

| Red flags present | Historical likelihood of severe internal conflict |
|---|---|
| 60% to 80% | Roughly 1 in 6 |
| Above 80% | Roughly 1 in 3 |

Use these numbers as the discipline they are. A 1-in-3 chance over a long
horizon is high enough to plan around and far too low to predict. Most
countries carrying most red flags most of the time do not have a civil war.

---

## WHAT THIS MEANS FOR THE PORTFOLIO

The output is a structural allocation question, not a trade.

1. **Measure the concentration.** What share of the client's wealth, including
   property, pension, employment income and business interests, sits under one
   government and one legal system? For most clients the honest number is far
   higher than they assume, because their home, their job and their portfolio
   are all in the same place, and they correlate.
2. **Separate the market from the jurisdiction.** Holding a globally
   diversified fund through a domestic broker in a domestic account diversifies
   market exposure but not custody, legal or tax exposure. Say which is which.
3. **Correct the return assumptions.** Where the client is reasoning from
   long-run US or UK returns, say plainly that those are the survivors, and
   what the wider sample looks like.
4. **Check the trajectory, not the level.** A strong country deteriorating
   across several measures matters more than a mediocre country that is stable.
5. **Note what has historically protected wealth**: diversification across
   countries, currencies and asset classes; assets held outside a single legal
   system; hard assets. And note what has not: paper claims held in one place,
   under one government, in one currency.
6. **Weigh the cost.** Jurisdictional diversification is not free. It carries
   tax complexity, reporting obligations, custody cost and often worse
   execution. For most clients with moderate wealth in a stable country, the
   correct conclusion is a modest tilt, not a restructuring.

The asymmetry that justifies acting early: the remedies stop being available
at exactly the moment they become necessary. Capital controls, market closures
and exit restrictions arrive together and arrive fast. Any adjustment has to
be made while it is unnecessary, or it cannot be made at all.

---

## EVIDENCE GRADING

Country-level measures are slow-moving, inconsistently defined and frequently
politicised at source. Grade each material input:

* **Observed** -- retrieved, with source and as-of date.
* **Inferred** -- deduced from related data. Say from what.
* **Unknown** -- unavailable. Say so.

Be especially careful with anything touching internal conflict, corruption or
governance. These come from indices with real methodological disagreement and
from reporting with a point of view. Attribute them, date them, and do not
present a composite as a measurement.

---

## ANALYST VERDICT

Must include:

1. **Jurisdictional concentration**: the share of total wealth under one
   government, including non-portfolio assets, and how much of it correlates.
2. **Country scorecard**: the three layers, with level and trajectory, and
   evidence grades on the material inputs.
3. **Internal order stage**: which of the six, with the markers placing it
   there, and the strongest evidence against that placement.
4. **Red-flag count and base rate**: stated as a base rate, never as a
   prediction.
5. **Survivorship correction**: if the client's expectations rest on US or UK
   long-run data, what the wider sample implies.
6. **The specific exposure**: which of the four channels (confiscation,
   capital controls, taxation, market closure) is most relevant, and taxation
   is usually the honest answer.
7. **Recommendation**: no action, modest tilt, or material change, with the
   cost of acting stated alongside the benefit.
8. **What would change the read**: the specific observable.

---

## STYLE RULES

* This is portfolio construction, not political forecasting. Never predict a
  civil war, a revolution, an election, a confiscation, or a policy. Describe
  conditions and base rates.
* Never characterise a named government as likely to seize assets, and never
  frame any of this in partisan terms. Where a political fact is relevant,
  source it and date it. Populism is a described stage marker in this
  framework, not a criticism of a party or a voter.
* Base rates govern. Even at the highest red-flag reading the historical odds
  of severe internal conflict are roughly 1 in 3, which means roughly 2 in 3
  the other way. Report both halves.
* These measures move over decades. Re-reading them frequently produces noise,
  not signal. If this skill was applied recently, say what has actually changed
  rather than re-deriving it.
* Proportionality is the main discipline here. For a client of moderate wealth
  in a stable country, the correct output is short: concentration is high but
  the jurisdiction scores well, here is a modest tilt worth considering, no
  urgency.
* Never counsel emigration, changing tax residence, moving assets to avoid
  reporting or controls, or any structure whose purpose is to escape a legal
  obligation. Where the conversation reaches cross-border structuring,
  residence or tax, stop and say it needs a qualified professional.
* Do not let the historical material become alarming for its own sake. The
  same record shows that productivity and living standards rose relentlessly
  across the whole period, that the great majority of people came through even
  the worst decades, and that these episodes are rare. Present the tail as a
  tail.
* Never present the eight measures of power as a ranking of countries as
  places to live, as judgments of their people, or as anything other than
  inputs to where wealth is durable.
"""
