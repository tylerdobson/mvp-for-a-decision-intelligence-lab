# Methodology

Retail KPI & Forecasting Sandbox is designed for explainable decision support. The methods are intentionally practical and transparent rather than overly complex.

## KPI Method

The KPI engine calculates metrics from the filtered dataset:

- Revenue = sum of revenue.
- Profit = sum of profit.
- Gross margin rate = gross margin / revenue.
- Profit margin = profit / revenue.
- Average price = revenue / units sold.
- Marketing efficiency = revenue / marketing spend.
- Retention rate = unit-weighted retention rate.
- Churn risk = unit-weighted churn risk.
- Month-over-month change = latest month compared with the prior month.

## Forecast Method

The forecast uses a blend of:

- A linear trend fit to monthly revenue.
- A recent moving average.

The blended forecast keeps the output smooth but still responsive to recent performance. The uncertainty band is based on historical residual variation and capped to avoid implying false precision.

This forecast is a planning estimate, not a guaranteed prediction.

## Scenario Method

The scenario engine estimates directional impact from user-controlled assumptions:

- Marketing spend change affects demand using a marketing elasticity.
- Price change affects demand using a price elasticity.
- Cost change affects cost of goods and operating cost.
- Demand change directly affects unit volume.
- Retention change lightly affects demand through customer-health economics.

Outputs include:

- Estimated revenue
- Estimated profit
- Estimated gross margin
- Estimated retention
- Revenue, profit, and gross-margin deltas
- Risk level
- Recommended action
- Plain-English interpretation

## Risk Classification

Scenario risk is classified as High, Medium, or Low using:

- Adjusted profit
- Profit delta
- Profit margin
- Gross margin rate
- Churn risk
- Size of the assumption change

Large or negative impacts increase risk. This is a decision-support signal, not a statistical guarantee.

## Recommendation Rules

Recommendations are rule-based. The engine checks:

- Low profit margin
- Low gross margin
- Negative revenue trend
- Profit falling faster than revenue
- Weak retention or high churn risk
- Strong region with above-average margin and efficiency
- Weak region with low profit margin
- Product category with high unit share but weak margin
- Scenario risk or opportunity
- Profitable growth patterns worth protecting

Each recommendation includes:

- Priority
- Theme
- Recommendation
- Evidence
- Action

## Limitations

- The dataset is modeled and deterministic for public demo use.
- Forecasts are directional and should be validated with actual results.
- Scenario assumptions are simplified.
- Recommendation rules are explainable but not exhaustive.
- The app is intended for small-business, student, analyst, and public demo use cases.
