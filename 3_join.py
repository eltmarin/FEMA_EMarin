#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 14:01:40 2022

@author: liz
"""

#This script joins county-level information and IHP assistance information that has information by zipcode
import pandas as pd
import numpy as np

string = {'FIP_disaster_count': int, 'GEOID': str}
fips = pd.read_csv('fip_disaster_count.csv', dtype=string ) #opens file

#%% Read IHP file
string = {'zipcode':str, 'disasterNumber':str}
ihp = pd.read_csv ('ihp.csv', dtype =string)
#%%Grouping of data by zip code and summing IHP assistance by zipcode for future mapping
grouped = ihp.groupby(['zipcode','county'])
ihp = grouped.sum('ihpAmount')
ihp = ihp.reset_index()

#%% Joining FIPS disaster count with IHP assistance information

join = ihp.merge(fips, on ='county', how='left', validate = 'm:1', indicator = True)
print (f"Merge Indicator for IHP and FIPS code DataFrames: \n{join['_merge'].value_counts()}")

join = join.query ('_merge !="right_only"')
column_list = list(join)

drop = ['_merge', 'haReferrals','haEligible',
'haAmount','onaReferrals','onaEligible','onaAmount', 'validCallCenterRegistrations',
'validWebRegistrations', 'validMobileRegistrations']
join = join.drop (columns =drop)
join = join.rename(columns ={'county_x':'county', 'state_x': 'state'})

#For future analysis, we will be dividing columns to get rates for approval and average project.
#By filtering out for more than 0 applications, we can control for undefined numbers. 
num_regs = join['totalValidRegistrations']
join = join[ num_regs > 0 ]
#%% Grouping of data by zip code and summing IHP assistance by zipcode for future mapping
grouped = join.groupby(['zipcode','state'])
amount = grouped.sum('ihpAmount')

print(f'Number of zip codes: \n{len(amount)}')
#%% This reviews if there are any NaN values in IHP amount
num_amount = pd.to_numeric(amount['ihpAmount'], errors ='coerce')
amount_bad = num_amount.isna()
print (f'Records with Non-numeric Amounts in IHP Amount:\n{amount_bad.value_counts()}')

#%% Math Time: This section produces average amount per project and approval rate at the zipcode level
amount['average_project'] = amount['ihpAmount']/amount['ihpEligible']
#rate of approved applications vs applications
amount['approved_rate'] = amount['ihpEligible']/amount['totalValidRegistrations']
amount = amount.reset_index()
amount = amount.dropna()
amount.to_csv('zipcode_amount.csv', index = False)

#%% Math by FIPS code: This will look at information at the county level for future mapping and plotting
fips_group = join.groupby(['GEOID','county','FIP_disaster_count','state'])
fips_amount = fips_group.sum('ihpAmount')
fips_amount = fips_amount.reset_index()
#average per project
fips_amount['average_project'] = fips_amount['ihpAmount']/fips_amount['ihpEligible']

#rate of approved vs applications
fips_amount['approved_rate'] = fips_amount['ihpEligible']/fips_amount['totalValidRegistrations']
fips_amount.to_csv('fips_amount.csv', index = False)



