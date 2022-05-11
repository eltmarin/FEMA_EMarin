#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 16:19:39 2022

@author: liz
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#This script takes the information from the cleaned disaster_number csv to aggregrate disaster count per county

import pandas as pd


string = {'GEOID': str, 'disaster_number': str}
dis_clean = pd.read_csv('disaster_number.csv', dtype=string)
variable_list = ['GEOID','county','state']
fips = dis_clean.groupby(variable_list).size()
#this now has the number of disasters a county has experienced
fips = fips.reset_index()
fips['FIP_disaster_count'] = fips[0].astype(float)
fips = fips.drop(columns = 0)

#%% Here we will check if the state has various different county names for the same FIPS code
# If the print statement comes back with some entries, go to lines 39 to 41 to rename the counties to match
#the desired/accurate county name. For best results, copy names directly from the dataframe.

fips_dups = fips.duplicated(subset=['GEOID'], keep = False)
dups = fips[fips_dups]
print(f'List of Duplicated GEOID codes with Different County Names: \n{dups["GEOID"].value_counts()}\n') 

#%% This cell takes out random spaces to help with any discrepancies in spacing for renaming
fips['county'] = fips['county'].str.replace(r'\s+','', regex=True)
#%% Clean discrepancies in county names 
namechange ={'FoxCrossing':	'Winnebago'}
fips['county'] = fips['county'].replace(namechange)
#For Louisiana, Ward 9 is part of Ascension so I changed Ward 9 to fit Ascension. 

#%% To make sure the information is aggregated after this fix, we run the groupby again and check the print statement
#to make sure it worked
variable_list = ['GEOID','county', 'state']
fips = fips.groupby(variable_list).sum('FIP_disaster_count')
fips = fips.reset_index()
print(f'List of GEOID codes with Number of County Names: \n{fips["GEOID"].value_counts()}\n') 
#Besides the entries with unknown GEOID (which end in 000), all other GEOIDs should have only one entry.

#%% Now, we will check if one county has multiple GEOIDs. States like Oklahama have counties with multiple FIPS
dis_dups = fips.duplicated(subset='county', keep = False)
dups = fips[dis_dups]
print(f'List of Same County Name with Different GEOID codes: \n{dups["county"].value_counts()}\n') 
#If there are counties with different GEOIDs, use the following cell to fix county's various geoids to the appropriate GEOID
#%% Run cell to clean up counties with multiple FIPS entries. This is the example for Oklahoma
fips['GEOID'] = fips['GEOID'].replace("40000", None)
#Often, counties will have one correct GEOID and have some entries with the XX000 format. To fix for this,
#we change all XX000 GEOIDs to none and will use the following loop to enter the appropriate GEOID.
# The first two numbers will be the STATE FP code.
county_list= {'Cherokee': '40021', 'Choctaw': '40023' ,'Creek': '40037', 'Pawnee': '40117','Seminole':'40133'}

for c in county_list.keys():
    is_county = fips['county'] == c
    is_missing = fips['GEOID'].isna()
    fips['GEOID'] = fips['GEOID'].where(~(is_county & is_missing),county_list[c]) 

#%% To aggregrate again, run this cell to ensure counties have only one GEOID code
variable_list = ['GEOID','county','state']
fips = fips.groupby(variable_list).sum('FIP_disaster_count')
fips = fips.reset_index()

print(f'List of Counties with Number of GEOID codes: \n{fips["county"].value_counts()}\n') 
#%% 
fips.to_csv('fip_disaster_count.csv', index=False)
