#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 23:30:40 2022

@author: liz
"""
# This script does the Census and FEMA information join at the county level for graphing assistance trends.
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

variables = {'B02001_001E':'pop_total', 'B02001_002E':'pop_white', 
             'B02001_003E':'pop_black', 'B03001_003E':'pop_latino', 'B06011_001E':'median_income'}

var_list = variables.keys()
var_string = ",".join(var_list)
api = "https://api.census.gov/data/2020/acs/acs5" 
get = var_string
for_clause = 'county:*'
key_value = 'f7e6ea72856a66b6dbc33cd769783f8bf4396da1'
payload = {'get':var_string, 'for':for_clause, 'key':key_value}

response = requests.get(api,payload) 
if response.status_code == 200: #this tests if the response.status_code equals 200 which is the HTTp status code for success
    print ('Request Succeeded')
else: 
    print (f'status:{response.status_code}' ) #this is an else statement which occurs if the response
    #status code isn't 200
    print (response.text)
    assert False #this causes the script to stop if statemtn is reached

#saving the API information as a dataframe
row_list = response.json() 
colnames = row_list [0] 
datarows = row_list[1:] 
fips = pd.DataFrame(columns = colnames, data=datarows)
fips = fips.replace('-666666666',np.nan)
fips = fips.rename(columns=variables)
fips_list= list(fips)
# combine state and county
fips['GEOID'] = fips['state']+''+fips['county']
fips['GEOID'] = fips['GEOID'].astype(str)
#%% Here we join the file with all disaster-affected counties with the counties that requested assistance
#to see if there are any counties that were eligible but did not register for assistance
string = {'GEOID': str}
dis_aid = pd.read_csv('fips_amount.csv', dtype=string) 
dis_aid = dis_aid.groupby('GEOID').sum('ihpAmount')

#%% This cell joines dis_aid information to census information
census_join=dis_aid.merge(fips, on='GEOID', how ='left', validate = '1:1', indicator = True)

print (f'Value Counts for Merge: \n{census_join["_merge"].value_counts()}')
#the left_only are the duplicated FIPS codes that lack the county code
census_join = census_join.query('_merge == "both"')
print (f'Value Counts for Merge: \n{census_join["_merge"].value_counts()}')
census_join = census_join.drop(columns=['_merge'])

#%% This will look at these variables from the Census
number_columns = ['pop_total','pop_white', 'pop_black' , 'pop_latino', 'median_income']
census_join[number_columns] = census_join[number_columns].apply(pd.to_numeric)
#%%#%% Taking information by people affected and populations
#total affected is in millions
census_join['total_affected'] =(census_join['FIP_disaster_count'])*(census_join['pop_total'])/1e6
#total applications by people affected
census_join['application_per_thousand'] = census_join['totalValidRegistrations']/census_join['total_affected']/1000
#this is approvals per 1000 people
census_join['approval_per_thousand'] = census_join['ihpEligible']/census_join['total_affected']/1000

#average percentage of X people
census_join ['pct_black'] = census_join['pop_black']/census_join['pop_total']
census_join ['pct_white'] = census_join['pop_white']/census_join['pop_total']
census_join['pct_latino'] = census_join['pop_latino']/census_join['pop_total']
census_join ['non_white'] = (census_join['pop_total'] - census_join['pop_white'])/census_join['pop_total']
#%% Now we will find the state average for each of the variables calculated 
#these will be used for reflines
state = census_join.groupby('state').median()
print (f'State summary: {state.describe()}')
state_list= list(state)
state_pct_black = float(state['pop_black']/state['pop_total'])
state_pct_white = float( state['pop_white']/state['pop_total'])
state_pct_latino = float(state['pop_latino']/state['pop_total'])
state_non_white = float((state['pop_total'] - state['pop_white'])/state['pop_total'])
state_average= float(state['average_project'])
state_approval_rate = float(state['approved_rate'])
state_application_thousand =float(state['application_per_thousand'])
state_approval_thousand=float(state['approval_per_thousand'])
state_income = float(state['median_income'])
census_join.to_csv('census_info_fips.csv', index = False)
#this will be used to create the histograms

#%% Applications and Approvals by Millions affected
plt.rcParams['figure.dpi'] = 300
fg = sns.relplot(data=census_join, x='application_per_thousand', y='approval_per_thousand', 
                 hue='total_affected', size ='total_affected', 
                 sizes=(10,200), 
                 facet_kws={'despine': False, 'subplot_kws': {'title': 'Applications and Approvals by Millions Affected,\n for counties with more than 0 applications'}})

fg.set_axis_labels('Applications per thousand affected','Approvals per thousand affected')
fg.refline(y=state_approval_thousand, x=state_application_thousand)
total = fg._legend.set_title('Millions Affected')
sns.move_legend(fg, "center right")
fg.tight_layout()
fg.savefig('Image_A_Applications and Approvals by Millions Affected.png')
#this image shows the applications and approvals for IHP per thousand people affected while the circles
#demosntrates millions affected. 
#%% Applications and Approval Rates by Income levels as well people affected
plt.rcParams['figure.dpi'] = 300
fig1, (ax1, ax2) = plt.subplots(1,2)
sns.scatterplot(data=census_join, x='application_per_thousand', y='median_income',hue="total_affected",size ='total_affected', 
                sizes = (8,150), ax=ax1)

sns.scatterplot(ax=ax2, data=census_join, x='approved_rate', y='median_income', 
                hue="total_affected",size ='total_affected', sizes = (8, 150))

ax1.set_xlabel('Applications per Thousand Affected')
ax1.set_ylabel('Median Income')
ax2.set_xlabel('Approval Rate')
ax2.set_ylabel('Median Income')
ax1.axvline(x=state_application_thousand)
ax1.axhline(y=state_income)
ax2.axvline(x=state_approval_rate)
ax2.axhline(y=state_income)
ax1.get_legend().remove()
ax2.legend(bbox_to_anchor=(1,-.3), loc='lower left', ncol= 1, title = "Millions\nAffected", fontsize = 8)
fig1.suptitle('Applications and Approval Rate by Income \n for counties with more than 0 applications')
fig1.tight_layout()
fig1.savefig('Image_B_Income and Applications.png')
#This image looks at applications and approval rates by median income. The hue and size represent total people affected
#%% This compares application per thousand by percent white and percent black
plt.rcParams['figure.dpi'] = 300
fig1, (ax1, ax2) = plt.subplots(1,2)
sns.scatterplot(data=census_join, x='application_per_thousand', y='pct_white', 
                ax=ax1, hue="total_affected", size ='total_affected', sizes =(8,150))

sns.scatterplot(ax=ax2, data=census_join, x='application_per_thousand', y='pct_black', 
                sizes = (8,150), hue="total_affected",size ='total_affected')
ax1.set_xlabel('Applications')
ax1.set_ylabel('Percent White')
ax2.set_xlabel('Applications')
ax2.set_ylabel('Percent Black')
ax1.get_legend().remove()
ax2.legend(bbox_to_anchor=(1,-.3), loc='lower left', ncol= 1, title = "Millions\nAffected", fontsize = 8)
ax1.axvline(x=state_application_thousand)
ax1.axhline(y=state_pct_white)
ax2.axvline(x=state_application_thousand)
ax2.axhline(y=state_pct_black)
fig1.suptitle('Applications by Race, \n for counties with more than 0 applications')
fig1.tight_layout()
fig1.savefig('Image_C_Applications by Race.png')
#This image compares applications by thousand affected by percent of white and black population

#%% This looks at ppproval per thousand by percent white and percent black
plt.rcParams['figure.dpi'] = 300
fig1, (ax1, ax2) = plt.subplots(1,2)
sns.scatterplot(data=census_join, x='approval_per_thousand', y='pct_black', 
                sizes = (8,1500), ax=ax1)

sns.scatterplot(ax=ax2, data=census_join, x='approval_per_thousand', y='pct_white', 
                sizes = (8, 150))
ax1.set_xlabel('Approvals per thousand affected')
ax1.set_ylabel('Percent Black')
ax2.set_xlabel('Approvals per thousand affected')
ax2.set_ylabel('Percent White')
ax1.axvline(x=state_approval_thousand)
ax1.axhline(y=state_pct_black)
ax2.axvline(x=state_approval_thousand)
ax2.axhline(y=state_pct_white)
fig1.suptitle('Approvals by Race, \nfor counties with more than 0 applications')
fig1.tight_layout()
fig1.savefig('Image_D_Approval and Race.png')

##This image compares approvals by thousand affected by percent of white and black population

#%% This looks at applications and approval rate for non-white populations
plt.rcParams['figure.dpi'] = 300
fig1, (ax1, ax2) = plt.subplots(1,2)
sns.scatterplot(data=census_join, x='application_per_thousand', y='non_white', hue="total_affected",size ='total_affected', 
                sizes = (10,200), ax=ax1)

sns.scatterplot(ax=ax2, data=census_join, x='approved_rate', y='non_white', 
               hue="total_affected",size ='total_affected', sizes = (10, 200))

ax1.set_xlabel('Applications per thousand affected')
ax1.set_ylabel('Percent Non-white')
ax2.set_xlabel('Approval rate')
ax2.set_ylabel('Percent Non-white')
ax1.get_legend().remove()
ax2.legend(bbox_to_anchor=(1,-.3), loc='lower left', ncol= 1, title = "Millions\nAffected", fontsize = 8)
ax1.axvline(x=state_application_thousand)
ax1.axhline(y=state_non_white)
ax2.axvline(x=state_approval_rate)
ax2.axhline(y=state_non_white)
fig1.suptitle('Applications and Approvals by Percent Non-white, \nfor counties with more than 0 applications')
fig1.tight_layout()
fig1.savefig('Image_E_Non-White and Applications.png')
##This image compares applications by thousand and approval rated by percent of non-white population

#%% This looks at application and approval rates by median incomes and non-white populations
plt.rcParams['figure.dpi'] = 300
fig1, (ax1, ax2) = plt.subplots(1,2)
sns.scatterplot(data=census_join, x='application_per_thousand', y='median_income',hue="non_white",size ='non_white', 
                sizes = (8,150), ax=ax1)

sns.scatterplot(ax=ax2, data=census_join, x='approved_rate', y='median_income', 
                hue="non_white",size ='non_white', sizes = (8,150))

ax1.set_xlabel('Applications per thousand affected')
ax1.set_ylabel('Median Income')
ax2.set_xlabel('Approval rate')
ax2.set_ylabel('Median Income')

ax1.get_legend().remove()

ax2.legend(bbox_to_anchor=(1,-.3), loc='lower left', ncol= 1, title = "Percent\nNon-white", fontsize = 8)
ax1.axvline(x=state_application_thousand)
ax1.axhline(y=state_income)
ax2.axvline(x=state_approval_rate)
ax2.axhline(y=state_income)
fig1.suptitle('Applications, Income, and Approval Rate \n for counties with more than 0 applications')
fig1.tight_layout()
fig1.savefig('Image_F_Applications, Income, Approval Rate by non-white.png')
# This looks at applications and approval rate by median income of a county. 
#The hue and size signal percent non white of the population

#%% This graph looks at average amount per project based on percent black and percent white
plt.rcParams['figure.dpi'] = 300
fig1, (ax1, ax2) = plt.subplots(1,2)
sns.scatterplot(data=census_join, x='average_project', y='non_white', hue ='approved_rate',
                sizes = (8,1500), ax=ax1)

sns.scatterplot(ax=ax2, data=census_join, x='average_project', y='pct_white', hue ='approved_rate',
                sizes = (8, 150))

ax1.set_xlabel('Average Amount per Project')
ax1.set_ylabel('Percent Non-white')
ax2.set_xlabel('Average Amount per Project')
ax2.set_ylabel('Percent White')
ax1.axvline(x=state_average)
ax1.axhline(y=state_pct_black)
ax2.axvline(x=state_average)
ax2.axhline(y=state_pct_white)
fig1.suptitle('Average Amount per Approved Application by Race, \nfor counties with more than 0 applications')
ax1.get_legend().remove()

ax2.legend(bbox_to_anchor=(1,-.3), loc='lower left', ncol= 1, title = "Approval\nRate", fontsize = 8)
fig1.tight_layout()
fig1.savefig('Image_G_Amount per Project and Race.png')
#THis looks at average amount per project by percent black and white. The hue represents the approval rate for the counties.