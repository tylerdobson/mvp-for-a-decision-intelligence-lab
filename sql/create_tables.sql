PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS business_metrics;

CREATE TABLE business_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    region TEXT NOT NULL,
    product_category TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    marketing_spend REAL NOT NULL,
    operating_cost REAL NOT NULL,
    units_sold INTEGER NOT NULL,
    average_price REAL NOT NULL,
    revenue REAL NOT NULL,
    gross_margin_rate REAL NOT NULL,
    gross_margin REAL NOT NULL,
    profit REAL NOT NULL,
    retention_rate REAL NOT NULL,
    churn_risk REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_business_metrics_month ON business_metrics(month);
CREATE INDEX idx_business_metrics_region ON business_metrics(region);
CREATE INDEX idx_business_metrics_category ON business_metrics(product_category);
CREATE INDEX idx_business_metrics_segment ON business_metrics(customer_segment);
