import pandas as pd
import warnings
from tkinter import Tk
from tkinter.filedialog import askopenfilename

warnings.filterwarnings('ignore')

# Prompt user to select a file
Tk().withdraw()  # Hide the root tkinter window
file_path = askopenfilename(
    title="Select a TXT or CSV file to clean",
    filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")]
)

if not file_path:
    print("❌ No file selected. Exiting...")
    exit()

# Load raw data
data = pd.read_csv(file_path)

# --- Step 1: Clean Data ---

# --- Load Agency Translation File (DTagy.txt) ---
agency_map = pd.read_csv('DTagy.txt')  # Ensure this file is in the same folder

# Merge in full agency names
data = data.merge(agency_map[['AGYSUB', 'AGYSUBT']], on='AGYSUB', how='left')
data.rename(columns={'AGYSUBT': 'AGENCY_NAME'}, inplace=True)

# Remove prefix before dash and any surrounding quotes
data['AGENCY_NAME'] = (
    data['AGENCY_NAME']
    .str.replace(r'^.*?-', '', regex=True)  # Remove everything before and including the dash
    .str.replace('"', '', regex=False)      # Remove quotes
    .str.strip()                            # Trim any leftover spaces
)

# Remove rows with missing SALARY or LOS
data_cleaned = data.dropna(subset=['SALARY', 'LOS'])

# Convert float-coded EDLVL and GSEGRD to string for consistent mapping
data_cleaned['EDLVL'] = data_cleaned['EDLVL'].astype(str).str.replace('.0', '', regex=False)
data_cleaned['GSEGRD'] = data_cleaned['GSEGRD'].astype(str).str.replace('.0', '', regex=False)

# --- Step 2: Decode Categorical Fields ---

# Age level mapping
age_map = {
    'A': '<20', 'B': '20-24', 'C': '25-29', 'D': '30-34', 'E': '35-39',
    'F': '40-44', 'G': '45-49', 'H': '50-54', 'I': '55-59',
    'J': '60-64', 'K': '65+', 'L': 'Unknown'
}
data_cleaned['AGE_GROUP'] = data_cleaned['AGELVL'].map(age_map)

# Education level mapping (partial example)
edlvl_map = {
    '01': 'Less than HS', '02': 'High School', '04': 'Associate',
    '13': 'Bachelor’s', '15': 'Master’s', '17': 'Doctorate'
}
data_cleaned['EDUCATION'] = data_cleaned['EDLVL'].map(edlvl_map)

# General Schedule grade (optional rename)
data_cleaned['GS_GRADE'] = data_cleaned['GSEGRD']

# Length of Service level mapping
los_map = {
    'A': '<1 yr', 'B': '1-2 yrs', 'C': '3-4 yrs', 'D': '5-9 yrs',
    'E': '10-14 yrs', 'F': '15-19 yrs', 'G': '20-24 yrs',
    'H': '25-29 yrs', 'I': '30-34 yrs', 'J': '35+ yrs'
}
data_cleaned['SERVICE_YEARS'] = data_cleaned['LOSLVL'].map(los_map)

# PATCO (Occupational category)
patco_map = {
    1: 'Professional', 2: 'Administrative', 3: 'Technical',
    4: 'Clerical', 5: 'Blue Collar', 6: 'Senior Exec', 9: 'Other'
}
data_cleaned['OCC_CATEGORY'] = data_cleaned['PATCO'].map(patco_map)

# Work status
workstat_map = {
    1: 'Full-Time Permanent', 2: 'Other'
}
data_cleaned['WORK_STATUS'] = data_cleaned['WORKSTAT'].map(workstat_map)

# --- Step 3: Export to Power BI-Friendly CSV ---

# Save cleaned and enriched dataset
output_file = 'FedScope_Cleaned_PowerBI.csv'
data_cleaned.to_csv(output_file, index=False)
print(f"✅ Dataset saved as '{output_file}'")
