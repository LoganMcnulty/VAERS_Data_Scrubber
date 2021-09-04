# # Covid-19 Vaccine Symptom Analysis
# ### Data provided by https://vaers.hhs.gov/data.html

# +
import pandas as pd
import numpy as np
from datetime import date, timedelta
from pandas.io.json import json_normalize
import datetime as dt
from pandas.tseries.offsets import DateOffset
import time

pd.set_option('display.max_columns', 130)
pd.set_option('display.max_rows', 130)
# -

# ## Source File Locations

# +
""" If you unpack the  downloaded VAERS .zip onto your desktop, just replace XXX here with User """

vaersVax = r'C:\Users\  XXX  \Desktop\2021VAERSData\2021VAERSVAX.csv'
vaersProfiles = r'C:\Users\  XXX  \Desktop\2021VAERSData\2021VAERSDATA.csv'
vaersSymptoms = r'C:\Users\  XXX  \Desktop\2021VAERSData\2021VAERSSYMPTOMS.csv'
# -

# ~ There may be some columns of the Symptoms file that you are interested in, check "Read symptom case profile file" line 13 to change columns that are kept or removed

# ## VAERS Vax ID, filtering on Vax Type

# +
def read_VaxType(vaersVax):
# Read in file
    print('- - - - - - - - - - - - - - - - - - - - - - -')
    df_Vax = pd.read_csv(vaersVax, low_memory=False)
    df_Vax['VAERS_ID'] = df_Vax['VAERS_ID'].astype(str).str.strip()
    
# Check for Dupes and remove first instance
    df_Vax['Dupes'] = df_Vax['VAERS_ID'].duplicated()
    dupes = df_Vax[df_Vax['Dupes'] == True].copy().reset_index(drop=True)
    if len(dupes) > 0:
        print(str(len(dupes)) + ' duplicates removed from the dataset (First instance of Dupe is kept)')
        df_Vax = df_Vax[df_Vax['Dupes'] == False].copy().reset_index(drop=True)
        print(str(len(df_Vax)) + ' IDs remaining')
        
# Select desired columns, format as strings
    df_Vax = df_Vax[['VAERS_ID', 'VAX_TYPE', 'VAX_MANU', 'VAX_LOT']].copy().reset_index(drop=True)
    df_Vax['VAX_TYPE'] = df_Vax['VAX_TYPE'].astype(str).str.strip()
    df_Vax['VAX_MANU'] = df_Vax['VAX_MANU'].astype(str).str.strip()
    df_Vax['VAX_LOT'] = df_Vax['VAX_LOT'].astype(str).str.strip().str.title()
    df_Vax.columns = df_Vax.columns.astype(str).str.strip().str.title()
    
# Filter on Covid-19 only vaccines
    df_CovidVax = df_Vax[df_Vax['Vax_Type'] == 'COVID19'].copy().reset_index(drop=True)
    manufacturers = df_CovidVax['Vax_Manu'].sort_values().unique()
    totalReports = len(df_CovidVax)
    print('Num. Covid-19 Vax Symptom Reports: ' + str(totalReports))
    print('Unique Manufacturers: ' + str(manufacturers))
    print('- - - - - - - - - - - - - - - - - - - - - - -')
    for m in manufacturers:
        numReports = len(df_CovidVax[df_CovidVax['Vax_Manu'] == m].copy().reset_index(drop=True))
        print(str(m) + " is " + str(round(numReports/totalReports*100, 2)) + "% of reports")
        
    return df_CovidVax
# df_CovidVaxID = read_VaxType(vaersVax)


# -

# ## Read symptom case profile file

# +
def case_profiles(vaersProfiles):

# Read file
    df_Data = pd.read_csv(vaersProfiles, low_memory=False)
    df_Data['VAERS_ID'] = df_Data['VAERS_ID'].astype(str).str.strip()
    
# Check for Dupes
    df_Data['Dupes'] = df_Data['VAERS_ID'].duplicated()
    dupes = df_Data[df_Data['Dupes'] == True].copy().reset_index(drop=True)
    if len(dupes) > 0:
        print(str(len(dupes)) + ' duplicates removed from the dataset (First instance of Dupe is kept)')
        df_Data = df_Data[df_Data['Dupes'] == False].copy().reset_index(drop=True)
        print(str(len(df_Data)) + ' IDs remaining')
    
# Select desired columns, format as strings
    df_Data = df_Data[['VAERS_ID','RECVDATE','VAX_DATE', 'ONSET_DATE', 
                       'AGE_YRS','SEX','DIED','RECOVD', 'NUMDAYS', 
                       'CUR_ILL','HISTORY','BIRTH_DEFECT', 
                       'ALLERGIES','ER_ED_VISIT', 'DATEDIED']].copy().reset_index(drop=True)
    df_Data['RECVDATE'] = df_Data['RECVDATE'].astype(str).str.strip()
    df_Data['VAX_DATE'] = df_Data['VAX_DATE'].astype(str).str.strip()
    df_Data['ONSET_DATE'] = df_Data['ONSET_DATE'].astype(str).str.strip().str.title()
    df_Data['AGE_YRS'] = df_Data['AGE_YRS'].astype(str).str.strip().str.title()
    df_Data['SEX'] = df_Data['SEX'].astype(str).str.strip().str.title()
    df_Data['DIED'] = df_Data['DIED'].astype(str).str.strip().str.title()
    df_Data['DATEDIED'] = df_Data['DATEDIED'].astype(str).str.strip().str.title()
    df_Data['RECOVD'] = df_Data['RECOVD'].astype(str).str.strip().str.title()
    df_Data['NUMDAYS'] = df_Data['NUMDAYS'].astype(str).str.strip().str.title()
    df_Data['CUR_ILL'] = df_Data['CUR_ILL'].astype(str).str.strip().str.title()
    df_Data['HISTORY'] = df_Data['HISTORY'].astype(str).str.strip().str.title()
    df_Data['BIRTH_DEFECT'] = df_Data['BIRTH_DEFECT'].astype(str).str.strip().str.title()
    df_Data['ALLERGIES'] = df_Data['ALLERGIES'].astype(str).str.strip().str.title()
    df_Data['ER_ED_VISIT'] = df_Data['ER_ED_VISIT'].astype(str).str.strip().str.title()
    df_Data.columns = df_Data.columns.astype(str).str.strip().str.title()
    
    return df_Data
# df_CaseProfiles = case_profiles(vaersProfiles)


# -

# ## All Vaccine Symptom Details File

# +
def read_SympDetails(vaersSymptoms):
    
# Read file
    df_Symp = pd.read_csv(vaersSymptoms, low_memory=False)
    df_Symp['VAERS_ID'] = df_Symp['VAERS_ID'].astype(str).str.strip()
    
# There are a lot of duplicated VAERS ID rows for symptoms
# They are removed and only the first row is kept
# this tarnishes the dat a little
    df_Symp['Dupes'] = df_Symp['VAERS_ID'].duplicated()
    dupes = df_Symp[df_Symp['Dupes'] == True].copy().reset_index(drop=True)
    if len(dupes) > 0:
        print(str(len(dupes)) + ' removed from the dataset')
        df_Symp = df_Symp[df_Symp['Dupes'] == False].copy().reset_index(drop=True)
        print(str(len(df_Symp)) + ' IDs remaining')
    
# select columns and format
    df_Symp = df_Symp[['VAERS_ID', 'SYMPTOM1', 'SYMPTOM2', 'SYMPTOM3', 'SYMPTOM4', 'SYMPTOM5']].copy().reset_index(drop=True)
    df_Symp['SYMPTOM1'] = df_Symp['SYMPTOM1'].astype(str).str.strip()
    df_Symp['SYMPTOM2'] = df_Symp['SYMPTOM2'].astype(str).str.strip()
    df_Symp['SYMPTOM3'] = df_Symp['SYMPTOM3'].astype(str).str.strip()
    df_Symp['SYMPTOM4'] = df_Symp['SYMPTOM4'].astype(str).str.strip()
    df_Symp['SYMPTOM5'] = df_Symp['SYMPTOM5'].astype(str).str.strip()
    df_Symp.columns = df_Symp.columns.astype(str).str.strip().str.title()
    df_Symp = df_Symp.replace('nan', np.nan)
    
    return df_Symp
# df_SympDetails = read_SympDetails(vaersSymptoms)


# -

# ## Merge three files on VAERS_ID and analyze

# +
def execute(vaersVax, vaersProfiles, vaersSymptoms):
    df_CovidVaxID = read_VaxType(vaersVax)
    df_CaseProfiles = case_profiles(vaersProfiles)
    df_SympDetails = read_SympDetails(vaersSymptoms)
    
## Merge case profiles
    print('- - - - - - - - - - - - - - - - - - - - - - -')
    print("Merge Vax IDs on Vax Case Profiles using Vaers_ID")    
    print('Length initial Vax ID dataframe ' + str(len(df_CovidVaxID)))
    df_Merge = pd.merge(df_CovidVaxID, df_CaseProfiles, on='Vaers_Id',how='left')
    print('Length merged dataframe ' + str(len(df_Merge)))
    
    df_Null = df_Merge[df_Merge['Vax_Type'] != 'COVID19'].copy().reset_index(drop=True)
    df_Valid = df_Merge[df_Merge['Vax_Type'] == 'COVID19'].copy().reset_index(drop=True)
    
    if (len(df_Null) != len(df_Valid)):
        print('Length case profiles not matching to Covid19 (invalid data) ' + str(len(df_Null)))
        print('Length case profiles matching to Covid19 (valid data) ' + str(len(df_Valid)))
    else:
        print("Profile match successful")
    
### Merge Symptoms
    print('- - - - - - - - - - - - - - - - - - - - - - -')
    print("Merge df_Valid to their vax symptoms")
    df_Final = pd.merge(df_Valid, df_SympDetails, on='Vaers_Id',how='left')
    df_Final = df_Final[df_Final['Vax_Type'] == 'COVID19'].copy().reset_index(drop=True)
    print('Length final valid cases ' + str(len(df_Final)))
    
# Check for Dupes
    df_Final['dupes'] = df_Final['Vaers_Id'].duplicated()
    if (len(df_Final[df_Final['dupes'] == True])):
        print("FAIL: Duplicated IDs")
        return
    
# Final Format of data types

# Floats
    df_Final['Age_Yrs'] = df_Final['Age_Yrs'].astype(str).replace('Nan', np.nan).replace('nan',np.nan).astype(float)
    df_Final['Numdays'] = df_Final['Numdays'].astype(str).replace('Nan', np.nan).replace('nan',np.nan).astype(float)
    
# Dates
# To filter bad dates...
# df_ValidDates = df[~pd.isnull(df['date'])]
    fillerDate = '2000.01.01'
    df_Final['Recvdate'] = pd.to_datetime(df_Final['Recvdate'].replace('nan',fillerDate).replace('Nan',fillerDate).fillna(fillerDate)).replace(pd.to_datetime(fillerDate),np.nan)
    df_Final['Vax_Date'] = pd.to_datetime(df_Final['Vax_Date'].replace('nan',fillerDate).replace('Nan',fillerDate).fillna(fillerDate)).replace(pd.to_datetime(fillerDate),np.nan)
    df_Final['Onset_Date'] = pd.to_datetime(df_Final['Onset_Date'].replace('nan',fillerDate).replace('Nan',fillerDate).fillna(fillerDate)).replace(pd.to_datetime(fillerDate),np.nan)
    df_Final['Datedied'] = pd.to_datetime(df_Final['Datedied'].replace('nan',fillerDate).replace('Nan',fillerDate).fillna(fillerDate)).replace(pd.to_datetime(fillerDate),np.nan)
    df_Final = df_Final.replace('nan', np.nan)

    return df_Final

df_Final = execute(vaersVax, vaersProfiles, vaersSymptoms)

# +
""" this data shows a slight relationship between % of symptoms by manufacturer, and % deaths by manufacturer"""

numDeaths = len(df_Final[df_Final['Died'] == 'Y'].copy().reset_index(drop=True))
manufacturers = df_Final['Vax_Manu'].sort_values().unique()
for m in manufacturers:
    theseDeaths = len(df_Final[(df_Final['Died'] == 'Y') & (df_Final['Vax_Manu'] == m)])
    print(str(m) + " is " + str(round(theseDeaths/numDeaths*100, 2)) + "% of deaths")
