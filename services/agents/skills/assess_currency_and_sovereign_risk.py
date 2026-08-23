assess_currency_and_sovereign_risk_skill = """
## CORE LOGIC

### Purpose

Assess the risk that a currency the client is exposed to depreciates sharply,
and what that would do to their portfolio. This covers the inflationary branch
of the big debt cycle: the crisis that happens when a country owes money in a
currency its own central bank cannot create.

Use it when the client holds assets denominated in a currency other than the
one they spend in, has emerging-market exposure, asks about currency risk,
inflation hedging, gold, or the safety of a particular country's assets, or
when `locateDebtCycleStage` has routed here because the debt in question is
foreign-currency denominated.

### Why foreign-currency debt changes everything

A country whose debts are in its own currency can always spread the pain of
those debts over time, because its central bank can create the money the debts
are owed in. The choices are unpleasant but they exist. A country whose debts
are in someone else's currency has no such lever. It must earn or borrow that
currency, and when neither is available the adjustment falls on the exchange
rate.

That is the whole distinction. Domestic-currency debt crises resolve
deflationary; foreign-currency debt crises resolve inflationary, through a
falling currency that pushes up import prices. Across the historical record,
the correlation between how much of a country's debt is foreign-denominated
and how inflationary its depression turns out is high.

Two consequences follow, and both matter for a portfolio:

* Currency weakness is what makes a depression inflationary. It is not a side
  effect. It is the transmission mechanism.
* Debts denominated in a foreign currency get *heavier* as the local currency
  falls, exactly when local income is falling. The two move against each other.

### What a currency holder actually earns

For a foreign holder, the return on holding a currency is the spot move plus
the interest rate differential. Nothing else. If a currency is expected to
fall 5% over a year, it must yield roughly 5% more to compensate. This
identity drives everything in the stages below, and it is also the right frame
for the client's own position: an asset denominated in a foreign currency
carries a currency return that is separate from the asset return, and the two
must be assessed separately.

Note that domestic and foreign holders want different things. A domestic saver
cares about inflation relative to the interest rate, and moves into inflation
hedges when compensation is inadequate. A foreign lender cares about the
currency move relative to the interest rate. Policy that satisfies one can
fail the other.

---

## VULNERABILITY SCREEN

Inflationary depressions are possible anywhere but concentrate sharply in
countries with these characteristics. Score each. The more that are present
and the more extreme each is, the greater the exposure.

| Criterion | Why it matters |
|---|---|
| No reserve currency status | No standing global demand to hold the currency as a store of wealth |
| Low foreign exchange reserves | Thin cushion against capital outflows |
| Large foreign-currency debt | Debt cost rises with the currency it is owed in, and cannot be monetised away |
| Large or widening budget and current account deficits | Continuous need to borrow or print to fund the gap |
| Negative real interest rates | Holders are not being compensated for holding the currency |
| History of high inflation and negative currency returns | Trust, once broken, does not return quickly |

A reserve-currency country with little foreign-currency debt is much less
exposed, but not immune. It can drift into an inflationary deleveraging late,
slowly, through sustained overuse of stimulation that erodes willingness to
hold the currency. The path is the same, only longer.

---

## THE FIVE STAGES

### 1. Early part of the cycle

Genuine competitiveness attracts capital, which funds productive investment,
which produces real returns. Debt and income rise together. The central bank
may buy incoming foreign currency to hold the exchange rate down, accumulating
reserves and easing domestic conditions in the process.

Markers: healthy balance sheets, capital inflows funding tradeable-sector
investment, reserves building, currency return positive for the right reasons.

### 2. The Bubble

Good returns attract more capital, which drives asset prices and the currency
higher, which attracts more capital still. Growth becomes increasingly financed
by debt rather than productivity, and the strengthening currency erodes the
competitiveness that started the boom. Foreign-currency borrowing grows
because local capital markets are shallow and foreign lending is cheap and
eager.

The structural danger builds quietly: entities all over the economy end up
long the local currency and short the foreign one without deciding to.
Exporters leave revenue unhedged, local firms borrow in the cheaper foreign
currency, foreign subsidiaries hold local deposits. Each position is
individually sensible while the trend holds and simultaneously unprofitable
when it turns.

Typical conditions at the top of the bubble, with the historical spread
between better and worse eventual outcomes:

| Measure | Average | Worst third of outcomes | Best third |
|---|---|---|---|
| Foreign-currency debt, share of total | ~34% | ~41% | ~25% |
| Foreign-currency debt, share of GDP | ~46% | ~46% | ~41% |
| Equity return, 3 years, in USD | ~18% | ~41% | ~7% |
| Capital inflows | ~12% of GDP | ~14% | ~8% |
| Current account | ~-6% of GDP | ~-9% | ~-4% |
| Reserves | ~10% of GDP | ~8% | ~10% |

Other typical bubble markers: real exchange rate overvalued by roughly 15% on
a purchasing power parity basis; debt-to-GDP rising around 10 percentage
points a year over three years; the output gap strongly positive; imports
rising faster than exports.

The pattern in that table is the usable part: the countries that were most
externally reliant and had the biggest asset bubbles had the most painful
outcomes. External reliance is the variable to watch, more than the level of
debt.

### 3. The Top and the Currency Defense

Because the optimism is fully priced, a minor event can start the reversal.
Causes cluster into four groups:

1. Income from selling to foreigners drops (currency too strong for exports to
   compete, or an export commodity price falls).
2. The cost of imports or of borrowing rises.
3. Capital inflows decline, whether because the unsustainable pace naturally
   slows, because worries about domestic conditions or politics grow, or
   because monetary policy tightens either locally or in the currency the debt
   is denominated in.
4. Domestic citizens and companies start moving their own money out.

Weakening capital flows are usually the first shoe to drop, and adverse shifts
in capital flows generally matter more than the trade balance.

Policy makers then defend the currency, by spending reserves and by raising
interest rates. **These defenses almost always fail, and the reason is
arithmetic.** If the market expects a 5% depreciation over a month, it demands
roughly 5% of extra yield over that month, which annualises to something near
80%. No weak economy can carry that. So the defense cannot offer enough
compensation to stop the selling, while the rates it does impose deepen the
downturn.

A managed, gradual decline is the worst version, because it teaches the market
to expect more of the same. That expectation raises domestic rates further,
accelerates capital withdrawal, and widens the gap the reserves must fill.
Capital controls, the usual last resort, mostly fail too: investors find ways
around them, and the attempt to trap capital is itself a reason to run, in the
same way that a rumour about a bank causes the run it warns of.

Markers, typically over roughly six months: reserves drawn down 10% to 20%;
short rates rising hard; the forward exchange rate falling ahead of the spot
as the interest differential widens; officials making emphatic public
commitments never to devalue.

That last marker deserves emphasis for reading the news flow. Emphatic
official denials are a feature of the stage immediately before the currency
is let go, not evidence against it. A surprise devaluation is the better
policy, so policy makers say they will defend the currency right up until
they stop. Treat such statements as information about the stage, never as
information about the outcome.

### 4. The Depression, when the currency is let go

A country, unlike a household, can change what its money is worth. Devaluing
30% is a 30% pay cut only relative to the rest of the world; domestic wages in
domestic currency are unchanged. That is why devaluation is stimulative, and
why defending a currency to the point of exhausted reserves or crushing
interest rates is the worse choice.

A large, surprising, one-off devaluation is better than a gradual one. It
creates a two-way market, where the currency is no longer universally expected
to keep falling, which is what allows inflation expectations to settle and
rates to come down.

What typically follows:

* Currency falls around 30% in real terms; foreign holders lose around 30% in
  the first year, as the interest rate does not offset the move
* Reserves fall a further ~10% as policy makers smooth the decline
* Capital inflows collapse by more than 5% of GDP in under a year; outflows
  continue at 3% to 5% of GDP
* Short rates rise by roughly 20 percentage points and the yield curve inverts
* Printing stays limited, around 1% to 2% of GDP, because printing enables
  more capital flight
* Equities fall around 50% in local currency terms and considerably more in
  foreign currency terms
* Debt service rises by more than 5% of GDP, as foreign-currency obligations
  get heavier in local terms while incomes fall
* Inflation rises roughly 15 percentage points, peaking near 30%, and stays
  elevated for around two years
* The output gap falls around 8 percentage points to a trough near -4%, with
  the bottom in activity roughly a year in

Hidden problems -- fraud, accounting failures, corruption -- surface in this
phase, because falling tides expose them.

### 5. Normalization

Recovery comes when it becomes desirable to hold the currency again. That
requires a positive expected total return at an interest rate the domestic
economy can bear, which is only possible once the currency is cheap enough.
The counterintuitive conclusion, and the one most policy makers resist, is
that a low currency is the precondition for stabilisation, not the failure of
it.

Typical recovery path: the collapse in imports swings the current account by
around 8 percentage points of GDP, from roughly -6% to a surplus near 2%,
about 18 months in; imports contract around 10%; short rates return to
pre-crisis levels in around two years, and inflation in around the same;
the real exchange rate sits undervalued by roughly 10% on a PPP basis and
stays cheap; activity returns to average around three years from the bottom;
capital inflows and equities in foreign-currency terms take four to five years
to recover.

| | Well managed | Poorly managed |
|---|---|---|
| The currency | Defended verbally, then devalued as a surprise, and by enough to create a two-way market | Weakness widely expected; initial devaluation too small, so more are needed |
| External imbalance | Tight policy brings domestic demand down in line with income; investors given a reason to stay | Policy kept loose to postpone domestic pain; outflows fought with capital controls |
| The downturn | Reserves used sparingly, to smooth rather than to resist | Reserves spent sustaining a level of spending that income no longer supports |
| Bad debts | Over-indebted entities worked through, with credit maintained elsewhere | Disorderly defaults, feeding uncertainty and further capital flight |

---

## THE HYPERINFLATION SPIRAL

Most inflationary depressions are transitory. A subset spiral. The
distinguishing feature is singular and worth stating plainly:

**Hyperinflation follows from failing to close the gap between external
income, external spending and debt service, and funding that gap by printing,
repeatedly, over years.**

Sometimes this is not a choice. An externally imposed obligation that cannot
be defaulted on removes the option. More often it is a decision to sustain
spending rather than bring it into line with income.

Escalation markers, roughly in order:

* Each round of printing produces less growth, because more of the money goes
  into real and foreign assets rather than into spending on goods and services
* A wage-price spiral takes hold, especially where wages are formally indexed
* Savers move faster each round into foreign currency and physical assets;
  those who shorted cash keep being proved right
* Deposit and lending maturities shorten across the system; at the extreme,
  lending stops
* Shorting cash becomes cheap as real interest rates go deeply negative
* Tax evasion and capital flight rise sharply in response to higher taxes on
  income and wealth
* The currency fails in sequence: first as a store of value, then as a unit of
  account, then as a medium of exchange, at which point producers demand
  foreign currency or barter

Once the spiral completes, the currency does not recover its standing. The
conventional exit is a new currency with hard backing, phased in as the old
one is retired.

### Asset behaviour through a spiral

This is where intuition fails most badly, so state it precisely:

* **Gold and commodities**: the preferred holdings. Commodity-producing
  industries too.
* **Foreign currency**: getting assets out of the currency and out of the
  country is the dominant consideration.
* **Equities**: a mixed bag early, and a losing proposition as inflation
  transitions into hyperinflation. Share prices rise in local currency and
  still lose in real and foreign-currency terms; the correlation between the
  exchange rate and share prices breaks down and the two diverge. Local-currency
  index gains during a currency collapse are not returns.
* **Bonds**: wiped out. Local-currency fixed income is the worst place to be.

The general shape holds, at reduced magnitude, for ordinary inflationary
depressions that never reach a spiral.

---

## APPLYING THIS TO THE CLIENT'S PORTFOLIO

This skill exists to assess the client's exposure. It does not exist to issue
views on sovereigns or to recommend currency trades. Keep the output anchored
to positions the client actually holds.

Work through:

1. **Currency mix of assets versus spending.** Which holdings are denominated
   in, or earn their revenue in, a currency other than the one the client
   spends in? Size that exposure as a share of the portfolio.
2. **Separate the two returns.** For each material foreign-currency exposure,
   the asset return and the currency return are distinct. A holding can be
   right on fundamentals and still lose. Say which is being relied on.
3. **Look through to underlying exposure.** A domestically listed company with
   most of its revenue abroad, or foreign-currency debt on its balance sheet,
   carries currency risk that the listing location hides. Companies that
   borrowed in a foreign currency while earning in a local one are the
   classic asymmetry, and they fail first.
4. **Screen the relevant currencies** against the vulnerability criteria
   above, and note which stage, if any, they appear to be in.
5. **Check for unintentional length.** The bubble-stage lesson applies to
   portfolios as much as to economies: exposures accumulated because a trend
   was working, rather than because they were chosen, are the ones that hurt.
6. **State the concentration honestly.** Currency risk correlates across
   holdings in a way that looks diversified in a list of positions and is not.
   This connects directly to the hidden-correlations dimension in
   `analyzePortfolioRisk`.

---

## EVIDENCE GRADING

Reserve levels, foreign-currency debt shares, capital flow data and real
exchange rate valuations are frequently unavailable, stale, or inconsistently
defined between sources. Grade each material input:

* **Observed** -- retrieved, with source and as-of date stated.
* **Inferred** -- deduced from related data. Say from what.
* **Unknown** -- unavailable. Say so, and say what it would take to change the
  conclusion.

Currency data goes stale faster than most financial data, and a reserves
figure or exchange rate from months ago can be actively misleading during a
defense. Always state the as-of date. An assessment resting mainly on inferred
inputs is a hypothesis and must be labelled as one.

---

## ANALYST VERDICT

Must include:

1. **Exposure**: which currencies the client is exposed to and how much of the
   portfolio each represents, including look-through exposure.
2. **Vulnerability score**: each relevant currency against the six criteria,
   with evidence grades.
3. **Stage**: which of the five stages each relevant currency appears to be
   in, and the markers placing it there.
4. **Spiral check**: for any currency in stage 3 or 4, whether the escalation
   markers are present or absent.
5. **Asset-versus-currency split**: for material foreign-currency holdings,
   which of the two returns the thesis depends on.
6. **The concentrated risk**: the single largest currency exposure and what a
   30% adverse move would do to the portfolio in the client's spending
   currency.
7. **What to watch**: the specific observable that would change the read.
8. **Posture**: hedge, reduce, hold, or no action, with reasoning. "No action"
   is the correct answer for most portfolios most of the time.

---

## STYLE RULES

* Assess the client's exposure. Do not issue country calls, sovereign credit
  opinions, or currency trade recommendations. If the client asks directly
  whether a country is heading for a crisis, answer in terms of observable
  vulnerability and what it would mean for their holdings, not as a forecast.
* Never predict a devaluation, its timing, or its size. The stages describe
  what has recurred, not what will happen. Countries sit in the vulnerability
  zone for years without a crisis, and some never have one.
* Official denials of an imminent devaluation are a stage marker, not
  evidence. Never repeat one as reassurance, and never present the framework
  as reason to disbelieve a specific government.
* Distinguish transitory inflationary depressions from spirals. Spirals are
  rare and require sustained policy failure. Do not describe ordinary currency
  weakness in hyperinflation language.
* Local-currency gains during a currency decline are not returns. Always
  express performance in the client's spending currency.
* Devaluation is stimulative and is usually the resolution rather than the
  catastrophe. Do not treat a falling currency as automatically bad news for
  the assets in it.
* Be proportionate. For a client with no meaningful foreign-currency exposure,
  the honest output is short: exposure is immaterial, here is why, no action.
* Never recommend moving assets between jurisdictions for the purpose of
  avoiding controls, taxes, or reporting obligations. Where the analysis
  touches cross-border movement of money, keep it to portfolio construction
  and say that jurisdictional and tax questions need professional advice.
"""
