Readme

# FEMA Assistance Trends across Income and Race Indicators
This project seeks to visualize FEMA assistance trends across income and race indicators for the Indiviudals and Households Program (IHP). IHP provides funds directly to individuals who have been affected by a FEMA declared disaster. In response to concerns that FEMA does not equitably distribute its assistance, this project visualizes assistance trends at the county and zip code level for a state of interest. Initially designed to visualize and map assistance trends in Louisiana, this project can be potetnailly used for other states by changing a part of the code in script 1B_fips data clean.py to a state of interest.

This project is useful in creating scatterplots, historgraphs, and heat maps that show potential trends in who receives IHP assistance within a state. By looking at variations in application rates, approval rates, and average amounts of assistance per application, this project can be a first step towards understanding if there are discrepancies within a state of which zip codes and counties apply, get approved, and 
receive assistance. By including the race and income indciators from the Census, we can visualize trends between important socioeconomic demographics and IHP assistance variables to get initial insight into potential assistance patterns in a state and if these patterns signal equity.  

*1) Run 1A_disaster clean.py*

**Input:**
This script cleans FEMA’s **DisasterDeclarationsSummaries.csv**. This file can be downloaded at:  https://www.fema.gov/openfema-data-page/disaster-declarations-summaries-v2 

**Function:**
It includes information on FEMA declared disasters including the declared disaster number and the county and state FIPS code for counties affected. The declared disaster number is a number that FEMA assigns to different disasters. The **DisasterDeclarationsSummaries.csv** file also includes the counties and states affected by each disaster. Cleaning steps included creating the GEOID from the state and county separate FIPS code.

**Outputs:**
Change the acronym and state FIPS code to run the repository through your state of interest at line 23 for series state_list. The series is saved to an excel file titled **state_list.xlsx** that will be used in future scripts to run plots and maps for the state of interest.

**Disaster_number.csv** is a file that has all the disasters that have affected the state of interest. The file also includes the counties that were affected by the disaster.

*2) Run 1B_fips data clean.py*

**Input:**
This file inputs **disaster_number.csv** and aggregates the information by county to receive the number of disasters each county in the state of interest has experienced.

**Function:**
This script checks to see if there are GEOIDs with different county names or if entries with the same county have more than one GEOID.

GEOID codes with multiple county names may occur if there are misspellings or if counties have been renamed or redistricted throughout time. The print statement at line 36 will return any GEOID codes with multiple county names. Lines 40-43 can be used to clean any duplicated GEOID codes.

Line 56 prints the same county that has different GEOID codes. Counties with multiple GEOID codes may occur if FEMA has entered some entries without a county FIPS code. Counties without a county FIPS code end 000 (3 zeros). If counties are printed in Line 56, lines 58-68 should be run to change counties' correct GEOID to the correct GEOID if known.

**Output:**
This script creates **fip_disaster_count.csv** which contains an entry for each GEOID, county name, state, and the number of disasters the county has experienced over time.

*3) Run 2_ihp_info.py*

**Input:** 
This script uses the **Registration Intake Individuals Household Program.csv** from FEMA that can be downloaded at: https://www.fema.gov/openfema-data-page/registration-intake-and-individuals-household-program-ri-ihp-v2

This document includes information on Individual and Household Program applications, approvals, and assistance. Each entry includes the city, zip code, declared disaster number, and county name. Information is documented at the zip code level and includes the county name but not a GEOID.

**disaster_number.csv** is used in this script to filter out applications for disasters that have not affected the state of interest. **State_list.xlsx** is also included to make sure that only entries for the state of interests are kept in the ihp dataframe.

**Function:**
This script cleans IHP assistance information to ensure zipcodes are either 5 or 9 digits long. Also, this script ensures that ihp[‘county’] is in the same format as the 'county' column in **fips_disaster_count.csv** as that will be the join merge key.

**Output:**
**ihp.csv** is the output. The csv file includes information on the amount of IHP assistance, number of applications, and approvals for each declared disaster number by zipcode.

*4) Run 3_join.py*

**Input:**
**fip_disaster_count.csv** and **ihp.csv** are inputs and are merged on the key ‘county.’

**Function:**
This merge allows for **ihp.csv** information that is reported at the zip code level to be merged to its respective county. As a result, each county entry receives an aggregated amount of IHP assistance, approval rates, and average per approved project across all disasters in the state. This is done for counties that have had more than 0 applications. By aggregating zip code information to the county level, we will be able to analyze later on which counties have undergone the most declared disasters and total people affected across the years. 

The script also aggregates IHP assistance, approval rates, and average per approved project for each zip code. 

**Output:**
**zipcode_amount.csv** has the aggregated IHP amounts (‘ihpAmount’) by zip code as well as the average amount of assistance per approved project(‘average_project), and approval rate (‘approved_rate’). **fips_amount.csv** has the same information aggregated at the county level.

*5) Run 4_zipcode.py*

**Input:** 
The variables {'B02001_001E':'pop_total', 'B02001_002E':'pop_white', 'B02001_003E':'pop_black', 'B03001_003E':'pop_latino', 'B06011_001E':'median_income'} are called from the Census's 2020 American Community Survey 5-year survey using an API key.

**zipcode_amount.csv** is also an input file. The csv file includes the the aggregated IHP amounts (‘ihpAmount’) by zip code as well as the average amount of assistance per approved project(‘average_project), and approval rate (‘approved_rate’)

**Function:**
This script joins information from the Census to the IHP assistance information at the zipcode level in **zipcode_amount.csv**. This script also creates the columns **census_join['application_per_thousand']**
and **census_join['approval_per_thousand']** which represent the number of applications and approvals by thousand people in the zip code. This does not signify **total_affected** ( calcuated by total population*number of FEMA disasters). Initaially, I wanted to look at **total_affected** at the zip code level. However, I ran into issues for accurately calculating **total_affected** as the same zip code belonged to multiple counties. As a result, the columns 'application_per_thousand' and 'approval_per_thousand' represent the total of applications and approvals by the total population in the zip code rather than **total_affected.** This script also calculates the percentage of non-white, white, Black, and Latino population per zip code.

It is important to note that zip codes associated with some IHP applications could be PO boxes or mail centers that are not included in the Census zip code tabulation areas tables. As a result, there may be a number of zip codes that are not merged into the census_join (‘right_only’ result) in lines 55 and 57. Also, some zip codes may have been incorrectly inputed into the IHP application information, which means that they would not appear in the Census zip code tabulation areas tables.

**Output:**
**census_info_zips.csv** contains the merged information from the Census and IHP assistance at the zipcode level.

*6) Run 5_fips_ratios*

**Input:**
The variables {'B02001_001E':'pop_total', 'B02001_002E':'pop_white', 'B02001_003E':'pop_black', 'B03001_003E':'pop_latino', 'B06011_001E':'median_income'} are called from the Census's 2020 American Community Survey 5-year survey using an API key.

**fips_amount.csv** is also input file. The file includes the the aggregated IHP amounts (‘ihpAmount’) by county as well as the average amount of assistance per approved project (‘average_project), and approval rate (‘approved_rate’)

**Function:**
First, **fips_amount.csv** is called as the dis_aid dataframe. dis_aid represents all counties that have more than zero IHP applications.

Then, dis_aid is merged onto the Census data into the dataframe **census_join.** census_join [‘total_affected’], in contrast to the script on zip codes, calculates the **total population*number of FEMA declared disasters** in a county. The result from this calculation will be used to analyze counties' number of disasters and people affected across time. This script calculates the percentage of non-white, white, Black, and Latino population per county.

This script also creates a series of scatterplots that map assistance trends across the following variables: median income, application per thousand affected, approvals per thousand affected, racial demographics, and approval rates.

Also, reference lines are created for each variable by takng the median of all counties and saving it into the **state** dataframe. The reference lines are used in the scatterplots to show the state median for each variable.

**Outputs:** **census_info_fips.csv** includes census variables and IHP assistance information at the county level.

The script also creates various scatterplots that visualizes assistance trends in connection to county's median income and racial demographics. The following scatterplots are visualized and saved as images:

**Image_A_Applications and Approvals by Millions Affected.png** shows the IHP applications and approvals per thousand people affected. The hue and size of the dots demonstrate total affected in millions. Each dot represents a county.

**Image_B_Income and Applications.png** demonstrates applications per thousand people affected and approval rates by median income. The hue and size of dots represent total people affected in millions. Each dot represents a county.

**Image_C_Applications by Race.png** shows a two-axis scatterplot that compares the applications per thousand people affected by percent white and black people per county. The hue and size of dots represent total people affected in millions. Each dot represents a county.

**Image_D_Approval and Race.png** shows a two-axis scatterplot that compares approvals per thousand people affected by percent of white and black people per county. Each dot represents a county.

**Image_E_Non-White and Applications.png** shows applications per thousand people affected and approval rates by percent of non-white population in each county. The hue and size of dots represent total people affected in millions. Each dot represents a county.

**Image_F_Applications, Income, Approval Rate by non-white.png** shows applications per thousand affected and approval rate by median income of a county. The hue and size 
of dots represent percent of non-white in the county’s population. Each dot represents a county.

**Image_G_Amount per Project and Race.png** shows the average amount per project by percent non-white and white. The hue represents the approval rate for the counties. Each dot represents a county.

*7) Run 6_zipfigures*

**Input:**
**census_info_zips.csv** and **census_info_fips.csv** are the input files.

**Function:**
This script creates histograms at both the county and zip code level to visualize trends for a set of variables described below for counties based on their percent of white population. 

This script divides the file's 'pct_white' column into two categories using the variable more_white. The variable more_white has two conditions: Yes and No to easily show whether a county's population is 50% white or more. 'Yes' corresponds to counties that have populations that are 50% or more white. 'No' corresponds to counties that have populations that less than 50% white. 

**Output:** The histograms plot distributions for the following variables: 'approved_rate','application_per_thousand', 'median_income', and 'average_project' at the zip code and county levels. There are two groups in each histogram: one group represents the 'Yes' condition for more_white and the other represents the 'No' condition for more_white.

*8) Run 7_mapping.py*

**Input:**
The following shapefiles were used from the Census to map the different geographic layers at the state, county, and zip code layer:
* **State shapefile:** cb_2020_us_state-500k.zip
https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2020.html      
* **County shapefile:** cb_2019_us_county_500k.zip https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2020.html
* **Zip code shapefile:** Cb_2020_us_zcta510_500k.zip
https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2020.html

**Function:**
This script uses geopandas to map **census_info.fips.csv** and **census_info_zips.csv** for different variables. After running the script, open QGIS and open the file **mapping.qgz** 

**Variables Mapped by Layer**

*Zip code level:* Heat maps include approval rates, median income, applications per thousand people, total population,percent non-white, and average amount per approved project for zip codes that have applied for IHP assistance.

*County level:* Heat maps include number of FEMA disasters experienced by county, total affected, and applications per thousand people affected.

These are various layers that you can review based on your variables for interest. However, to make sure that information has been updated after running the scripts, click on the layer you want to review. Scroll down to layer styling for the layer.

Scroll down to the button **classify** and click it. This will ensure you have the updated intervals and information for the variable and state of interest.

**Output:**
This script creates the output **joined.gpkg** which is the geopackage for the mapping. **mapping.qgz** can be opened to show the maps with the above mentioned layers

Enjoy!
