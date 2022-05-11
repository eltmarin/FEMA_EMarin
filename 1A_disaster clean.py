# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#This script cleans the Disaster Declarations Summaries CSV and only takes the disasters
#that impacted the state of interest

import pandas as pd

string = {'fipsStateCode': str, 'fipsCountyCode': str, 'disasterNumber': str, 
          'fyDeclared':str, 'declarationRequestNumber': str}
dis = pd.read_csv('DisasterDeclarationsSummaries.csv', dtype=string)

#this allows us to look at the columns in dis for renaming and other issues
column_list = list(dis)
dis = dis.rename(columns={'disasterNumber': 'disaster_number'})

#%% Queries only the states in the list
#This will make it easier if another state is of interest to change throughout the script
state_list = pd.Series(['OK','40'])
#change line 23 to state of interest

state_list.to_excel('state_list.xlsx')

dis = dis.query('state in @state_list').copy()
#%%Here we are creating the fipscode with the state and county and replacing any spaces for later joining
#As the script did not come with this

dis ['FIPS'] = dis['fipsStateCode']+" "+dis['fipsCountyCode']
dis ['FIPS'] = dis ['FIPS'].str.replace( r'\s+', '', regex=True )
dis = dis.drop(columns = ['fipsStateCode','fipsCountyCode', 'declarationDate'])
dis=dis.rename(columns={'FIPS':'GEOID'})
#column_list = list(dis)

#%%% cleaning counties to see what areas are counties and which are not
#this will make merging with Individuals and Housing Program Assistance dataset easier to merge
#as that dataset only has the county name and not the type
old_place = dis['designatedArea']
new_county = old_place.str.split('(', n = 1, expand = True)
  
# making separate first name column from new data frame
dis["county"]= new_county[0]
dis['type'] = new_county[1]
dis['type']= dis['type'].fillna('None')
print (f"Types of Areas:\n{dis['type'].value_counts()}")

#%%This section puts the dis dataframe into a csv that has the diaster numbers
#that have impacted the state of interest. This will be used to clean the IHP assistance information 

var_list =['disaster_number','GEOID','county','state']
dis_number = dis.groupby(var_list).size()
print (f"Disasters by Number of Counties Eligible: \n{dis_number.sort_values(ascending=False)}")
dis_number = dis_number.reset_index()
dis_number = dis_number.drop(columns=0)

dis_number.to_csv('disaster_number.csv', index=False)

