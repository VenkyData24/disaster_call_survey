#!/usr/bin/env python
# coding: utf-8

"""
Comprehensive Data Cleaning and Integration Script

This workflow performs:
1. Cleaning of raw outreach call data
2. ZIP and county-based FIPS matching
3. Download and processing of US disaster declarations
4. Final merge for analytical use
"""

import pandas as pd
import kagglehub
import os

# ---------------------------------------------------
# Step 1: Clean Outreach Call Data
# ---------------------------------------------------
raw_df = pd.read_csv("source_files/call_data_assessment.csv", dtype={46: str, 47: str}, low_memory=False)

# Remove irrelevant or sensitive columns
columns_to_drop = [
    'Campaign_ID', 'HUBID', 'Phone_Number',
    'Voter_ID', 'Agent_Session_Number', 'Agent_Email_ID',
    'Account_Name', 'Phone_Type'
]
raw_df.drop(columns=[col for col in columns_to_drop if col in raw_df.columns], inplace=True)

# Strip column names and reset index
raw_df.columns = raw_df.columns.str.strip()
raw_df.reset_index(drop=True, inplace=True)

# Create normalized keys for later merge
raw_df['countyclean'] = raw_df['County'].str.lower().str.strip()
raw_df['zipcodeclean'] = raw_df['Zip'].astype(str).str.extract(r'(\d+)', expand=False).str.zfill(5)

# Save intermediate version
raw_df.to_csv("source_files/cleaned_call_data_intermediate.csv", index=False)

# ---------------------------------------------------
# Step 2: Merge ZIP + County to FIPS
# ---------------------------------------------------
call_df = pd.read_csv("source_files/cleaned_call_data_intermediate.csv", dtype=str)
zip_fips_df = pd.read_csv("source_files/unique_zip_county_with_fips.csv", dtype=str)

# Normalize headers and keys
call_df.columns = call_df.columns.str.lower().str.strip()
zip_fips_df.columns = zip_fips_df.columns.str.lower().str.strip()
call_df['zipcodeclean'] = call_df['zip'].str.extract(r'(\d+)', expand=False).str.zfill(5)
call_df['countyclean'] = call_df['county'].str.lower().str.strip()
zip_fips_df['zipcodeclean'] = zip_fips_df['zipcodeclean'].str.zfill(5)
zip_fips_df['countyclean'] = zip_fips_df['countyclean'].str.lower().str.strip()

# Merge to bring in fipsclean column
df_merged = pd.merge(
    call_df,
    zip_fips_df[['zipcodeclean', 'countyclean', 'fipsclean']],
    on=['zipcodeclean', 'countyclean'],
    how='inner'
)

# Save cleaned dataset with FIPS
df_merged.to_csv("source_files/cleaned_call_data_with_fips.csv", index=False)

# ---------------------------------------------------
# Step 3: Download and Prepare Disaster Declaration Data
# ---------------------------------------------------
disaster_path = kagglehub.dataset_download("headsortails/us-natural-disaster-declarations")

for file in os.listdir(disaster_path):
    if file.endswith(".csv"):
        csv_path = os.path.join(disaster_path, file)
        break

disaster_raw_df = pd.read_csv(csv_path)
disaster_raw_df.to_csv("source_files/us_natural_disaster_declarations.csv", index=False)

# Clean county and FIPS keys
disaster_df = pd.read_csv("source_files/us_natural_disaster_declarations.csv")
disaster_df['countyclean'] = (
    disaster_df['designated_area']
    .str.lower()
    .str.replace(r'\(county\)', '', regex=True)
    .str.replace(' ', '')
    .str.strip()
)
disaster_df['fipsclean'] = (
    pd.to_numeric(disaster_df['fips'], errors='coerce')
    .dropna()
    .astype(int)
    .astype(str)
    .str.extract(r'(\d+)', expand=False)
    .str.zfill(5)
)

# ---------------------------------------------------
# Step 4: Merge Disaster Info with Call Data
# ---------------------------------------------------
call_df = pd.read_csv("source_files/cleaned_call_data_with_fips.csv")

call_df['fipsclean'] = call_df['fipsclean'].astype(str).str.zfill(5)
call_df['countyclean'] = call_df['countyclean'].str.lower().str.strip()
disaster_df['fipsclean'] = disaster_df['fipsclean'].astype(str).str.zfill(5)
disaster_df['countyclean'] = disaster_df['countyclean'].str.lower().str.strip()

final_df = pd.merge(
    call_df,
    disaster_df[['fipsclean', 'countyclean', 'incident_type', 'incident_begin_date', 'incident_end_date', 'declaration_type']],
    on=['fipsclean', 'countyclean'],
    how='inner'
)

final_df.drop_duplicates(inplace=True)
# Save final dataset for analysis
final_df.to_csv("source_files/final_merged_call_disaster_stats.csv", index=False)
