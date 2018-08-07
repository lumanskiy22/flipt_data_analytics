#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 10:20:29 2018

@author: lumanskiy
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 12:33:57 2018

@author: lumanskiy
"""
#the goal of this script is to extract meaningful information from the
#search report
#at the bottom, I construct boxplots for the number of searches vs search number
import os
import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
import matplotlib.pyplot as plt


os.getcwd()
os.chdir('/Users/lumanskiy/Desktop/FliptFiles')

#Import all data you will need  
search = pd.read_csv('SearchPrescription08072018.csv', encoding = 'latin')
transaction_report = pd.read_csv('transaction_report_demographics_2018-08-01.csv')
data = pd.ExcelFile("EEID Crosswalk.xlsx")
df_cross = data.parse('Flipt ID Crosswalk with EEID')


search = search.dropna(how = 'all', axis = 1)
search_id = search[search['user_identification_id'].notnull()]

action_count = pd.DataFrame(search_id.groupby('user_identification_id')['timestamp'].count())

#Extract interactions that have more than one action 
multiple_action = action_count[action_count['timestamp'] != 1]
multiple_action_list = multiple_action.index.tolist()
multiple_action_df = search_id[search_id['user_identification_id'].isin(multiple_action_list)]
multiple_action_df['timestamp'] = pd.to_datetime(multiple_action_df['timestamp'])
multiple_action_df['date'] = multiple_action_df['timestamp'].dt.date
multiple_action_df['date'] = multiple_action_df['date'].astype(str)


#Extract the analytics IDs that have a Route ID associated with them 
multiple_action_prescription = multiple_action_df[multiple_action_df['route_id'].notnull()]
ids_for_routed_prescriptions = list(set(multiple_action_prescription['user_identification_id'].tolist()))

 
#Create an emply data frame with user_identification_IDs as the index as the following columns
columns = ['route_id', 'flipt_person_id', 'search_time_length', '# actions prior to routing', '# app uses prior to routing','# of actions historically prior to routing', 'contact with concierge']
df = pd.DataFrame(index=ids_for_routed_prescriptions, columns=columns)
df = df.fillna(0)

#Set dataframe that only has the user_identification_ids found in the ids of routed prescriptiosn         
sessions_with_routed_prescriptions = multiple_action_df[multiple_action_df['user_identification_id'].isin(ids_for_routed_prescriptions)]
ids_for_routed_prescriptions = list(set(multiple_action_prescription['user_identification_id'].tolist()))


#Find the Flipt Person ID associated with the routed prescription  
flipt_person_ids = {}
for i in ids_for_routed_prescriptions:
    df_one = pd.DataFrame(sessions_with_routed_prescriptions[sessions_with_routed_prescriptions['user_identification_id'] == i])
    #Order each dataframe so that they are in ascending order by time 
    df_one = df_one.sort_values('timestamp', ascending = True)
    #Fill all of the columns so they are associated with the same flipt iD 
    df_one['flipt_person_id'] = df_one['flipt_person_id'].fillna(method = 'bfill')
    df_one['flipt_person_id'] = df_one['flipt_person_id'].fillna(method = 'ffill')
    flipt_id = df_one['flipt_person_id'].iloc[0]
    if str(df_one['flipt_person_id'].iloc[0])[1] == 'a':
        flipt_person_ids[i] = 0
    else: 
        flipt_person_ids[i] = df_one['flipt_person_id'].iloc[0]


#Find the search length of the interaction
search_length = {}
for i in ids_for_routed_prescriptions:
    df_one = pd.DataFrame(sessions_with_routed_prescriptions[sessions_with_routed_prescriptions['user_identification_id'] == i])
    df_one = df_one.sort_values('timestamp', ascending = True)
    #Modify the dataframe so that the last action is routing the prescription
    for m in range(0, len(df_one)):
        if type(df_one['route_id'].iloc[m]) == str:
            #Check to see if this is the last value
            new_df_one = df_one[:m]                
        #Find the time difference between the start and end 
        new_df_one['timestamp'] = pd.to_datetime(new_df_one['timestamp'])
        if len(new_df_one) > 1 :
            search_time = (((new_df_one['timestamp'].iloc[-1] - new_df_one['timestamp'].iloc[0]).seconds)/60)
            search_length[i] = search_time
    
#Figure out how many actions a person took prior to routing
num_actions_prior_to_route = {}
for i in ids_for_routed_prescriptions:
    df_one = pd.DataFrame(sessions_with_routed_prescriptions[sessions_with_routed_prescriptions['user_identification_id'] == i])
    df_one = df_one.sort_values('timestamp', ascending = True)
    #Modify the dataframe so that the last action is routing the prescription
    for m in range(0, len(df_one)):
        if type(df_one['route_id'].iloc[m]) == str:
            #Check to see if this is the last value
            new_df_one = df_one[:m]        
    num_actions_prior_to_route[i] = len(new_df_one)
    
#Number of searches prior to this one 
unique_user_id_routed = list(set(sessions_with_routed_prescriptions['user_identification_id'].tolist()))

routed_prescrips_dict = {}
for i in unique_user_id_routed:
    df_one = pd.DataFrame(sessions_with_routed_prescriptions[sessions_with_routed_prescriptions['user_identification_id'] == i])
    df_one = df_one.sort_values('timestamp', ascending = True)    
    df_one['prescription_1_id'] = df_one['prescription_1_id'].fillna(method = 'bfill')
    df_one['prescription_1_id'] = df_one['prescription_1_id'].fillna(method = 'ffill')
    name = df_one['prescription_1_id'].iloc[0] 
    time = df_one['timestamp'].iloc[0]
    if name in routed_prescrips_dict.keys():
        routed_prescrips_dict[name].append({i:time})
    else:
        routed_prescrips_dict[name] = [{i:time}]

unique_user_id_all = list(set(multiple_action_df['user_identification_id'].tolist()))
all_prescrips_dict = {}
for i in unique_user_id_all:
    df_one = pd.DataFrame(multiple_action_df[multiple_action_df['user_identification_id'] == i])
    df_one = df_one.sort_values('timestamp', ascending = True)    
    df_one['prescription_1_id'] = df_one['prescription_1_id'].fillna(method = 'bfill')
    df_one['prescription_1_id'] = df_one['prescription_1_id'].fillna(method = 'ffill')
    df_one['flipt_person_id'] = df_one['flipt_person_id'].fillna(method = 'bfill')
    df_one['flipt_person_id'] = df_one['flipt_person_id'].fillna(method = 'ffill')
    flipt_id = df_one['flipt_person_id'].iloc[0]
    name = df_one['prescription_1_id'].iloc[0] 
    time = df_one['timestamp'].iloc[0]
    if str(name) == 'nan':
        if flipt_id in all_prescrips_dict.keys():
            all_prescrips_dict[flipt_id].append({i:time})
        else:
            all_prescrips_dict[flipt_id] = [{i:time}]
    else:
        if name in all_prescrips_dict.keys():
            all_prescrips_dict[name].append({i:time})
        else:
            all_prescrips_dict[name] = [{i:time}]


#Now, I'm going to adjust the information based on the Crosswalk file, so I have more information             
data = pd.ExcelFile("EEID Crosswalk.xlsx")
df_cross = data.parse('Flipt ID Crosswalk with EEID')
#Create a new dictionary. First, I must concatenate everyone's name
name_id = {}
for i in range(0, len(df_cross)):
    first_name = df_cross['First Name'].iloc[i]
    last_name = df_cross['Last Name'].iloc[i]
    full_name = str(first_name) + ' ' + str(last_name)
    flipt_person_id = df_cross['Flipt Person ID'].iloc[i]
    name_id[flipt_person_id] = full_name
    
for i in list(all_prescrips_dict.keys()):
    if type(i) == np.float64 and str(i) != 'nan':
        name = name_id[i]
        all_prescrips_dict[name] = all_prescrips_dict.pop(i)
        
            
#The goal, now, is to count how many analytics IDs are in all_prescrips_dict
searches_prior = {}
for i in routed_prescrips_dict:   
    length = len(routed_prescrips_dict[i])
    if length > 1:
        for m in range(1,len(routed_prescrips_dict[i])):
            #I need to sort the values 
            date_1 = str(list(routed_prescrips_dict[i][m].values()))
            date_2 = str(list(routed_prescrips_dict[i][m-1].values()))
            #Then, I need to create a list of all of the possible analytics ids from that person
            searches_in_between = []
            analytics_ids_key = str(list(routed_prescrips_dict[i][m].keys())[0])
            search_prior = 0
            values = all_prescrips_dict[i] 
            for p in range(0, len(values)):
                searches_in_between.append(list(values[p].values()))
            for n in searches_in_between: 
                if str(n) <= date_1 and str(n) >= date_2:
                    search_prior += 1
            searches_prior[analytics_ids_key] = search_prior
    else:
        searches_in_between = []
        search_prior = 0
        values = all_prescrips_dict[i] 
        for m in range(1,len(routed_prescrips_dict[i])):
            #I need to sort the values 
            analytics_ids_key = str(list(routed_prescrips_dict[i][m].keys())[0])
            date_1 = str(list(routed_prescrips_dict[i][m].values()))
            date_2 = str(list(routed_prescrips_dict[i][m-1].values()))
        for p in range(0, len(values)):
            searches_in_between.append(list(values[p].values()))
        for n in searches_in_between: 
            if str(n) <= date_1 and str(n) >= date_2:
                    search_prior += 1
        searches_prior[analytics_ids_key] = search_prior
        
    
#Number of actions prior (historically)
num_searches_prior  = {}
for i in ids_for_routed_prescriptions:
    df_one = pd.DataFrame(sessions_with_routed_prescriptions[sessions_with_routed_prescriptions['user_identification_id'] == i])
    df_one = df_one.sort_values('timestamp', ascending = True)
    df_one['prescription_1_id'] = df_one['prescription_1_id'].fillna(method = 'bfill')
    df_one['prescription_1_id'] = df_one['prescription_1_id'].fillna(method = 'ffill')
    name = df_one['prescription_1_id'].iloc[0]    
    date = str(df_one['timestamp'].dt.date.iloc[0])
    see_what_else = multiple_action_df[(multiple_action_df['prescription_1_id'] == name) & 
                                   (multiple_action_df['date'] < date)]
    num_searches_prior[i] = see_what_else['user_identification_id'].nunique()
    
#Contact with concierge 
concierge_interaction = {}
for i in ids_for_routed_prescriptions:
    df_one = pd.DataFrame(sessions_with_routed_prescriptions[sessions_with_routed_prescriptions['user_identification_id'] == i])
    action = df_one['action'].notnull().any()
    concierge_interaction[i] = action
    
#Route ID Dictionary 
route_id_dict = {}

for i in ids_for_routed_prescriptions:
    df_one = pd.DataFrame(sessions_with_routed_prescriptions[sessions_with_routed_prescriptions['user_identification_id'] == i])
    df_one = df_one.sort_values('timestamp', ascending = True)
    #Modify the dataframe so that the last action is routing the prescription
    try:
        for m in range(0, len(df_one)):
            if type(df_one['route_id'].iloc[m]) == str:
            #Check to see if this is the last value
                new_df_one = df_one[:m]
                new_df_one['route_id'] = new_df_one['route_id'].fillna(method = 'bfill')
                new_df_one['route_id'] = new_df_one['route_id'].fillna(method = 'ffill')
                route_id_dict[i] = new_df_one['route_id'].iloc[0]
            else:
                df_one['route_id'] = df_one['route_id'].fillna(method = 'bfill')
                df_one['route_id'] = df_one['route_id'].fillna(method = 'ffill')
                route_id_dict[i] = df_one['route_id'].iloc[0]
    except IndexError:
        print("There was a problem with " + str(i))



#Add all of this information to the dataset 

for i in range(0, len(df)):
    key = df['index'].iloc[i]
    if key in flipt_person_ids.keys():
        value = flipt_person_ids[key]
        df['flipt_person_id'].iloc[i] = value 
    else: 
        df['flipt_person_id'].iloc[i] = np.nan
    if key in search_length.keys():
        search_value = search_length[key]
        df['search_time_length'].iloc[i] = search_value
    else:
        df['search_time_length'].iloc[i] = np.nan
    if key in num_actions_prior_to_route.keys():    
        action_value = num_actions_prior_to_route[key]
        df['# actions prior to routing'].iloc[i] = action_value
    else:
        df['# actions prior to routing'].iloc[i] = np.nan
    if key in searches_prior.keys():   
        searches_prior_value = searches_prior[str(key)]
        df['# app uses prior to routing'].iloc[i] = searches_prior_value
    else:
        df['# app uses prior to routing'].iloc[i] = np.nan
    if key in num_searches_prior.keys():
        num_search_value = num_searches_prior[key]
        df['# of actions historically prior to routing'].iloc[i] = num_search_value
    else:
        df['# of actions historically prior to routing'].iloc[i] = np.nan
    if key in concierge_interaction.keys():
        conceirge_interaction = concierge_interaction[key]
        df['contact with concierge'].iloc[i] = conceirge_interaction
    else:
        df['contact with concierge'].iloc[i] = np.nan
    if key in route_id_dict.keys():
        route_id = route_id_dict[key]
        df['route_id'].iloc[i] = route_id
    else:
        df['route_id'].iloc[i] = np.nan
        
for i in range(0, len(df)):
    key = df['index'].iloc[i]
    if key in searches_prior.keys():   
        searches_prior_value = searches_prior[str(key)]
        df['# app uses prior to routing'].iloc[i] = searches_prior_value
    else:
        df['# app uses prior to routing'].iloc[i] = np.nan

df_new = df.reset_index()
df.to_csv('search_report_extract_' + str(dt.date.today()) + '.csv')    

#Work with transaction report to yield only 
transaction_report = pd.read_csv('transaction_report_demographics_2018-08-01.csv')

transaction_report['Routed Date'] = pd.to_datetime(transaction_report['Routed Date'])
transaction_report['Date'] = transaction_report['Routed Date'].dt.date
transaction_report_filled = transaction_report[transaction_report['Rx Status'] == 'Filled']
transaction_report_small = transaction_report_filled[['RX Number', 'Flipt Person ID', 'Rx Status', 'Date', 'Age', 'Gender', 'Salary']]
df = df.reset_index()

extract = pd.merge(left = df_new, right = transaction_report_small, on = None, left_on = 'route_id', right_on = 'RX Number' )
extract_filled = extract[extract['Rx Status'] == 'Filled']
extract_filled = extract_filled[extract_filled['search_time_length'] != 0]


extract_filled.to_csv('search_report_extract_filled_' + str(dt.date.today()) + '.csv')    


#Extract the Flipt IDs of this list
extract_filled['search_number'] = '' 
unique_ids = list(set(extract_filled['Flipt Person ID'].tolist()))

search_number_dict = {}
for i in unique_ids:
    dd = pd.DataFrame(extract_filled[extract_filled['Flipt Person ID'] == i])
    dd = dd.sort_values('RX Number', ascending = True)
    for count, value in enumerate(dd['RX Number']):
        search_number_dict[value] = (count+1)
        

extract_filled_1 = extract_filled.reset_index(drop = True)
for i in extract_filled_1.index:
    key = extract_filled_1['route_id'].iloc[i]
    extract_filled_1['search_number'].iloc[i] = search_number_dict[key]
    
    
extract_filled_1 = extract_filled_1.set_index(pd.to_datetime(extract_filled_1['Date']))
extract_filled_1.resample('M').count()
months_list = extract_filled_1['RX Number'].resample('M').count().index.astype(str)
#I need to figure out how many times people are ordering a prescription per month 
months_list[1][5:7]
months_numbers = []
for i in range(len(months_list)):
    month = months_list[i][5:7]
    months_numbers.append(month)
    
for m in months_numbers:
    date_range = '2018-' + str(m) 
    num_times_used_that_month = dict(extract_filled_1[date_range].groupby('Flipt Person ID')['RX Number'].count())
    extract_filled_1['Used in ' + m] = ''
    for i in range(len(extract_filled_1)): 
        key = extract_filled_1['Flipt Person ID'].iloc[i]
        if key in num_times_used_that_month.keys():
            extract_filled_1['Used in ' + m].iloc[i] = num_times_used_that_month[key]
        else:
            extract_filled_1['Used in ' + m].iloc[i] = 0
            
extract_filled_1['user_categorization'] = ''
extract_filled_1['Total prescriptions ordered'] = ''
for i in range(0, len(extract_filled_1)):
    flipt_use_pattern = []
    for m in months_numbers:
        flipt_use_pattern.append(extract_filled_1['Used in ' + m].iloc[i])
    prescript_total = sum(np.array(flipt_use_pattern))
    extract_filled_1['Total prescriptions ordered'].iloc[i] = prescript_total

for i in range(0, len(extract_filled_1)):
    prescript_total = extract_filled_1['Total prescriptions ordered'].iloc[i]    
    if prescript_total < 3:
        extract_filled_1['user_categorization'].iloc[i] = 'Infrequent'
    else:
        extract_filled_1['user_categorization'].iloc[i] = 'Frequent'
        
extract_filled_1.to_csv('search_report_extract_filled_' + str(dt.date.today()) + '.csv')    

#*****************************************************************************#
# Begin manipulation for data visualization # 
#*****************************************************************************#

#Separate all of these to compare within groups 
route_1 = extract_filled_1[extract_filled_1['Total prescriptions ordered'] == 1]
np.median(extract_filled_1['search_time_length'])

route_2 = extract_filled_1[extract_filled_1['Total prescriptions ordered'] == 2]
route_2.groupby('search_number')['search_time_length'].median()

route_3 = extract_filled_1[extract_filled_1['Total prescriptions ordered'] == 3]
route_3.groupby('search_number')['search_time_length'].median()


route_4 = extract_filled_1[extract_filled_1['Total prescriptions ordered'] == 4]
route_4.groupby('search_number')['search_time_length'].median()

route_5 = extract_filled_1[extract_filled_1['Total prescriptions ordered'] == 5]
route_5.groupby('search_number')['search_time_length'].median()    
    
#Modify dataset for people who have ordered fewer than 5 prescriptions
less_than_5 = extract_filled_1[extract_filled_1['search_number'] < 5]

  
# Number of actions vs routing number  
sns.set()
sns.set_palette('Blues')

sns.boxplot(x = 'search_number', y = '# actions prior to routing',
            data = less_than_5)
plt.title('Number of Searches vs Search Number')
plt.xlabel('Search Number')
plt.ylabel('# Actions Prior to Routing')
plt.show()               
# Search time vs # routed prescriptions    
sns.set()
sns.set_palette('Reds')
sns.boxplot(x = 'search_number', y = 'search_time_length',
                data = less_than_5)
plt.title('Search Time vs Number of Filled Prescription')
plt.xlabel('# Filled Prescription')
plt.ylabel('Search Time Prior to Routing')
plt.ylim(0,15)
plt.savefig('Search Time vs Search Number_' + str(dt.date.today()) + '.png')
    

#Look at people based on prescription number group

#**** People who have ordered one prescription only ***#
sns.set_palette('Set1')
_ = sns.swarmplot(x = 'search_number', y = 'search_time_length',
            data = route_1)
_ = plt.title('Time to Route vs Routed Prescription Number')
_ = plt.xlabel('# routed prescription')
_ = plt.ylabel('Search time prior to routing (minutes)')
_ = plt.ylim(0,25)
np.median(route_1['search_time_length'].notnull())

medians_2 = (pd.DataFrame(route_2).groupby('search_number')['search_time_length'].median()).reset_index()               
_ = sns.boxplot(x = 'search_number', y = 'search_time_length',
            data = route_2)
_ = plt.title('Time to Route vs Routed Prescription Number')
_ = plt.xlabel('# routed prescription')
_ = plt.ylabel('Search time prior to routing (minutes)')
_ = plt.ylim(0,10)
_ = plt.scatter(np.array(medians_2['search_number'].tolist())-1, medians_2['search_time_length'], color = 'black')

medians_3 = (pd.DataFrame(route_3).groupby('search_number')['search_time_length'].median()).reset_index()               
_ = sns.swarmplot(x = 'search_number', y = 'search_time_length',
            data = route_3)
_ = plt.title('Time to Route vs Routed Prescription Number')
_ = plt.xlabel('# routed prescription')
_ = plt.ylabel('Search time prior to routing (minutes)')
_ = plt.ylim(0,20)
_ = plt.scatter(np.array(medians_3['search_number'].tolist())-1, medians_3['search_time_length'], color = 'black')


medians_4 = (pd.DataFrame(route_4).groupby('search_number')['search_time_length'].median()).reset_index()               
_ = sns.swarmplot(x = 'search_number', y = 'search_time_length',
            data = route_4)
_ = plt.title('Time to Route vs Routed Prescription Number')
_ = plt.xlabel('# routed prescription')
_ = plt.ylabel('Search time prior to routing (minutes)')
_ = plt.ylim(0,15)
_ = plt.scatter(np.array(medians_4['search_number'].tolist())-1, medians_4['search_time_length'], color = 'black')


_ = plt.scatter(1, np.median(route_1['search_time_length'].notnull()), color = 'blue', label = '1 prescrip.')
_ = plt.scatter(np.array(medians_2['search_number'].tolist()), medians_2['search_time_length'], color = 'red', label = '2 prescrip.')
_ = plt.scatter(np.array(medians_3['search_number'].tolist()), medians_3['search_time_length'], color = 'grey', label = '3 prescrip.')
_ = plt.scatter(np.array(medians_4['search_number'].tolist()), medians_4['search_time_length'], color = 'black', label = '4 prescrip.')
_ = plt.legend()
_ = plt.xticks([1,2,3,4])
_ = plt.suptitle('Median search time based on total prescriptions ordered')
_ = plt.xlabel('Prescription order number')
_ = plt.ylabel('Time to routed prescription (minutes)')
_ = plt.savefig('Median search time based on total prescriptions ordered.png')


#Understanding the relationship between # of times app was used prior to using the app
# to route a prescription and the time it takes to route the prescription  
not_zero = extract_filled_1[extract_filled_1['# app uses prior to routing'] != 0]
not_zero_0 = not_zero[not_zero['# app uses prior to routing'] < 6]
short = not_zero_0[not_zero_0['search_time_length'] < 15]                                               
                                             
sns.boxplot(short['# app uses prior to routing'], short['search_time_length'], data = short)
plt.suptitle('Effect of using Flipt App Prior to Routing the Prescription ')       
plt.xlabel('Number app uses prior to routing')
plt.ylabel('Length of search (minutes)') 
plt.savefig('Effect of using Flipt App Prior to Routing the Prescription.png')         
                  
                  
                  
sns.swarmplot(short['# app uses prior to routing'], short['search_time_length'], data = short)
medians_5 = (pd.DataFrame(short).groupby('# app uses prior to routing')['search_time_length'].median()).reset_index()               
plt.scatter(np.array(medians_5['# app uses prior to routing'].tolist())-1, medians_5['search_time_length'], color = 'black')

sns.boxplot(not_zero_0['# app uses prior to routing'], not_zero_0['search_time_length'], data = not_zero_0)
                   

                             


