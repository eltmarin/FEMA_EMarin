#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 12:44:30 2022

@author: liz
"""
#This script maps out at the zipcode level the variables of interests - including 
import requests
import pandas as pd
import geopandas as gpd
import numpy as np
import os

out_file = 'joined.gpkg'
if os.path.exists(out_file):
     os.remove(out_file)
    
string = {'GEOID': str}
county = pd.read_csv('census_info_fips.csv', dtype =string)
geo_county = gpd.read_file("cb_2019_us_county_500k.zip")
joined = geo_county.merge(county, how='outer', validate ='1:1', 
                      on="GEOID",  indicator = True)

print (f"Summary of Merge Results:\n{joined['_merge'].value_counts()}")

joined = joined.query('_merge=="both"').copy()

joined = joined.drop(columns='_merge')

joined.to_file("joined.gpkg",  layer = "county", index=False)

#%%
geo_state = gpd.read_file("cb_2020_us_state_500k.zip")
state_list = list(pd.read_excel('state_list.xlsx')[0])
state_list = state_list[1]
print(f'States to Review: \n{state_list}')
geo_state = geo_state.query('STATEFP in @state_list')

geo_state.to_file("joined.gpkg", layer="state", index=False)
#adds the layer of state to the joined gpkg
    
#%%
string = {'state': str, 'zipcode': str, 'GEOID': str}
zipcode = pd.read_csv('census_info_zips.csv', dtype =string)

zipcode= zipcode.sort_values('zipcode')
d_string = {'ZCTA5CE10': str}
geo_zip = gpd.read_file("cb_2019_us_zcta510_500k.zip", dtype = d_string)
joined = geo_zip.merge(zipcode, how='outer', validate ='1:1', 
                       left_on="ZCTA5CE10", right_on ='zipcode', indicator = True)

print (f"Summary of Merge Results:\n{joined['_merge'].value_counts()}")

joined = joined.query('_merge=="both"').copy()
joined = joined.replace(np.inf, np.nan)
joined = joined.dropna()
joined = joined.drop(columns='_merge')
joined = joined.clip(geo_state, keep_geom_type=True)

joined.to_file("joined.gpkg",  layer = "zip", index=False)