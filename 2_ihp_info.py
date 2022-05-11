#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 10:54:05 2022

@author: liz
"""
import pandas as pd

#This script cleans IHP assistance information

#Taking list of all disasters impacting state of interest and putting it into a list. This list will be run
#through IHP csv to only include disasters that have hit the state of interest

dis_number = pd.read_csv('disaster_number.csv', dtype =str)
dis_list =list(dis_number['disaster_number'])

#%% Now we import the main information of FEMA assistance and registration
reg = pd.read_csv('RegistrationIntakeIndividualsHouseholdPrograms.csv', dtype = str)

#By running the next two lines, we make sure that we are only looking at the state of interest, before running through disasters
state_list = list(pd.read_excel('state_list.xlsx')[0])
print(f'States to Review: \n{state_list}')

#this takes all the disasters that were in the dis_list and makes a query of assistance for those disasters
ihp = reg.query('disasterNumber in @dis_list').copy() 
#this keeps information only of states in interests rather than states affected by disaster
ihp = ihp.query ('state in @state_list').copy()
#%% This will make the following columns into integers for future analysis

v_list = ['totalValidRegistrations','ihpReferrals', "ihpEligible", 'ihpAmount']
for v in v_list:
    ihp[v] = ihp[v].astype(float)

#%% Rename column for zipcodes
ihp = ihp.rename(columns = {'zipCode':'zipcode'})

#%% Clean zipcodes. To make sure that zipcodes with 9 digits can be salvaged, we run this cell.
# Later scripts will filter out zipcodes not in Census data. 

zip_all =ihp['zipcode'] 
ziplen =zip_all.str.len()

print (f'Count of Zip Code Lengths: \n{ziplen.value_counts(dropna=False)}') 
zip_9 = ziplen==9 
zip_5 = ziplen==5 
zip_ok = zip_5 | zip_9 
zip_bad = ~zip_ok 
zip5 = zip_all.copy()
zip5[zip_9] =zip5[zip_9].str[:5]
zip5[zip_bad] = None 
zip5len = zip5.str.len()
print (f'Number of Records with a Zip Code Length of 5 Digits:\n { zip5len.value_counts(dropna=False)}')
ihp['zipcode'] = zip5 

#%% Changing county to match GEOID data for joining. We will join on county as IHP dataframe does not 
#have county GEOID codes. This makes it difficult to know how many disasters a zipcode may have experienced.

old_county = ihp['county']
new_county = old_county.str.split("(", n = 1, expand = True)
# making separate first name column from new data frame
ihp['county_type'] = new_county[1]
ihp["county"]= new_county[0]

print (f"Types of County:\n {ihp['county_type'].value_counts()}")
ihp["county"] =ihp["county"].str.replace( r'\s+', '', regex=True )
#%%
ihp.to_csv('ihp.csv', index =False)