# Data Dictionary

The sample dataset is stored in `data/sample_business_data.csv` and loaded into the SQLite table `business_metrics`.

## Table: business_metrics

| Column | Type | Description |
| --- | --- | --- |
| id | Integer | SQLite primary key generated when the CSV is loaded into the database. |
| month | Date text | First day of the month for the business record. |
| region | Text | Sales region. Values are Northeast, Midwest, South, and West. |
| product_category | Text | Product or service line. Values are Analytics Software, Implementation Services, Training Workshops, and Support Plans. |
| customer_segment | Text | Customer group. Values are Small Business, Mid-Market, and Enterprise. |
| marketing_spend | Real | Estimated marketing dollars assigned to the row. |
| operating_cost | Real | Estimated operating cost assigned to the row, excluding marketing spend. |
| units_sold | Integer | Number of units sold for the month, region, product category, and segment. |
| average_price | Real | Average selling price per unit. |
| revenue | Real | Units sold multiplied by average price. |
| gross_margin_rate | Real | Gross margin as a decimal rate. Example: 0.42 means 42%. |
| gross_margin | Real | Revenue multiplied by gross margin rate. |
| profit | Real | Gross margin minus operating cost and marketing spend. |
| retention_rate | Real | Estimated customer retention rate as a decimal. |
| churn_risk | Real | Estimated churn risk as a decimal. Calculated as 1 minus retention rate. |
| created_at | Date text | Timestamp added by SQLite when each row is loaded. |

## Dataset Grain

Each row represents one monthly business outcome for a unique combination of:

- Month
- Region
- Product category
- Customer segment

The generated dataset includes 36 months, 4 regions, 4 product categories, and 3 customer segments for a total of 1,728 records.

## Notes

- The data is synthetic and deterministic.
- It is designed for portfolio analytics, not real financial decision-making.
- The values include seasonality, regional differences, customer-segment differences, and product-level economics.
