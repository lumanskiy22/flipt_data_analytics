#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 14:02:42 2018

@author: lumanskiy
"""

#This will be a clean and easy-to-understand 'repeat_users' file 

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 15:50:49 2018

@author: lumanskiy
"""
#First, set up packages and working directory as needed 
import os
import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
import matplotlib.pyplot as plt

os.getcwd()
os.chdir('/Users/lumanskiy/Desktop/FliptFiles')

#Import and clean the data that will be used
transaction_report = pd.read_csv('transaction_report_demographics_2018-07-13.csv')
transaction_report['Number of Drugs Ordered'] = 0 
transaction_report['Ordered Multiple Drugs'] = 0
del transaction_report['Unnamed: 0']       

#Separate only into 'filled' prescriptions 
transaction_report_filled = transaction_report[transaction_report['Rx Status'] == 'Filled']

#Group by people who have filled more than drug
drug_count = pd.DataFrame(transaction_report_filled.groupby('Flipt Person ID')['GPI Code'].count())
ordered_more_than_one = drug_count[drug_count['GPI Code'] != 1]
ids = ordered_more_than_one.index.tolist()
num_drugs_order = ordered_more_than_one['GPI Code'].tolist()

#Create dictionary that stores the number of times every Flipt ID has ordered a 
#prescription drug 
num_drugs_ordered = {}
for i in range(1, len(ids)):
    id_value = ids[i]
    num_drugs_ordered[id_value] = num_drugs_order[i]
    
for i in transaction_report.index:
    if transaction_report['Flipt Person ID'].iloc[i] in num_drugs_ordered:
        id_value = transaction_report['Flipt Person ID'].iloc[i]
        transaction_report['Number of Drugs Ordered'].iloc[i] = num_drugs_ordered[id_value] 
    else:
        transaction_report['Number of Drugs Ordered'].iloc[i] = 1
    if transaction_report['Number of Drugs Ordered'].iloc[i] != 1:
        transaction_report['Ordered Multiple Drugs'].iloc[i] = 'TRUE'
    else: 
        transaction_report['Ordered Multiple Drugs'].iloc[i] = 'FALSE'

transaction_report_multiple = transaction_report_filled[transaction_report_filled['Ordered Multiple Drugs'] == 'TRUE']

#The transaction_report_multiple data subset represents all of the people who have purchase 
#more than one drug more than once 

#For each Flipt Person ID, lets get rid of the drugs that we only ordered once

#Now, lets sort out from the original dataframe the people and the drugs
#that we have stored in the multiple_drugs dataset
drugs_ordered_multiple_times = list(set(list(transaction_report['GPI Code'])))
transaction_report_ids = transaction_report[transaction_report['Flipt Person ID'].isin(ids)]

        
#Now, I want to see the number of people who went to the same pharmacy 
#For the same drug
unique_location = pd.DataFrame(transaction_report_multiple.groupby(['Flipt Person ID', 'GPI Code'])['Location'].nunique())

unique_location_dict = {}
for i in range(0,len(unique_location.index)):
    unique_location_dict[unique_location.index[i]] = unique_location['Location'][i]
        
transaction_report_multiple = transaction_report_multiple.set_index(['Flipt Person ID', 'GPI Code'])

transaction_report_multiple['Switch Pharmacy'] = ''

for i in transaction_report_multiple.index:
    if unique_location_dict[i] == 1:
        transaction_report_multiple['Switch Pharmacy'][i] = "FALSE"
    else:
        transaction_report_multiple['Switch Pharmacy'][i] = "TRUE"


transaction_report_slim = transaction_report_multiple[transaction_report_multiple['Switch Pharmacy'] == 'TRUE']
transaction_report_slim['Used Same Pharmacy'] = ''
transaction_report_slim = transaction_report_slim.set_index(['Flipt Person ID', 'GPI Code'])

for b in range(0, len(transaction_report_slim.index)):
    a = transaction_report_slim.index[b]
    df = pd.DataFrame(transaction_report_slim.loc[a])
    for i in range(1,len(df)):
        if df.iloc[i]['Location'] == df.iloc[i-1]['Location']:
            transaction_report_slim['Used Same Pharmacy'].loc[a] = 'TRUE'
        else:
            transaction_report_slim['Used Same Pharmacy'].loc[a] = 'FALSE'
        
#Finally, filter people out who switched pharmacies for the same drug 
transaction_report_same_drug_diff_pharm = transaction_report_slim[transaction_report_slim['Used Same Pharmacy'] != 'TRUE']

#The next project will be to find the difference between the prices each time the person
#Goes to the pharmacy to get the same prescription 

transaction_report_same_drug_diff_pharm = transaction_report_same_drug_diff_pharm.set_index(['Flipt Person ID', 'GPI Code'])

##The goal is to create two lists: one which has the differences between the distances
## and the other one is one that has the differences in prices
unique_indexes = list(set(list(transaction_report_same_drug_diff_pharm.index)))

prices = []
distances = []
gender = []
for i in unique_indexes:
    df = pd.DataFrame(transaction_report_same_drug_diff_pharm.loc[i])
    for p in range(1, len(df)):
        price_diff = df['Net OPC'][p] - df['Net OPC'][p-1] 
        prices.append(price_diff)
        distance_diff = df['Distance between Pharmacy and Home'][p] - df['Distance between Pharmacy and Home'][p-1] 
        distances.append(distance_diff)
        gender.append(df['Gender'][p])

df_switch = pd.DataFrame({'prices':prices, 'distances':distances, 'gender':gender})

sns.set()
sns.lmplot(x = 'distances', y = 'prices', hue = 'gender', data = df_switch, fit_reg = False)
plt.xlabel('Differences of distance between recent and past purchase')
plt.ylabel('Price differences' )
plt.title('Trends in switching pharmacy for same drug purchase')
plt.annotate('Count: ' + str(len(prices)), xy = (df_switch['distances'].max()-0.5,df_switch['prices'].max()))
plt.savefig('trends_in_switching_pharmacy_for_same_drug_purchase_gpi_' + str(dt.date.today()) + '.png')


#Now, I want to create a graph to see when people are switching and when people are not
index_list = list(set(list(transaction_report_multiple.index)))

price_1 = []
price_2 = []
gender = []
age = []
switch = []
for i in index_list: 
    df = pd.DataFrame(transaction_report_multiple.loc[i])
    for p in range(1, len(df)):
        price1 = df['Net OPC'][p-1]
        price_1.append(price1)
        price2 = df['Net OPC'][p]
        price_2.append(price2)
        gender.append(df['Gender'][p])  
        age.append(df['Age'][p])  
        switch.append(df['Switch Pharmacy'][p])

price_switch_df = pd.DataFrame({'price_1':price_1, 'price_2':price_2, 'gender': gender, 'Pharmacy Pattern': switch})

def recode(x):
    if x == 'TRUE':
        x = x.replace('TRUE','Switched')
        return x
    else:
        x = x.replace('FALSE', 'Did not switch')
        return x 
price_switch_df['Pharmacy Pattern'] = price_switch_df['Pharmacy Pattern'].apply(recode)
    
sns.lmplot(x = 'price_1', y = 'price_2', data = price_switch_df, fit_reg = False, hue = 'Pharmacy Pattern',markers = ['o','x'])
plt.plot([o for o in range(-75,75)], [p for p in range(-75,75)])
plt.ylim(-75, 75)
plt.xlim(-75, 75)
plt.xlabel('Net OPC 1st purchase')
plt.ylabel('Net OPC 2nd purchase')
plt.annotate('Count: ' + str(len(price_switch_df)), xy = (40, 70))
plt.title('Trends in purchasing the same prescription drug')
plt.savefig('Pharmacy patterns in purchasing same drug_gpi' + str(dt.date.today()) +'.png')
  
#Now, I want to create a graph to see when people are switching and when people are not
#based on pharmacy distances 
transaction_report_multiple = transaction_report_multiple.set_index(['Flipt Person ID', 'GPI Code'])
index_list = list(set(list(transaction_report_multiple.index)))


distance_1 = []
distance_2 = []
gender_dist = []
switch_dist = []
for i in index_list: 
    df = pd.DataFrame(transaction_report_multiple.loc[i])
    for p in range(1, len(df)):
        distance1 = df['Distance between Pharmacy and Home'][p-1]
        distance_1.append(distance1)
        distance2 = df['Distance between Pharmacy and Home'][p]
        distance_2.append(distance2)
        gender_dist.append(df['Gender'][p])  
        switch_dist.append(df['Switch Pharmacy'][p])

distance_switch_df = pd.DataFrame({'distance_1':distance_1, 'distance_2':distance_2, 'gender': gender_dist, 'Pharmacy Pattern': switch_dist})

def recode(x):
    if x == 'TRUE':
        x = x.replace('TRUE','Did not switch')
        return x
    else:
        x = x.replace('FALSE', 'Switched')
        return x 
distance_switch_df['Pharmacy Pattern'] = distance_switch_df['Pharmacy Pattern'].apply(recode)


sns.lmplot(x = 'distance_1', y = 'distance_2', data = distance_switch_df, fit_reg = False, hue = 'Pharmacy Pattern', markers = ['o','x'])
plt.plot([o for o in range(-75,75)], [p for p in range(-75,75)])
plt.ylim(0, 10)
plt.xlim(0, 10)
plt.xlabel('Distance 1st purchase')
plt.ylabel('Distance 2nd purchase')
plt.annotate('Count: ' + str(len(distance_switch_df)), xy = (0, 9.7))
plt.title('Pharmacy switching patterns')
plt.savefig('Pharmacy switching patterns'+ str(dt.date.today())+'.png')

