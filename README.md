# Emergency Alert Outreach Campaign – Data Analysis

## Project Summary

This project analyzes a phone outreach campaign to understand who was contacted, how communities responded, and whether past disaster exposure influenced targeting.

The analysis includes data cleaning, demographic insights, disaster correlation, and visual reporting.

---

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
# Activate it
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
````

### 2. Install Required Packages

```bash
pip install -r requirements.txt
```

### 3. Prepare Required Files

* Create a folder called `source_files` in the root directory.
* Place the following static files in that folder:

  * `call_data_assessment.csv`
  * `unique_zip_county_with_fips.csv`

> These files are treated as static for now due to time constraints. Automating this is possible later.

---

## How to Run

From the project root, run these scripts in order:

```bash
# Step 1: Clean the data
python scripts/1.data_cleaning.py

# Step 2: Analyze demographic patterns
python scripts/2.analyze_targeting.py

# Step 3: Merge with disaster data and generate visuals
python scripts/3.disaster_merge_analysis.py

# Step 4: Launch the dashboard
streamlit run scripts/4.streamlit_dashboard.py
```

Once Step 4 is run, the dashboard will open at:

```
http://localhost:8051
```

Unless the port is changed. You can explore KPIs and visuals from there.

> A PDF version of the dashboard is also saved at: `dashboard/dashboard.pdf`

---

## Output Summary

* All **final reports** are saved in the project **root folder**
* All **charts, tables, and images** are saved in the **`dashboard/`** folder

---

## Final Reports

* `Client_Ready_Report_Final.pdf`
* `Formatted_Final_Proposal_Submission.pdf`
* `Targeting_Strategies_Report.pdf`
* `Q3_Disaster_Exposure_Analysis.pdf`
* `Final_Client_Report_With_Impact_Statement.pdf`

---

## Notes

* Scripts must be run from the **project root folder**
* Data was cleaned and standardized for analysis
* Dashboards and reports are prepared for non-technical clients
