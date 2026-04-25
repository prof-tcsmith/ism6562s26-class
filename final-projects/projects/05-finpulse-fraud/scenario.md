# Final Project: FinPulse — Fraud Detection & Transaction Analytics

## Company Background

FinPulse is a digital payments company founded in 2018 that has grown rapidly to process approximately 2 million transactions daily across credit cards, debit cards, and digital wallets. The company serves as a payment processor for 45,000 merchants ranging from small online shops to large retail chains, handling an annual transaction volume of $38 billion. FinPulse operates in 12 countries, with the majority of its volume concentrated in the United States, Canada, the United Kingdom, and Germany.

FinPulse differentiates itself through fast settlement times (merchants receive funds within 24 hours), competitive processing fees, and a developer-friendly API that makes integration straightforward. This has attracted a large number of e-commerce merchants, where card-not-present (CNP) transactions dominate. While this growth has been impressive, the heavy e-commerce focus has also made FinPulse an attractive target for fraudsters — CNP transactions have inherently higher fraud rates than in-store chip-and-PIN transactions because the physical card is not verified.

FinPulse's current fraud detection system was built in 2019 and relies on a rule-based engine with approximately 200 hand-crafted rules. These rules check for known fraud patterns — transactions over a certain amount, transactions from blacklisted countries, velocity checks (too many transactions in a short time), and mismatches between billing and shipping addresses. While effective against simple fraud, the rule-based system has two critical weaknesses: it cannot detect novel fraud patterns that don't match existing rules, and its false positive rate frustrates legitimate customers whose transactions are incorrectly flagged. FinPulse has engaged your team to build the data infrastructure for a next-generation fraud detection system that combines historical pattern analysis with real-time transaction scoring.

## The Business Problem

FinPulse's fraud problem is large and growing:

**Direct Fraud Losses**: Last year, confirmed fraud totaled **$45M** — representing 0.12% of total transaction volume. While this percentage seems small, it significantly exceeds the industry average of 0.07% for payment processors. The $45M breaks down as follows:

- **Card-not-present fraud** (62%): Stolen card numbers used for online purchases
- **Account takeover** (21%): Fraudsters gaining access to legitimate customer accounts
- **Counterfeit cards** (11%): Physical cards cloned from skimmed data
- **Identity theft** (6%): New accounts opened with stolen identities

**False Positive Problem**: The current rule-based system flags **12% of all transactions** for manual review, but **85% of those flagged transactions are actually legitimate**. This creates two problems: (1) legitimate customers experience declined transactions and delayed processing, leading to merchant complaints and customer churn; and (2) the fraud review team of 45 analysts is overwhelmed, spending most of their time clearing false positives rather than investigating actual fraud. FinPulse estimates that each false positive costs **$3.50 in analyst time and customer support**, totaling approximately **$31M annually** in false positive overhead.

**Detection Gap**: Of the fraud that occurs, the current system only catches **60%** in real-time. The remaining 40% is identified only after the customer reports it — often days or weeks later, when chargeback recovery is more difficult and costly. FinPulse's competitors claim real-time detection rates above 85%.

**Merchant Risk**: Certain merchant categories experience disproportionately high fraud rates, but FinPulse's risk scoring for merchants has not been updated in two years. Several high-risk merchants continue to process transactions with minimal scrutiny, while low-risk merchants face unnecessary friction.

The total annual cost of FinPulse's fraud problem — including direct losses, false positive overhead, chargeback fees, and customer churn — is estimated at **$95M**.

## Available Data Sources

| Source | Format | Records | Key Fields |
|--------|--------|---------|------------|
| Transactions | CSV | 1,000,000 | txn_id, timestamp, card_id, merchant_id, amount, currency, merchant_category, country, channel, is_international |
| Customer Profiles | JSON | 100,000 | customer_id, card_id, age, income_bracket, account_age_months, avg_monthly_spend, home_country, typical_categories, credit_limit |
| Merchant Directory | CSV | 10,000 | merchant_id, name, category, country, risk_score, avg_transaction_amount, monthly_volume |
| Fraud Reports | JSON | 15,000 | report_id, txn_id, timestamp, reported_by, fraud_type, amount_disputed, resolution |
| Device Fingerprints | CSV | 600,000 | session_id, txn_id, device_type, os, browser, ip_country, ip_city, is_vpn, is_known_device, login_attempt_count |

### Data Notes

- **Transactions**: A sample of recent transactions. Approximately 2% are associated with confirmed fraud (linked via the fraud reports table). The `channel` field indicates online, in_store, atm, or contactless. The `is_international` flag indicates whether the transaction country differs from the cardholder's home country.
- **Customer Profiles**: One record per customer. The `typical_categories` field is a JSON array of the merchant categories where the customer usually shops. The `avg_monthly_spend` is calculated from the past 6 months. Income bracket is self-reported and may be missing.
- **Merchant Directory**: Master data for all merchants. The `risk_score` (1–10) was last updated two years ago and may be stale. Monthly volume and average transaction amount provide context for expected merchant behavior.
- **Fraud Reports**: Filed by customers, banks, or merchants when fraud is suspected. The `resolution` field indicates whether the investigation confirmed fraud or determined it was a false alarm. The `fraud_type` classifies the nature of the fraud.
- **Device Fingerprints**: Captured during online transactions. The `is_vpn` flag indicates whether the IP address is associated with a known VPN provider. The `is_known_device` flag indicates whether the customer has used this device before. The `login_attempt_count` records how many login attempts preceded the transaction.

## Business Questions

FinPulse's risk management and executive teams need your analysis to address the following:

1. **Fraud Scoring Model**: What transaction, customer, and device features are most predictive of fraud? Build a feature set that could power a fraud scoring model, identifying the top risk indicators from the data.
2. **Merchant Risk Assessment**: Which merchant categories have the highest fraud rates? Update the merchant risk scores based on actual fraud data rather than the stale 2-year-old scores. Identify specific merchants that warrant enhanced scrutiny.
3. **Velocity Attack Detection**: What patterns characterize velocity attacks (many transactions in rapid succession from the same card)? Define detection rules based on transaction frequency, amount patterns, and merchant diversity within short time windows.
4. **Device and Channel Risk**: Which device types, operating systems, and channels have the highest fraud rates? How does VPN usage correlate with fraud? Should FinPulse implement different authentication requirements by channel?
5. **Geographic Risk Patterns**: Which country pairs (cardholder country vs. transaction country) have the highest fraud rates? Are there specific international corridors that warrant enhanced monitoring?
6. **False Positive Reduction**: Among the transactions currently flagged by the rule-based system, which characteristics distinguish true fraud from false positives? Can you identify customer segments where the false positive rate is particularly high?
7. **Customer Behavior Anomalies**: For confirmed fraud cases, how did the fraudulent transaction patterns differ from the customer's normal behavior? Which behavioral deviations are most indicative of account compromise?

## Stage Guide

This section provides **minimum scaffolding** for each stage — think of these as the floor, not the ceiling. Strong projects will go well beyond these suggestions.

### Stage 1: Data Lake Foundation (HDFS)

- **Zone design**: Create landing, curated, and analytics zones in HDFS
- **Landing zone**: Load all five data sources in their original formats
- **Format considerations**: Transactions and device fingerprints are the largest datasets and benefit most from Parquet conversion. Customer profiles JSON needs flattening of the `typical_categories` array.
- **Partitioning hints**: Transactions could partition by `channel` or by date. Device fingerprints could partition by `device_type`. Fraud reports might partition by `fraud_type`.
- **Replication**: Higher replication for fraud reports (audit trail) and customer profiles (regulatory requirement). Standard replication for transaction data.

### Stage 2: Batch Transformation (Spark)

- **Key joins**: Join transactions with customer profiles (on card_id) to compare each transaction against the customer's typical behavior. Join transactions with device fingerprints (on txn_id) to add device context. Join transactions with fraud reports (on txn_id) to label confirmed fraud cases. Enrich transactions with merchant risk data.
- **Aggregations**: Fraud rates by merchant category, channel, and country. Transaction velocity metrics per card (count and sum within rolling time windows). Customer-level behavioral baselines (average transaction amount, typical merchant categories, typical transaction times).
- **Derived features**: Calculate "deviation from normal" metrics — how far each transaction's amount deviates from the customer's average, whether the merchant category is unusual for the customer, whether the transaction time is atypical. Compute device trust scores based on whether the device is known, VPN usage, and past fraud association.
- **Output**: Write enriched transaction data with fraud labels and feature columns to the analytics zone. Build merchant risk scorecards and customer behavioral profiles.

### Stage 3: Real-Time Streaming (Kafka + Spark Streaming)

- **Streaming source**: Transactions are the natural streaming source — they flow continuously 24/7.
- **Kafka topic design**: Consider a `transactions` topic keyed by `card_id`, a `fraud-alerts` topic for detected anomalies, and possibly a `fraud-scores` topic for real-time scoring results.
- **Real-time logic**: Flag transactions where amount exceeds 3x the customer's average monthly spend. Detect velocity attacks — more than 5 transactions from the same card in 10 minutes. Alert on international transactions from cards flagged as domestic-only. Use a tumbling window to track per-card transaction velocity.
- **Alert events**: Generate fraud risk alerts with txn_id, card_id, risk_score, triggered_rules (array of which conditions were met), and recommended_action (approve/review/block).
- **Architecture decision**: Fraud detection is the classic use case for stream processing — every millisecond of delay is an opportunity for additional fraudulent transactions. Consider how batch-computed features (customer behavioral profiles) feed into real-time scoring.

### Stage 4: Pipeline Orchestration (Airflow)

- **Batch DAG**: Schedule daily processing to update customer behavioral baselines, refresh merchant risk scores, and retrain/update fraud detection features. Tasks: ingest new transactions and fraud reports, run Spark transforms, update customer profiles, run quality checks, refresh analytics tables.
- **Quality gates**: Validate that transaction amounts are positive and within plausible ranges. Check that fraud report resolution values are valid. Verify that the fraud rate in each batch is within expected bounds (a sudden spike or drop might indicate a data quality issue). Flag duplicate transaction IDs.
- **Monitoring DAG**: Monitor the real-time transaction scoring pipeline. Track fraud alert rates — too few might indicate the streaming pipeline is down, too many might indicate a false positive surge. Check Kafka consumer lag.
- **Retry and SLA**: Set strict SLAs — fraud detection pipelines cannot fall behind. Build an end-of-day reconciliation DAG that compares real-time fraud flags with batch-computed risk scores to identify discrepancies.

## Evaluation Focus

Strong submissions for this project will demonstrate:

- **Feature engineering creativity**: Fraud detection is fundamentally a feature engineering problem. The raw transaction data is not very informative — the signal comes from derived features like velocity metrics, behavioral deviations, device trust scores, and cross-source signals. Projects that build rich, thoughtful feature sets will stand out.
- **Class imbalance awareness**: Only ~2% of transactions are fraudulent. Projects should address this imbalance in their analysis — stratified metrics, not just overall accuracy. A model that flags nothing as fraud would be "98% accurate" but useless.
- **Real-time architecture depth**: This is the project where real-time processing matters most. Strong submissions will design a streaming pipeline that genuinely adds value — scoring transactions in near-real-time using features computed in batch.
- **Business impact quantification**: Connect your findings to dollars. "Implementing velocity detection rules would catch an additional 500 fraud cases per month, worth $2.3M in prevented losses, while adding only 0.3% to the false positive rate" is the language FinPulse's executives need to hear.

## Data Access

Download the project datasets from the course data repository:

```
https://github.com/prof-tcsmith/ism6562s26-class/tree/main/final-projects/data/05-finpulse-fraud
```

All data files are gzip-compressed (`.csv.gz` and `.json.gz`). Decompress them after downloading with `gunzip *.gz` or load them directly in Spark (which reads gzipped files natively). Clone the data repo and copy files into your project's `data/` directory, or reference them directly from HDFS after loading.
