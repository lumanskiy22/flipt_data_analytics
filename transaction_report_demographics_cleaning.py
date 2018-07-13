#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 16:46:40 2018

@author: lumanskiy
"""
import numpy as np
#Write a consolidated function for all of the demographic variables 
#where only your demographic information and the place it comes from changes
import os 
import re
import json
import numpy as np
import pandas as pd
import datetime as dt
import urllib.request as requests


#First, set the working directory
os.getcwd()
os.chdir('/Users/lumanskiy/Desktop/FliptFiles')

#Next, import all of the files that you are going to need
#Transaction Report (make sure you convert it to a csv before importing)
file1 = 'dailyrxreport.xlsx2018-07-10T123001.813263.csv'
transaction_report1 = pd.read_csv(file1)

file2 = 'AllUsers07022018.csv'
registered_users_report = pd.read_csv(file2)

file3 = 'Adoption_0702_Kimi.csv'
flipt_adoption_report = pd.read_csv(file3)

#Clean the transaction report
#Delete the first 9 rows and the last one 
transaction_report1 = transaction_report1[9:-1]

#Label the column names based on the values in the the 9th rows
transaction_report1.columns = transaction_report1.iloc[0]
transaction_report1 = transaction_report1.drop(transaction_report1.index[0])
transaction_report1 = transaction_report1.reset_index(drop = True)
transaction_report1['Flipt Person ID'] = pd.to_numeric(transaction_report1['Flipt Person ID'])

#Clean the flipt_adoption_report
flipt_adoption_report.columns = flipt_adoption_report.iloc[0]
flipt_adoption_report = flipt_adoption_report.drop(flipt_adoption_report.index[0])
flipt_adoption_report['Flipt Person ID'] = flipt_adoption_report['flipt person ID']
flipt_adoption_report['Flipt Person ID'] = pd.to_numeric(flipt_adoption_report['Flipt Person ID'])
flipt_adoption_report = flipt_adoption_report.reset_index()


#Create all of the additional columns we are going to need to have in the report
transaction_report1['Gender'] = ''
transaction_report1['Date of Birth'] = ''
transaction_report1['Age'] = ''
transaction_report1['Salary'] = ''
transaction_report1['Home Location'] = ''     
transaction_report1['Frequent Pharmacy'] = ''
transaction_report1['Distance between Pharmacy and Home'] = ''




def apply_demographics(dataset_main, dataset_origin, column_name_origin, column_name_new):
    #Create the new column
    dataset_main[column_name_new] = ''
    demographic_dict = {}
    for i in dataset_origin.index: 
       key = dataset_origin['Flipt Person ID'].iloc[i]
       value = dataset_origin[column_name_origin].iloc[i]
       demographic_dict[key] = value
    for i in range(0, len(dataset_main)):
        id_number = dataset_main['Flipt Person ID'].iloc[i]
        if id_number in list(demographic_dict.keys()):
            dataset_main[column_name_new].iloc[i] = demographic_dict[id_number] 
        else:
            dataset_main[column_name_new].iloc[i] = np.nan
        
#Gender: column_name_origin = 'Gender', column_name_new = 'Gender'
apply_demographics(transaction_report1, registered_users_report, 'Gender', 'Gender')

#Date of Birth: column_name_origin = 'Date of Birth', column_name_new = 'Date of Birth
apply_demographics(transaction_report1, registered_users_report, 'Date of Birth', 'Date of Birth')
#Add additional code to convert birthday into age
transaction_report1['Date of Birth'] = pd.to_datetime(transaction_report1['Date of Birth'])
def age(i):
    birth_date = (pd.to_datetime(transaction_report1['Date of Birth'].iloc[i])).date()
    today_date = dt.date.today()
    years = ((today_date-birth_date).days/365)
    transaction_report1['Age'].iloc[i] = years
    return years        

for i in range(0, len(transaction_report1)):
    age(i)
transaction_report1['Age'] = transaction_report1['Age'].astype(int)

  
#Salary
apply_demographics(transaction_report1, flipt_adoption_report, 'salary', 'Salary')
    

def strip_comma(x):
    if type(x) == str:
        num = x.replace(',', '')
        return float(num)
    else:
        return x
    
transaction_report1['Salary'] = transaction_report1['Salary'].apply(strip_comma)
#Change all values to integers and ignore the values that are not numbers 
transaction_report1['Salary'] = transaction_report1['Salary'].astype(int, errors = 'ignore') 

#Create a column for the conglomerated home address so that we can use the apply_demographics function
registered_users_report['Home Address'] = ''
registered_users_report = registered_users_report[registered_users_report['Home Address1'].notnull()]
for i in registered_users_report.index: 
    registered_users_report['Home Address'][i] = registered_users_report['Home Address1'][i] + " " + registered_users_report['City'][i] + " " + registered_users_report['State'][i]

registered_users_report_address = registered_users_report[['Flipt Person ID', 'First Name', 'Last Name', 'Home Address1',
                   'Home Address2', 'City', 'State', 'Zip', 'Employee_ID']]
address_dict = {}
registered_users_report_address = registered_users_report_address.set_index('Flipt Person ID')
for i in registered_users_report_address.index:
    address_string = registered_users_report_address['Home Address1'][i] + " " + registered_users_report_address['City'][i] + " " + registered_users_report_address['State'][i]
    address_dict[i] = address_string

for i in range(0, len(transaction_report1)):
    id_number = transaction_report1['Flipt Person ID'].iloc[i]
    if id_number in list(address_dict.keys()):
        transaction_report1['Home Location'].iloc[i] = address_dict[id_number] 
    else:
        transaction_report1['Home Location'].iloc[i] = np.nan
        
registered_users_report_address = registered_users_report_address.reset_index()
#Set the frequent pharmacy address
frequent_pharm_dict = {}
for i in range(0, len(transaction_report1)):
    id_number = transaction_report1['Flipt Person ID'].iloc[i]
    dataframe = transaction_report1[transaction_report1['Flipt Person ID'] == id_number]
    frequent = pd.DataFrame(dataframe['Location'].value_counts())
    if frequent.shape[0] != 1:
        frequent_pharm_dict[id_number] = frequent.index[0]
    else: 
        frequent_pharm_dict[id_number] = np.nan
        
for i in range(0, len(transaction_report1)):
    id_number = transaction_report1['Flipt Person ID'].iloc[i]
    if id_number in list(frequent_pharm_dict.keys()):
        transaction_report1['Frequent Pharmacy'].iloc[i] = frequent_pharm_dict[id_number] 
    else:
        transaction_report1['Frequent Pharmacy'].iloc[i] = np.nan
        
#Calculate distance between pharmacy and home 
api_key_value = 

def location_between(index_number):
    origin = transaction_report1['Home Location'][index_number].replace(' ', '+')
    destination = transaction_report1['Location'][index_number].replace(',', '').replace(' ', '+')
    api_key = api_key_value
    endpoint = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&'
    nav_request = 'origins={}&destinations={}&key={}'.format(origin, destination, api_key)
    url_needed = endpoint + nav_request
    response = requests.urlopen(url_needed).read()
    result = json.loads(response)
    distance = result['rows'][0]['elements'][0]['distance']['text']
    transaction_report1['Distance between Pharmacy and Home'][index_number] = distance
    return distance 
    
for i in range(0, len(transaction_report1)):
    id_number = transaction_report1['Flipt Person ID'].iloc[i]
    location_between(i)
    
transaction_report1['Distance between Pharmacy and Home']
    
#Extract the numeric value from the distance 
patterns = re.compile('\d*\.\d*')    
transaction_report1['Distance between Pharmacy and Home'] = transaction_report1['Distance between Pharmacy and Home'].apply(lambda x: re.findall(patterns, str(x)))

for i in range(0, len(transaction_report1)):
    if transaction_report1['Distance between Pharmacy and Home'][i] != []:
        value = transaction_report1['Distance between Pharmacy and Home'].iloc[i][0]
        transaction_report1['Distance between Pharmacy and Home'].iloc[i] = value
    else: 
        transaction_report1['Distance between Pharmacy and Home'][i] = 0

del transaction_report1['Date of Birth']

transaction_report1.to_csv('transaction_report_demographics_' + str(dt.date.today()) +'.csv')

        
        

