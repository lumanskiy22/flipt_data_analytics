#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 09:31:01 2018

@author: lumanskiy
"""

##The goal of this script is to work on understanding whether or not 
## people are making their choices based on cheapest price or closest distance

import os 
os.getcwd()
os.chdir('/Users/lumanskiy/Desktop/FliptFiles')

import pandas as pd
import numpy as np
sorted_df = pd.read_csv('search_report_sorted_by_analytics_id_for_exploration.csv')
sorted_df = sorted_df.dropna(how = 'all', axis = 1)

sorted_routed = sorted_df[sorted_df['route_id'].notnull()]

analytics_ids = sorted_routed['user_identification_id'].tolist()

sorted_for_analysis = sorted_df[sorted_df['user_identification_id'].isin(analytics_ids)]
sorted_for_analysis.head()

#Cut down the dataframe for only columns that we will need 
pharmacy = []
for i in range(1,11):
    pharmacy.append('pharmacy_' + str(i) + '_opc')
    pharmacy.append('pharmacy_' + str(i) + '_rewards')
    pharmacy.append('pharmacy_distance' + str(i)) 
pharmacy
columns_list = ['timestamp', 'user_identification_id', 'route_id']    
for i in columns_list:
    pharmacy.append(i)

df = sorted_for_analysis[pharmacy]

pharmacy_analysis_dict = {}
distance_analysis_dict = {}
#We want to create a new dataframe for all of the pharmacy options 
    
def extracting_important_info(p):
    possible_values_prescription = []
    possible_values_pharmacy = []
    possible_values_distance = []
    working_df = df[df['user_identification_id'] == p]
    working_df = working_df.sort_values('timestamp', ascending = True)
    working_df = working_df.reset_index()
    working_df = working_df.fillna(0)
            #Modify the dataframe so that the last action is routing the prescription
    for m in range(0, len(working_df)):
        if working_df['route_id'].iloc[m] != 0:
            possible_values_prescription.append(m) 
    new_index = (np.array(possible_values_prescription)).min() + 1 
    new_working_df = working_df[:new_index]
    key1 = new_working_df['route_id'].iloc[-1]        
    
    new_working_df = new_working_df.reset_index()
    for m in range(0, len(new_working_df)):
        if new_working_df['pharmacy_1_opc'].iloc[m] != 0:
            possible_values_pharmacy.append(m) 
        if possible_values_pharmacy != [] :
            pharm_index = (np.array(possible_values_pharmacy).max())
            value = new_working_df.iloc[pharm_index]
            pharmacy_analysis_dict[key1] = value
        else:
            pharmacy_analysis_dict[key1] = 'nan'
            


    for m in range(0, len(new_working_df)):
        if new_working_df['pharmacy_distance1'].iloc[m] != 0:
            possible_values_distance.append(m)
        if possible_values_distance != []:
            distance_index = (np.array(possible_values_distance).max())
            value2 = new_working_df.iloc[distance_index]
            distance_analysis_dict[key1] = value2
        else:
            distance_analysis_dict[key1] = 'nan'
            
    return pharmacy_analysis_dict
    return distance_analysis_dict
    
pharmacy_info = pd.DataFrame(pharmacy_analysis_dict)
pharmacy_info.to_csv('pharmacy_info_for_prescriptions.csv')


column_names = pharmacy_info.index.tolist()

distance_info = pd.DataFrame(distance_analysis_dict)

distance_info.to_csv('distance_info_for_prescriptions.csv')
distance_info.head()

distance_info = pd.read_csv('distance_info_for_prescriptions.csv')
distance_info = distance_info.transpose()

pharmacy_info = pd.read_csv('pharmacy_info_for_prescriptions.csv')
pharmacy_info = pharmacy_info.transpose()
for p in analytics_ids:
    extracting_important_info(p)
    
    
#Subset only the parts of the dataframes that are relevant 
relevant_pharmacy = []
for i in range(1,11):
    relevant_pharmacy.append('pharmacy_' + str(i) + '_opc'),
    relevant_pharmacy.append('pharmacy_' + str(i) + '_rewards'),

relevant_distance = []
for i in range(1,11):
    relevant_distance.append('pharmacy_distance' + str(i))


pharmacy_info.columns = pharmacy_info.loc['Unnamed: 0']
distance_info.columns = distance_info.iloc[0]


pharmacy_info_relevant = pharmacy_info[relevant_pharmacy]   
distance_info_relevant = distance_info[relevant_distance]
    
prescription_choices  = pd.concat([pharmacy_info_relevant, distance_info_relevant], axis = 1 )

transaction_report = pd.read_csv('transaction_report_demographics_2018-07-13.csv')    
transaction_report.columns
transaction_report_relevant = transaction_report[['RX Number', 'Flipt Person ID',                                                  
                                            'Rx Status', 'Employee opc', 'Rewards', 'Net OPC',
                                            'Distance between Pharmacy and Home']]

prescription_choices = prescription_choices.reset_index()

all_choices = pd.merge(left = prescription_choices, right = transaction_report_relevant, on = None, left_on = 'index',
         right_on = 'RX Number')

for b in range(1,11):
    column_name = 'pharmacy_' + str(b) + '_opc'
    all_choices[column_name] = pd.to_numeric(all_choices[column_name])
    column_name2 = 'pharmacy_' + str(b) + '_rewards'
    all_choices[column_name2] = pd.to_numeric(all_choices[column_name2])
    column_name3 = 'pharmacy_distance' + str(b)
    all_choices[column_name3] = pd.to_numeric(all_choices[column_name3], errors = 'coerce')

all_choices.info()
all_choices.to_csv('prescription_choice_information.csv')
#****************************#
#   We need to compute the net opc for all of the options 
all_choices.columns
#*****************************

#First, create new columns for all of chice
for i in range(1, 11): 
    new_column_name = 'choice_' + str(i) + '_net_opc'
    all_choices[new_column_name] = ''
    

#Subtract the values from one another and put computed values into a new column
for i in range(1, 11):    
    opc_column = 'pharmacy_' + str(i) + '_opc'
    rewards_column = 'pharmacy_' + str(i) + '_rewards'
    net_opc_column = 'choice_' + str(i) + '_net_opc'
    for m in range(0,len(all_choices)):
        all_choices[net_opc_column].iloc[m] = all_choices[opc_column].iloc[m] - all_choices[rewards_column].iloc[m]
        
#Identify the cheapest option 
all_choices['cheapest option'] = 0

for i in range(1,11):
    net_opc_column = 'choice_' + str(i) + '_net_opc'
    all_options = []
    for b in range(0,len(all_choices)): 
        
        all_options.append(all_choices[net_opc_column].iloc[b])
    

for b in range(0,len(all_choices)): 
    all_options = []
    for i in range(1,11): 
        net_opc_column = 'choice_' + str(i) + '_net_opc'
        all_options.append(all_choices[net_opc_column].iloc[b])
    all_negative = 0 
    for p in all_options:
        if p > 0:
            all_negative += 1 
    if all_negative == 0:
        lowest_price = np.array(all_options).max()
        all_choices['cheapest option'].iloc[b] = lowest_price
    else:
        lowest_price = np.array(all_options).min()
        all_choices['cheapest option'].iloc[b] = lowest_price

#Did people pick the cheapest option? 
all_choices['Chose cheapest option'] = ''

for b in range(0, len(all_choices)):
    cheapest_option = all_choices['cheapest option'].iloc[b]
    chosen_option = all_choices['Net OPC'].iloc[b]
    if round(cheapest_option, 2) == chosen_option:
        all_choices['Chose cheapest option'].iloc[b] = 'TRUE'
    else:
        all_choices['Chose cheapest option'].iloc[b] = 'FALSE'
        
all_choices['Difference between cheapest and chosen'] = ''
#I'm going to code all of those whose difference was less than $.50 as TRUE 
for b in range(0, len(all_choices)):
    cheapest_option = all_choices['cheapest option'].iloc[b]
    chosen_option = all_choices['Net OPC'].iloc[b]
    difference = chosen_option - cheapest_option
    if abs(difference) <= 1:
        all_choices['Chose cheapest option'].iloc[b] = 'TRUE'
    all_choices['Difference between cheapest and chosen'].iloc[b] = difference 
        
all_choices.groupby('Chose cheapest option')['RX Number'].count()
        
net_opcs = all_choices[['Net OPC', 'cheapest option']]


not_cheapest = all_choices[all_choices['Chose cheapest option'] == 'FALSE']

not_cheapest['Difference between cheapest and chosen'].min()





















