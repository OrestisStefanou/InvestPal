locate_debt_cycle_stage_skill = """
## CORE LOGIC

### Purpose

Locate an economy in the long-term (big) debt cycle, read what policy makers
are doing about it, and translate both into a portfolio posture. This is a
systemic diagnosis, not a company one. Use it when the question is about the
state of the machine -- debt burdens, credit contraction, central bank
response, whether a downturn is a recession or a depression -- rather than
about a single holding.

Distinguish it from the neighbouring skills:

* `assessMarketSentiment` reads the mood and the pendulum. This skill reads
  the debt mechanics underneath the mood.
* `analyzeMacroImpact` asks how the environment distorts one company's
  earnings power. This skill asks where the whole system is.
* `assessCurrencyAndSovereignRisk` handles the case where the debt is
  denominated in a currency the borrower's central bank does not control.
  That is a different cycle with different asset implications -- see the
  routing question below.

### Credit, debt, and why cycles exist

Credit is the giving of buying power in exchange for a promise to pay it
back, which is debt. Credit is not inherently bad: the question is whether
the borrowed money is used productively enough to generate the income needed
to service it. Too little credit growth can be as damaging as too much,
through foregone development.

Borrowing is pulling spending forward. Someone who earns 100 and spends 120
for several years must later spend 80 for several years. That mechanical
sequence -- not psychology -- is what creates a cycle. If everyone woke up
tomorrow with no memory of the crisis, the position would be unchanged,
because the obligations to deliver money would still exceed the money coming
in.

Short-term debt cycles (business cycles) produce bumps. They stack into a
long-term cycle because each cyclical peak and trough carries a higher
debt-to-income ratio than the last, sustained by central banks progressively
lowering interest rates. When rates can no longer be lowered, the stacking
stops and the deleveraging begins.

### The routing question, asked first

**Is the problem debt denominated in a currency the relevant central bank
controls?**

* **Yes** -- domestic-currency debt, no significant foreign-currency
  liabilities. Expect a *deflationary* deleveraging. Continue with this skill.
* **No** -- significant foreign-currency debt, reliance on foreign capital
  inflows, thin reserves. Expect an *inflationary* deleveraging and a currency
  crisis. Stop and apply `assessCurrencyAndSovereignRisk` instead.
* **Mixed** -- apply both. A reserve-currency country can still drift into an
  inflationary deleveraging late in the process through sustained overuse of
  stimulation, but it emerges slowly and much later.

This single question determines which playbook applies and which assets
survive. Get it wrong and every downstream conclusion is wrong. Answer it
explicitly before proceeding.

---

## THE SEVEN STAGES (DEFLATIONARY BRANCH)

### 1. Early part of the cycle

Debt grows, but not faster than income, because borrowing is financing
activity that produces income. Debt burdens low, balance sheets healthy,
growth and inflation neither too hot nor too cold.

Markers: debt-to-income flat or improving; credit growth broadly matched by
income growth; policy neutral.

### 2. The Bubble

Debt rises faster than income and produces accelerating asset returns.
Self-reinforcing: rising incomes, net worths and collateral values raise
borrowing capacity, which raises spending, which raises incomes. Bull markets
that were initially justified get over-extrapolated. Lending standards fall,
new and lightly regulated intermediaries appear, financial engineering
proliferates, and asset-liability mismatches build up (borrowing short to lend
long, liquid liabilities against illiquid assets, borrowing in one currency to
lend in another).

Markers: debt-to-income rising rapidly; leverage financing purchases;
new participants entering; monetary policy still accommodative because
inflation and measured growth look fine.

**The clearest single warning sign: an increasing share of borrowing is going
to service existing debt rather than to fund new activity.** That is
arithmetically unsustainable and usually visible before anything else breaks.

### 3. The Top

The market is fully long, leveraged and overpriced, and becomes ripe for
reversal. The general principle: when things are so good that they cannot get
better, yet everyone believes they will, tops are being made.

Most tops are triggered by tightening. Short rates rise, the yield curve
flattens or inverts, holding cash becomes relatively more attractive, and the
discount rate on future cash flows rises. Credit problems appear first in the
frothiest pockets, typically around half a year before the peak in the
economy. Riskiest debtors miss payments, spreads tick up, risky lending slows.

Markers: yield curve flat or inverted; credit spreads widening from the
bottom; the most speculative credits deteriorating first while the core still
looks sound.

The magnitude of the coming bust depends less on the size of the tightening
than on how leveraged the system is and how losses cascade between sectors.
Look at individual sectors and the big players within them, not economy-wide
averages.

### 4. The Depression

Interest rates cannot be cut enough to fix the imbalance, because they are at
or near zero (or, where currency risk applies, floored well above zero). This
is the defining condition: **a depression is a downturn in which the primary
monetary lever no longer works.** In a recession it still does.

Defaults and restructurings cascade. Runs occur on institutions that rely on
short-term funding. Both solvency problems (insufficient equity capital under
accounting and regulatory rules) and cash-flow problems (no cash to meet
obligations, often because assets are illiquid) appear; cash-flow problems are
usually the trigger and the more urgent.

Deflationary forces -- defaults, restructurings, austerity -- dominate without
being offset by money creation. Because most lenders are themselves leveraged,
a write-down cascades: a 30% write-down against a lender levered 2:1 removes
60% of its net worth, and banks typically run at 12:1 to 15:1.

Note the asymmetry that traps investors early in this stage: when prices fall
before earnings do, stocks look cheap against both trailing and forecast
earnings. They are not cheap, because the earnings decline has not happened
yet.

Markers: policy rate at the floor; credit spreads wide; runs and failures;
falling asset prices feeding falling collateral values feeding falling
creditworthiness.

### 5. The Beautiful Deleveraging

The turn comes when the four levers are balanced well enough to produce
falling debt-to-income ratios alongside positive growth and acceptable
inflation. The operative condition is arithmetic:

**Nominal income growth must exceed the nominal interest rate on the debt.**

If debt is 100 at 2% and income is 100 growing at 1%, the ratio worsens from
100/100 to 102/101. Enough stimulation to flip that inequality, but not so
much that faith in the currency breaks, is the whole game.

Money printing at this stage is not inflationary if it offsets a credit
contraction of comparable size and character. A unit of spending financed by
money has the same effect on prices as a unit financed by credit; credit is
disappearing, so money replaces it. This is the point most commentary gets
wrong, and it is worth correcting explicitly when a client raises it.

Markers: large-scale asset purchases, not just liquidity facilities; nominal
growth crossing above nominal rates; currency depreciating against gold and
commodities; equity and credit markets stabilising before the real economy.

### 6. Pushing on a String

Stimulus loses traction. Rate cuts are exhausted and asset purchases have
already compressed risk premiums to the point where further buying produces
little wealth effect. Low growth, low prospective returns.

Markers: further monetisation producing diminishing market and spending
response; risk premiums already thin; talk shifting to fiscal and monetary
coordination.

The tail risk here runs in both directions: too little stimulation prolongs
the malaise, too much relative to the deflationary forces tips the process
into an inflationary deleveraging. If you see sustained monetisation alongside
movement out of the currency and into gold or foreign assets, switch to
`assessCurrencyAndSovereignRisk`.

### 7. Normalization

Slow. Real economic activity typically takes 5 to 10 years to regain its prior
peak. Equity prices typically take longer, around a decade, because risk
premiums stay elevated for a long time after the event.

---

## ARCHETYPE CALIBRATION

Historical averages across the deflationary cases in the reference set. Treat
these as order-of-magnitude anchors for locating a stage, never as forecasts
or targets. Ranges are wide and every case differs.

| Measure | Typical | Range |
|---|---|---|
| Debt growth in excess of income, through the bubble | ~40% | 14% to 79% |
| Equity market rally into the top | ~48% | 22% to 68% |
| Yield curve flattening into the top (short minus long) | ~1,4pp | 0,9pp to 1,7pp |
| Total debt-to-GDP at the bubble peak | ~300% | wide |
| Length of the contraction | ~55 months | 22 to 79 |
| Currency decline against gold | ~-44% | -58% to -37% |
| Peak money creation, annualised | ~4% of GDP | 1% to 9% |
| Peak fiscal deficit | ~-6% of GDP | -14% to -1% |
| Equity drawdown before aggressive stimulation | >-50% | wide |
| Length of equity drawdown | ~119 months | 60 to 249 |
| Length of GDP drawdown | ~72 months | 25 to 106 |
| Debt-to-GDP change after stimulation | ~-54% | -70% to -29% |

Sequencing anchors worth more than the levels: the fastest pace of tightening
tends to come roughly five months before the equity top; short rates tend to
peak a few months before the equity top; aggressive stimulation typically
arrives two to three years into the depression, after equities have already
halved.

**Never present these numbers as predictions of what will happen next.** They
are the shape of past cases, used to ask whether the present resembles one.

---

## READING THE POLICY RESPONSE

### The four levers

Every debt crisis is resolved by some mix of four things. Identify which are
in play and in what proportion, because the mix determines the asset outcome.

| Lever | Direction | Effect on assets |
|---|---|---|
| Austerity (spending less) | Deflationary | Depresses nominal growth; rarely works alone, because cutting spending cuts income |
| Defaults and restructurings | Deflationary | Destroys creditor wealth; cascades through leveraged lenders |
| Money printing and asset purchases | Inflationary | Supports nominal asset prices; depreciates the currency |
| Transfers from haves to have-nots | Roughly neutral | Rarely large enough to matter absent revolution; drives capital flight and tax responses |

The observed pattern is that policy makers reach for austerity and
restructuring first, find them insufficient, and eventually print. Austerity
causes more pain than benefit, large restructurings destroy wealth too fast,
and transfers do not happen at sufficient scale voluntarily. Speed matters
enormously: acting quickly and in size compresses the depression, acting late
prolongs it.

### The three monetary policy modes

* **MP1 -- interest rates.** Broadest and most effective. Works through the
  wealth effect, cheaper credit purchases, and lower debt service. Exhausted
  at the zero bound.
* **MP2 -- asset purchases (QE).** Works on investors and savers rather than
  borrowers and spenders. Most effective when risk and liquidity premiums are
  wide, because it compresses them. Loses effectiveness as premiums compress
  and asset prices rise. Widens the wealth gap, because it benefits owners of
  financial assets.
* **MP3 -- money directed at spenders.** Fiscal and monetary coordination,
  debt-financed fiscal spending, direct transfers, debt write-downs paired
  with money creation. Reached for when MP2 is pushing on a string. Most
  effective when coordinated, because coordination ensures the money is
  actually spent rather than saved into assets.

Which mode is active tells you what to expect. MP2 lifts financial assets more
than the real economy. MP3 lifts nominal spending, nominal growth, and
inflation risk more directly, and is less favourable for long-duration bonds.

### Well managed versus poorly managed

| Stage | Well managed | Poorly managed |
|---|---|---|
| Bubble | Policy considers debt growth and its effect on asset markets; targeted restraint where bubbles are forming; fiscal tightening | Policy targets only inflation and growth, keeping credit cheap while an asset bubble inflates |
| Top | Constrain, then ease selectively once the bubble is pricked | Continue tightening well after the bubble has burst |
| Depression | Ample liquidity, rates to the floor fast, then aggressive monetisation; sustained fiscal stimulus; systemically important institutions protected | Slow to cut, limited liquidity, early tightening, austerity without offsetting easing, systemic institutions left damaged |
| Beautiful deleveraging | Monetisation large enough to bring nominal growth above nominal rates; non-systemic institutions allowed to fail in an orderly way | Stuttering, muted purchases skewed to cash-like instruments; central bank stimulus undercut by fiscal austerity; insolvent but non-systemic entities propped up, producing zombie institutions |

Where the current response sits on this table is a better predictor of how
long the episode lasts than the size of the debt itself. The two recurring
impediments are ignorance of what to do and lack of authority to do it, not
the debt burden.

---

## WHAT THIS MEANS FOR THE PORTFOLIO

Translate the stage into posture. This is the same discipline as
`assessMarketSentiment`: an adjustment of stance, not a timing call.

| Stage | Dominant risk | Posture |
|---|---|---|
| Early cycle | Missing opportunity | Normal to constructive. Credit risk acceptable. |
| Bubble | Losing capital permanently | Reduce leverage in holdings. Insist on margin of safety. Avoid entities funding debt service with new borrowing. |
| Top | Losing capital permanently | Defensive. Cut exposure to the leveraged and the illiquid. Do not treat the first drawdown as cheap. |
| Depression | Forced selling, permanent impairment | Survival first. Liquidity and balance-sheet strength over cheapness. Avoid entities dependent on rolling short-term funding. |
| Beautiful deleveraging | Missing the turn | Add risk as monetisation turns aggressive. Nominal assets over cash. Historically the highest-return entry point. |
| Pushing on a string | Low returns, reaching for yield | Accept lower returns. Do not manufacture risk to hit a target. Watch for the inflationary tail. |
| Normalization | Impatience | Normal posture. Expect recovery in activity to precede recovery in equity prices by years. |

Two cross-cutting rules:

* **Do not judge systemic vulnerability from averages.** A given level of
  economy-wide debt or debt service is far less dangerous when it is evenly
  distributed than when it is concentrated in a few key entities. The averages
  hide exactly the concentrations that break first. Where the client holds
  leveraged names, assess those entities directly.
* **Ask what is connected to the stress.** The relevant question is not only
  which market is stretched, but which counterparties, lenders and sectors
  hold claims against it and would be damaged when it corrects.

---

## EVIDENCE GRADING

Much of what this skill needs is macro data that may be incomplete,
unavailable, or of uncertain provenance. Do not silently fill gaps. For the
main inputs, state which of the following applies:

* **Observed** -- a figure was retrieved and its source and date are known.
* **Inferred** -- not directly available, but reasonably deduced from related
  observable data. Say from what.
* **Unknown** -- not available. Say so, and say what the conclusion would look
  like if it turned out either way.

A stage location resting mostly on inferred inputs is a hypothesis, and must
be labelled as one. Never present an unverified figure as a measurement, and
never state a precise number where only a rough magnitude is known.

---

## ANALYST VERDICT

Must include:

1. **Currency routing**: is the relevant debt in a currency the central bank
   controls? If not, this skill is the wrong one -- say so and switch.
2. **Stage**: which of the seven, with the specific markers that place it
   there, and the strongest evidence against that placement.
3. **Confidence**: calibrated, with the evidence grade of the key inputs.
4. **Debt service trend**: is an increasing share of borrowing going to
   service existing debt?
5. **Policy read**: which levers are active, which monetary policy mode, and
   whether the response looks well or poorly managed against the table above.
6. **Concentration check**: where are debt burdens concentrated, as distinct
   from the average?
7. **Posture**: the stance implied for the client's portfolio, with magnitude.
8. **What would change the read**: the specific observation that would move
   the diagnosis to an adjacent stage.

---

## STYLE RULES

* This is a diagnosis of the present, not a forecast. Cycles are logically
  driven sequences of events, not schedules. They do not repeat in the same
  way or take the same amount of time.
* Never produce a market-timing call, a top-down sector rotation
  recommendation, or a date. The output is posture and risk awareness, and it
  feeds bottom-up security selection rather than replacing it.
* Archetype figures are historical averages with wide ranges. Present them as
  such. Never round or restate them as precise expectations.
* Never state or imply that a depression is inevitable, imminent, or
  scheduled. Most downturns are recessions, where the primary monetary lever
  still works.
* Correct the common error that money printing is necessarily inflationary,
  but only where the offsetting credit contraction is genuinely present.
* Be willing to conclude "early-to-mid cycle, nothing actionable." That is the
  honest answer most of the time, and manufacturing a dramatic reading is the
  main failure mode of this skill.
* Political consequences of debt crises are often more consequential and more
  durable than the crises themselves, and over long horizons productivity
  growth dominates both. Keep the drama proportionate.
* Never advise the client to position for a specific policy decision. Describe
  what different responses would imply and let the position be robust across
  them.
"""
