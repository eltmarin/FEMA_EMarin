#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 17:01:16 2022

@author: liz
"""
zipcode code
# =============================================================================
# ihp_zip = ihp['zipcode']
# 
# ihp_zip = ihp_zip.str.replace(r'\D','', regex=True )
# #This removes any non-digit thing from the script
# ihp_zip = ihp_zip.astype(float)
# #here we convert the zip into a float to read the length
# #units = units.str.strip()
# #%%
# #zip_all = ihp_zip.astype(str).apply(lambda x:x.replace ('.0',''))
# ziplen =ihp_zip.str.len()
# print (f'Lengths of Zipcodes: \n{ziplen.value_counts(dropna=False)}')
# zip_ok = ziplen == 5
# zip_bad = ~ zip_ok
# zip5 = ihp_zip.copy()
# zip5[zip_bad] = None
# zip5len = zip5.str.len()
# print (f'Lengths of Zipcodes after Cleanup:\n{zip5len.value_counts(dropna=False)}')
# ihp['zip'] = zip5
# ihp = ihp.drop (columns = ['zipcode'])
# ihp = ihp.rename(columns ={'zip':'zipcode'})
# =============================================================================
