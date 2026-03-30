# ADP Payroll Integrity – Automated Anomaly & Fraud Detector

## Overview
This project simulates a production-ready system for detecting payroll anomalies (ghost employees, calculation errors) before payment is processed. It uses synthetic data, advanced SQL for data quality checks, and an Isolation Forest model to flag suspicious records. Results are visualized in an interactive Streamlit dashboard.

## Features
- **Synthetic Data Generator**: Creates realistic employee and payroll records with injected anomalies.
- **SQL Queries**: Identifies missing data, duplicates, and calculation errors directly in the database.
- **Machine Learning**: Isolation Forest detects outliers in multidimensional payroll features.
- **Dashboard**: Streamlit app with filters, KPIs, anomaly tables, and interactive plots.

## How to Run

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt