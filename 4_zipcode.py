#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 16:51:40 2022

@author: liz
"""

#This script sends an API request for zipcode data from the Census. The information for population, race demographics, and median
#income are requested and joined to the IHP assistance information aggregated at the zipcode level  
import requests
import pandas as pd
import numpy as np

variables = {'B02001_001E':'pop_total', 'B02001_002E':'pop_white', 
             'B02001_003E':'pop_black', 'B03001_003E':'pop_latino', 'B06011_001E':'median_income'}

var_list = variables.keys()
var_string = ",".join(var_list)
api = "https://api.census.gov/data/2020/acs/acs5" #i Used ACS 2019 AS THAT has the most recent information on zip codes
get = var_string
for_clause = 'zip code tabulation area:*'
key_value = 'f7e6ea72856a66b6dbc33cd769783f8bf4396da1'

payload = {'get':var_string, 'for':for_clause,'key':key_value}
response = requests.get(api,payload)  #this call creates a query string than can help collect a response
if response.status_code == 200: #this tests if the response.status_code equals 200 which is the HTTp status code for success
    print ('Request Succeeded')
else: 
    print (f'status:{response.status_code}' ) #this is an else statement which occurs if the response
    #status code isn't 200
    print (response.text)
    assert False #this causes the script to stop if statemtn is reached

#saving as a dataframe
row_list = response.json() #will return a list of rows of response query
colnames = row_list [0] #this takes the elemnet 0 and puts its as column names
datarows = row_list[1:] #puts the rest of the information as the data
zipcode = pd.DataFrame(columns = colnames, data=datarows)
zipcode = zipcode.rename(columns=variables)
zip_list = list(zipcode)
zipcode['zipcode'] = zipcode['zip code tabulation area']
zipcode = zipcode.replace("-666666666", np.nan)
zipcode = zipcode.replace('-666666666.001',np.nan)

#%% This cleans and sets the data for zipcode information to make sure that all zipcodes have been complied into one entry
string = {'zipcode':str, 'GEOID': str}
amount = pd.read_csv('zipcode_amount.csv', dtype = string)
amount_dups = amount.duplicated(subset='zipcode', keep =False) 
dups = amount[amount_dups]
print(f'List of Duplicated Zipcodes: \n{dups["zipcode"].value_counts()}\n') 

#%% This merges the census data and IHP zipcode data
census_join =amount.merge(zipcode, on ='zipcode', how = 'outer', validate = '1:1', indicator = True)
print (f'Value Counts for Merge: \n{census_join["_merge"].value_counts()}')
#%% Here we decide to keep the entries for zipcodes only in the zipcode (IHP) dataframe and those found in both. 
census_join = census_join.query('_merge !="right_only"')
print (f'Value Counts for Merge: \n{census_join["_merge"].value_counts()}\n')

census_join = census_join.drop (columns=['_merge','zip code tabulation area'])
census_join = census_join.rename(columns={'county_x':'county','state_x':'state'})
#%% This makes the following columns into numeric values
number_columns = ['pop_total','pop_white', 'pop_black' , 'pop_latino', 'median_income']
census_join[number_columns] = census_join[number_columns].apply(pd.to_numeric)
#%%#%% This will start looking at different percentages of zip codes based on Census inforamtion

#Application per thousands
census_join['application_per_thousand'] = census_join['totalValidRegistrations']/census_join['pop_total']/1000
#this is approval per 1000 people
census_join['approval_per_thousand'] = census_join['ihpEligible']/census_join['pop_total']/1000
#average percentage of X population 
census_join ['pct_black'] = census_join['pop_black']/census_join['pop_total']
census_join ['pct_white'] = census_join['pop_white']/census_join['pop_total']
census_join['pct_latino'] = census_join['pop_latino']/census_join['pop_total']
census_join ['non_white'] = (census_join['pop_total'] - census_join['pop_white'])/census_join['pop_total']

#%% 
census_join.to_csv('census_info_zips.csv', index = False)
