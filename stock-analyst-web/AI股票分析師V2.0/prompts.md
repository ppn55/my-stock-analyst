# Wall Street Analyst — Prompt Templates

This file contains 12 institutional-grade financial analysis frameworks.
Each section is a complete template. Replace bracketed placeholders with
real data gathered via web search and user input.

## Table of Contents

1. [DCF Valuation Model](#1-dcf-valuation-model)
2. [Three-Statement Financial Model](#2-three-statement-financial-model)
3. [M&A Accretion/Dilution Analysis](#3-ma-accretiondilution-analysis)
4. [LBO (Leveraged Buyout) Model](#4-lbo-leveraged-buyout-model)
5. [Comparable Company Analysis (Comps)](#5-comparable-company-analysis-comps)
6. [Precedent Transaction Analysis](#6-precedent-transaction-analysis)
7. [IPO Valuation & Pricing Analysis](#7-ipo-valuation--pricing-analysis)
8. [Credit Analysis & Debt Capacity Model](#8-credit-analysis--debt-capacity-model)
9. [Sum-of-the-Parts (SOTP) Valuation](#9-sum-of-the-parts-sotp-valuation)
10. [Operating Model & Unit Economics](#10-operating-model--unit-economics)
11. [Sensitivity & Scenario Analysis](#11-sensitivity--scenario-analysis)
12. [Investment Committee Memo](#12-investment-committee-memo)

---

## 1. DCF Valuation Model

**Role context:** Senior Analyst, Investment Banking Division

**Produce a complete DCF (Discounted Cash Flow) valuation model containing:**

- **Free cash flow projections:** Next 5 years with explicit growth assumptions.
  Build from revenue → EBITDA → EBIT → NOPAT → FCF. State each assumption.
- **WACC calculation:** Cost of equity (CAPM: risk-free rate + beta × equity
  risk premium) + cost of debt (after tax). Weight by target capital structure.
- **Terminal value:** Calculate using BOTH the perpetuity growth method
  (Gordon Growth: FCF × (1+g) / (WACC−g)) AND exit multiple method
  (terminal EBITDA × exit multiple). Compare results.
- **Sensitivity analysis:** Two-way table varying WACC (rows) and terminal
  growth rate (columns). Show implied share price at each intersection.
- **Discount rate justification:** Explain beta source, risk-free rate
  selection, and equity risk premium used.
- **Key drivers:** Identify the 3–5 variables that move the valuation most.
- **Comparable companies:** Show how growth, margin, and risk assumptions
  compare to public peers.
- **Valuation range:** Bull case, base case, bear case with clear
  assumptions for each.

**Format:** Investment banking pitch-book valuation page with clear formulas.

---

## 2. Three-Statement Financial Model

**Role context:** VP, Financial Modeling Group

**Produce a complete three-statement model containing:**

- **Income statement:** Revenue, COGS, gross profit, SG&A, EBITDA, D&A, EBIT,
  interest, taxes, net income — projected 5 years.
- **Balance sheet:** Current assets (cash, AR, inventory), fixed assets, total
  assets; current liabilities (AP, accrued), long-term debt, equity — 5 years.
- **Cash flow statement:** Operating (net income + add-backs + working capital
  changes), investing (capex, acquisitions), financing (debt, dividends,
  buybacks) — 5 years.
- **Link formulas:** Explain how net income flows to cash flow statement, how
  cash flow ending balance ties to balance sheet cash, how retained earnings
  link statements together.
- **Working capital model:** Days sales outstanding (DSO), days inventory
  outstanding (DIO), days payable outstanding (DPO) driving AR, inventory, AP.
- **Debt schedule:** Outstanding principal, interest rate, mandatory
  amortization, optional prepayment, interest expense calculation.
- **Key assumptions:** Revenue growth rate, gross margin, opex as % of
  revenue, capex as % of revenue, tax rate, working capital days.
- **Error checks:** Balance sheet balances (A = L + E), cash flow ties to
  balance sheet, no circular references without iteration.

**Format:** Excel-style model with formulas explained in plain English.

---

## 3. M&A Accretion/Dilution Analysis

**Role context:** Managing Director, M&A Advisory

**Produce an accretion/dilution analysis containing:**

- **Deal structure:** Cash vs. stock consideration mix, total enterprise value,
  equity value, per-share price, premium to current trading price.
- **Pro forma income statement:** Combined revenue, EBITDA, net income for
  acquirer + target post-deal.
- **EPS impact:** Standalone acquirer EPS vs. pro forma EPS. Calculate
  accretion or dilution in dollars and percentage.
- **Synergies:** Itemize cost synergies (headcount, facilities, systems) and
  revenue synergies (cross-sell, pricing) with dollar amounts and timing
  (when they phase in).
- **Funding sources:** How the deal is paid for — cash on hand, revolver
  draw, new term loan, bond issuance, stock issuance. Show interest cost of
  each debt tranche.
- **Credit impact:** Pro forma net debt/EBITDA, interest coverage ratio,
  credit rating implications.
- **Break-even synergies:** Minimum synergies required for deal to be EPS
  accretive in year 1.
- **Sensitivity table:** EPS accretion/dilution at different purchase prices
  and synergy levels.

**Format:** M&A analysis memo with deal recommendation.

---

## 4. LBO (Leveraged Buyout) Model

**Role context:** Associate, Private Equity

**Produce a complete LBO model containing:**

- **Sources and uses:** Sources (senior debt, mezzanine, sponsor equity,
  rollover equity, cash on B/S). Uses (equity purchase price, transaction
  fees, debt repayment, cash to balance sheet).
- **Debt structure:** Senior secured (term loan A, term loan B), second lien,
  mezzanine/sub debt, revolver. For each: amount, interest rate (fixed vs.
  floating), amortization schedule, maturity, covenants.
- **Cash flow sweep:** How excess free cash flow is applied to mandatory
  debt repayment vs. optional prepayment. Sweep percentage by year.
- **Exit scenarios:** Strategic sale and IPO at years 3, 4, and 5. Apply
  exit EBITDA multiples ranging from current to +1x expansion.
- **IRR calculation:** Equity IRR for each exit year and multiple
  combination. Show the formula.
- **Cash-on-cash multiple (MOIC):** Total equity proceeds ÷ initial equity
  invested for each scenario.
- **Debt paydown schedule:** Year-by-year beginning balance, mandatory
  amort, optional prepay, ending balance for each tranche.
- **Management assumptions:** Revenue CAGR, EBITDA margin trajectory,
  capex as % of revenue, working capital changes.

**Format:** Private equity investment committee memo with returns analysis.

---

## 5. Comparable Company Analysis (Comps)

**Role context:** Equity Research Analyst

**Produce a trading comps analysis containing:**

- **Peer group:** 10–15 public companies in the same industry. Justify
  inclusion/exclusion criteria (size, geography, business model, growth).
- **Trading multiples:** For each peer: EV/Revenue (NTM), EV/EBITDA (NTM),
  P/E (NTM), EV/FCF. Use next-twelve-months consensus estimates.
- **Financial metrics:** Revenue, revenue growth, EBITDA, EBITDA margin,
  net income, FCF margin for each peer.
- **Valuation range:** 25th percentile, median, mean, 75th percentile of
  each multiple across the peer set.
- **Implied valuation:** Apply 25th/median/75th multiples to the target
  company's financials to get an implied equity value range.
- **Premium/discount adjustments:** Explain why the target deserves to
  trade at a premium (superior growth, margins) or discount (smaller scale,
  higher risk) vs. peers.
- **Growth comparison:** Revenue growth, EBITDA growth, margin trend vs.
  peer median.
- **Quality screen:** Rank peers by comparability. Flag the 5 closest comps.

**Format:** Comparable company valuation table with multiples highlighted.

---

## 6. Precedent Transaction Analysis

**Role context:** M&A Banker

**Produce a precedent transaction analysis containing:**

- **Transaction universe:** 15–20 relevant M&A deals in the past 5 years in
  the same or adjacent industry.
- **Deal multiples:** EV/EBITDA, EV/Revenue paid in each transaction.
- **Deal characteristics:** Acquirer name, target name, deal size (EV),
  announcement date, deal rationale (strategic, financial, consolidation).
- **Premium analysis:** Control premium paid over the target's unaffected
  trading price (1-day, 30-day, 90-day prior).
- **Valuation range:** 25th percentile, median, 75th percentile of deal
  multiples.
- **Adjustments:** Flag differences between strategic vs. financial buyers,
  high-synergy vs. low-synergy deals, contested vs. friendly transactions.
- **Market conditions:** Note how M&A volumes, credit availability, and
  sector sentiment evolved over the period.
- **Implied valuation:** Apply 25th/median/75th deal multiples to the target
  company's financials.

**Format:** M&A valuation analysis with transaction comparables table.

---

## 7. IPO Valuation & Pricing Analysis

**Role context:** Capital Markets Banker

**Produce an IPO pricing analysis containing:**

- **Offering structure:** Primary shares (new capital raised) vs. secondary
  shares (insider selling), total shares offered, over-allotment (greenshoe).
- **Pre-money valuation:** Implied company value before IPO proceeds.
- **Post-money valuation:** Pre-money + primary proceeds.
- **Comparable IPOs:** 5–10 recent IPOs in the same sector with pricing
  multiples (EV/Revenue, EV/EBITDA, P/E at IPO price), first-day return,
  and current trading vs. IPO price.
- **Valuation range:** Low, mid, high price per share with implied
  EV/Revenue and EV/EBITDA at each price.
- **Dilution analysis:** Existing shareholder ownership before and after IPO,
  including ESOP pool expansion.
- **Float analysis:** Shares trading publicly as % of total shares
  outstanding. Compare to sector median float.
- **First-day pop expectation:** Typical underpricing in the sector based on
  recent IPO data.

**Format:** IPO pricing memo with share price recommendation range.

---

## 8. Credit Analysis & Debt Capacity Model

**Role context:** Leveraged Finance Banker

**Produce a debt capacity analysis containing:**

- **EBITDA analysis:** Historical (3 years) and projected (3 years). Note any
  add-backs or adjustments to arrive at "adjusted EBITDA."
- **Leverage ratios:** Total Debt / EBITDA, Senior Debt / EBITDA, Net Debt /
  EBITDA. Compare to industry standards and rating agency thresholds.
- **Interest coverage:** EBITDA / Interest Expense, (EBITDA − Capex) /
  Interest Expense. State minimum acceptable thresholds.
- **Debt structure:** Senior secured (1st lien), senior unsecured, subordinated,
  mezzanine layers. Amount, rate, maturity for each.
- **Covenants:** Maximum leverage ratio, minimum interest coverage, minimum
  liquidity, restricted payments basket.
- **Maximum debt capacity:** How much the company can borrow while staying
  within investment-grade (or specified) credit metrics.
- **Pricing grid:** Expected interest rate at different leverage levels
  (e.g., 2.0x = L+175, 3.0x = L+250, 4.0x = L+350).
- **Refinancing analysis:** Existing debt maturity profile and when each
  tranche needs to be rolled or refinanced.

**Format:** Credit memo with debt capacity recommendation.

---

## 9. Sum-of-the-Parts (SOTP) Valuation

**Role context:** Restructuring / Strategic Advisor

**Produce a sum-of-the-parts valuation containing:**

- **Business segments:** Break the company into distinct operating divisions.
  Name each segment and describe what it does.
- **Segment financials:** Revenue, EBITDA, EBITDA margin, revenue growth for
  each segment.
- **Valuation methodology:** Select the best approach for each segment — DCF,
  public comps, or precedent transactions. Justify the choice.
- **Segment values:** Individual enterprise value for each segment using the
  chosen methodology.
- **Corporate costs:** Identify unallocated overhead. Decide whether to
  capitalize as a negative value or allocate to segments.
- **Debt allocation:** Total consolidated debt, cash, and other
  enterprise-to-equity bridge items.
- **Total value:** Sum of segment EVs − corporate costs − net debt + cash +
  non-operating assets.
- **Value per share:** Total equity value ÷ diluted shares outstanding.
  Compare to current trading price to find discount/premium.

**Format:** Restructuring analysis with breakup valuation scenarios.

---

## 10. Operating Model & Unit Economics

**Role context:** Growth Equity Investor

**Produce a detailed operating model containing:**

- **Revenue build:** Bottom-up forecast. For SaaS: customers × ARPU × retention.
  For e-commerce: orders × AOV × purchase frequency. For marketplaces:
  GMV × take rate. State the driver model explicitly.
- **Unit economics:** Customer acquisition cost (CAC), lifetime value (LTV),
  LTV/CAC ratio, payback period in months, gross margin per unit or per
  customer.
- **Cohort analysis:** Show how retention, revenue, and margin evolve for
  customer cohorts acquired in different periods.
- **Key drivers:** The 5 inputs that move revenue and costs the most. Show
  impact of ±10% change in each.
- **Scenario planning:** Upside (strong retention, expanding ARPU, lower CAC),
  base (management plan), downside (churn increases, CAC rises, growth
  slows). State assumptions for each.
- **Burn rate:** Monthly cash consumption. Cash runway at current burn. Months
  to zero.
- **Breakeven analysis:** When does the company reach cash-flow breakeven?
  What metrics must hit for that to happen?
- **Scaling assumptions:** How do unit economics improve (or degrade) as the
  company scales? Economies of scale vs. diminishing returns.

**Format:** Operating model with monthly projections for year 1, quarterly
for years 2–3.

---

## 11. Sensitivity & Scenario Analysis

**Role context:** Risk Management / Valuation Quality Control

**Produce a sensitivity and scenario analysis containing:**

- **One-way sensitivity:** For each key variable (revenue growth, EBITDA
  margin, WACC, terminal growth, exit multiple), show how the valuation
  changes as that single variable moves ±20% from base case.
- **Two-way sensitivity:** Pair the two most impactful variables. Create a
  matrix showing valuation at each combination.
- **Scenario builder:**
  - *Bull case:* All key assumptions at optimistic end simultaneously.
  - *Base case:* Management plan / consensus estimates.
  - *Bear case:* All key assumptions at pessimistic end simultaneously.
  State the specific assumptions for each scenario.
- **Monte Carlo inputs (conceptual):** For each key assumption, define the
  probability distribution (normal, triangular, uniform) and parameters
  (mean, std dev, min, max). Describe the simulation approach.
- **Breakeven analysis:** What minimum revenue growth, margin, or synergy
  level is required for the investment to generate a positive return?
- **Downside protection:** At what valuation does the equity get wiped out?
  What margin of safety exists?
- **Risk factors:** Rank the top 5 assumptions by impact on valuation. For
  each, state the base case value, plausible downside, and valuation impact.
- **Hedging strategies:** For each major risk, suggest a financial or
  operational hedge.

**Format:** Risk analysis memo with sensitivity tables and scenario outcomes.

---

## 12. Investment Committee Memo

**Role context:** Partner / Portfolio Manager, Investment Committee

**Produce an investment committee memo containing:**

- **Executive summary:** Three paragraphs: (1) what the opportunity is and why
  now, (2) expected returns and structure, (3) key risks and mitigants.
- **Deal overview:** Transaction structure, total size, use of proceeds,
  expected timeline, key parties involved.
- **Company analysis:** Business model, products/services, customer base,
  competitive positioning (moats), management team assessment, financial
  performance summary (3-year history + projections).
- **Industry analysis:** Total addressable market (TAM), market growth rate,
  secular trends, competitive landscape, regulatory environment.
- **Investment thesis:** 3–5 specific reasons this investment will generate
  returns. Each point should be a testable hypothesis with supporting
  evidence.
- **Valuation summary:** Present results from multiple methodologies (DCF,
  comps, precedent transactions). Describe the "football field" chart showing
  ranges from each method.
- **Returns analysis:** Expected IRR, cash-on-cash multiple (MOIC), payback
  period. Show returns under base, upside, and downside scenarios.
- **Risk assessment:** Top 5 risks ranked by probability × impact. For each:
  description, likelihood, severity, and specific mitigation strategy.
- **Recommendation:** Clear invest or pass recommendation with reasoning. If
  invest, state the maximum price / terms acceptable.

**Format:** Investment committee presentation deck outline.

## 13. 台股股票分析報告

**產生完整台股分析報告，10 大區塊**：

### 1. 基本資訊
股票：[TICKER] [NAME] | 產業：[INDUSTRY]
現價：[PRICE]元 | 市值：[CAP]億元


### 2. 執行摘要
- **論點**：說明看好/看淡理由
- **評級**：短期/中期/長期 BUY/HOLD/AVOID
- **目標價**：[低]–[高]元

### 3. 公司產業
- 商業模式、主要客戶、競爭者
- 產業週期：衰退/復甦/成長/高峰

### 4. 財務表（3年）
| 年 | 營收 | 毛利% | EPS |
觀察：成長性、獲利品質、配息

### 5.估值
同業平均 P/E [X]倍，本公司 [Y]倍

### 6. 技術面
- MA：5日[Y]、20日[Z]（多/空排列）
- RSI：[X]（超買/超賣）
- 支撐：[S1]、壓力：[R1]

### 7. 籌碼
- 外資近10日：[買/賣超] [X]張
- 融資：[餘額]、vs高點折[X]%
  
### 8. 交易計畫
- **買點**：< [Y]元
- **停損**：破 [S1]元
- **目標**：[短]、[中]、[長]元

### 9. 風險（前3）
| 風險 | 機率 | 影響 | 對策 |

### 10. 結論
**短線：[BUY/HOLD/SELL]**  
**波段：[BUY/HOLD/SELL]**  
**長期：[BUY/HOLD/SELL]**

**格式**：Markdown + 表格，適合 YouTube 腳本。

