# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 23:35:20 2016

@author: andrew walter owens
"""

import seaborn, datetime
import pandas as pd
import lifelines
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
import numpy as np

file_name = 'NYC_Rest_Ratings_Data.csv'
#df = pd.read_csv('https://nycopendata.socrata.com/api/views/xx67-kt59/rows.csv?accessType=DOWNLOAD')
#df.to_csv(file_name)
df = pd.read_csv(file_name)

### Date Conversions
df['INSPECTION DATE'] = pd.to_datetime([datetime.datetime.strptime(d, "%m/%d/%Y").strftime("%Y-%m-%d") for d in df['INSPECTION DATE']])
df['RECORD DATE'] = pd.to_datetime([datetime.datetime.strptime(d, "%m/%d/%Y").strftime("%Y-%m-%d") for d in df['RECORD DATE']])

#Get Subsets of Dates:
min_i_date = df.groupby('CAMIS')['INSPECTION DATE'].min().reset_index()
min_grade_date = df.groupby(['CAMIS','GRADE'])['INSPECTION DATE'].min().reset_index()
max_grade_date = df.groupby(['CAMIS','GRADE'])['INSPECTION DATE'].max().reset_index()

start_set = min_grade_date[min_grade_date["GRADE"] == 'A']

## GET 'DEATH' CATEGORIZATIONS
#GRADE DATA DEFINITIONS: (As of Aug 31st, 2016)
#N = Not Yet Graded 
#A = Grade A
#B = Grade B
#C = Grade C
#Z = Grade Pending 
#P = Grade Pending issued on re-opening following an initial inspection that resulted in a closure
end_set = min_grade_date[(min_grade_date["GRADE"] != 'A') & (min_grade_date["GRADE"] != 'Z')]
#GET THE MINIMUM GRADE FOR ANY OTHER GRADE BUT AN A
end_set = end_set.groupby('CAMIS')["INSPECTION DATE"].min().reset_index()

#a_grades contains resturants which started with A's only (all time)
a_grades = pd.merge(min_i_date, start_set, on=['CAMIS','INSPECTION DATE'], how='inner')

c = pd.merge(a_grades[['CAMIS','INSPECTION DATE']], end_set, on=['CAMIS'], how='inner')

c['duration'] = c['INSPECTION DATE_y'] - c['INSPECTION DATE_x']
#Convert the timedelta object to a date
c['duration'] = (c['duration'] / np.timedelta64(1, 'D')).astype(int)

c.duration.hist(bins=100).plot(title='Distribution of Grade Changes')
#appears to show a significant change around 400 days or roughly a year after the first A rating
f = pd.merge(start_set,c[['CAMIS','duration']], on=['CAMIS'], how= 'left')

#### Now we have our list of all the death events observed... but what about those still trucking with A's?
#
max_grade_date = df.groupby(['CAMIS','GRADE'])['INSPECTION DATE'].max()
#max_g_date = df.groupby(['CAMIS','GRADE'])['INSPECTION DATE'].max()
mgd = max_grade_date.unstack().reset_index()
mgd = mgd[(mgd.B.isnull() == True) & (mgd.C.isnull() == True) & (mgd.C.isnull() == True) & (mgd['Not Yet Graded'].isnull() == True) & (mgd.P.isnull() == True) & (mgd.Z.isnull() == True)]

mgda = pd.merge(max_grade_date.reset_index(),mgd[['CAMIS']],on=['CAMIS'])
mgda = pd.merge(start_set, mgda, on=['CAMIS'], how='inner')

mgda['duration'] = mgda['INSPECTION DATE_y'] - mgda['INSPECTION DATE_x']
#Convert the timedelta object to a date
mgda['duration'] = (mgda['duration'] / np.timedelta64(1, 'D')).astype(int)


####UNION MGDA (ALL A's) && f
mgda['observed'] = 0 #death is not observed
f['observed'] = 1 #death is observed
data = pd.concat([mgda[['CAMIS','duration','observed']],f[['CAMIS','duration','observed']]])

data = data.groupby(['CAMIS','observed'])['duration'].sum().unstack()
data = data[(data[1].isnull() == False) | (data[0].isnull() == False)].stack().reset_index()

data.columns = 'CAMIS', 'observed', 'duration'

##### OVERALL MODEL:
kmf = KaplanMeierFitter()

T = data["duration"]
C = data["observed"]

kmf.fit(T, event_observed=C)

kmf.survival_function_.plot()
plt.title('Survival of A (From the Start) Grade Restaurants in NYC')

print 'Median Time on Site is: ' + str(kmf.median_)

print 'Median Time on Site is: ' + str(kmf.median_)

## HAZARD FUNCTION: 
from lifelines import NelsonAalenFitter
naf = NelsonAalenFitter()

naf.fit(T, event_observed=C)
ax = naf.plot(ix=slice(0,1000),secondary_y=True)
c.duration.hist(bins=100).plot(title='Distribution of Grade Changes')
plt.show()

##### SPLIT BY BORO:

boro = df[['CAMIS','BORO']].drop_duplicates()

borod = pd.merge(data,boro,on=['CAMIS'])

ax = plt.subplot(111)
dem = (borod.BORO == "MANHATTAN")
kmf.fit(T[dem], event_observed=C[dem], label="MANHATTAN")
kmf.plot(ax=ax)
dem2 = (borod.BORO == "BRONX")
kmf.fit(T[dem2], event_observed=C[dem2], label="BRONX")
kmf.plot(ax=ax)
dem3 = (borod.BORO == "QUEENS")
kmf.fit(T[dem3], event_observed=C[dem3], label="QUEENS")
kmf.plot(ax=ax)
dem4 = (borod.BORO == "STATEN ISLAND")
kmf.fit(T[dem4], event_observed=C[dem4], label="STATEN ISLAND")
kmf.plot(ax=ax)
dem5 = (borod.BORO == "Missing")
kmf.fit(T[dem5], event_observed=C[dem5], label="Missing")
kmf.plot(ax=ax)
plt.ylim(0.75,1);
plt.title("Lifespans of A rated restaurant by NYC borough")
plt.savefig("Lifespans of A rated restaurant by NYC borough");


from lifelines import NelsonAalenFitter
naf = NelsonAalenFitter()

naf.fit(T[dem], event_observed=C[dem], label="MANHATTAN")
ax = naf.plot(ix=slice(0,1000))
naf.fit(T[dem2], event_observed=C[dem2], label="BRONX")
naf.plot(ax=ax, ix=slice(0,1000))
naf.fit(T[dem3], event_observed=C[dem3], label="QUEENS")
naf.plot(ax=ax, ix=slice(0,1000))
naf.fit(T[dem4], event_observed=C[dem4], label="STATEN ISLAND")
naf.plot(ax=ax, ix=slice(0,1000))
naf.fit(T[dem5], event_observed=C[dem5], label="Missing")
naf.plot(ax=ax, ix=slice(0,1000))
plt.title("Hazard functions of A rated restaurant by NYC borough")
plt.savefig("Hazard functions of A rated restaurant by NYC borough.png");