# import necessary libraries

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import lxml.html as lh
import pandas as pd

#url of the data we need
url = 'http://pokemondb.net/pokedex/all'
 #'https://data.nasa.gov/Software/Open-Source-And-General-Resource-Software/fk38-4khf/data'
page = requests.get(url)

doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')

#Check the length of the first 12 rows
[len(T) for T in tr_elements[:12]]

#Create empty list
col=[]
i=0

#For each row, store each first element (header) and an empty list
for t in tr_elements[0]:
    i+=1
    name=t.text_content()
   # print "%d:"%s" " %(i,name)
    col.append((name,[]))
    
#Since out first row is the header, data is stored on the second row onwards
for j in range(1,len(tr_elements)):
    #T is our j'th row
    T=tr_elements[j]
    
    #If row is not of size 5, the //tr data is not from our table 
    if len(T)!=10:
        break
    
    #i is the index of our column
    i=0
    
    #Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content() 
        #Check if row is empty
        if i>0:
        #Convert any numerical value to integers
            try:
                data=int(data)
            except:
                pass
        #Append the data to the empty list of the i'th column
        col[i][1].append(data)
        #Increment i for the next column
        i+=1
        
Dict={title:column for (title,column) in col}

df=pd.DataFrame(Dict)

df.head()

import pyodbc
import statistics

#connect to our database
connection = pyodbc.connect(
    "DRIVER={PostgreSQL Unicode(x64)};"
    "DATABASE=pokemon;"
    "UID=postgres;"
    "PWD=*******;"
    "SERVER=localhost;"
    "PORT=5432;"
    )

print("Connection Successful!")

#create cursor
cursor = connection.cursor()

#adjut settings to allow for easy creating of tables
cursor.execute("SET client_encoding TO 'UTF8';")
cursor.commit()

#split dataframe into 2 different tables
podex = df.iloc[:,0:4]
podex = podex.drop(['#'], axis = 1) #drop a column with repetition
podex.head()

#create unique id column
podex['ID'] = range(len(podex))
podex.head()

fight = df.iloc[:,4:10]
fight.head()

#create unique id column
fight['ID'] = range(len(fight))
fight.head()

import sqlalchemy  # Package for accessing SQL databases via Python

# Connect to database (Note: The package psychopg2 is required for Postgres to work with SQLAlchemy)
engine = sqlalchemy.create_engine("postgresql://postgres:Ekxxcoo4@localhost/pokemon")
con = engine.connect()

# Verify that there are no existing tables
print(engine.table_names())

#convert our dataframes into tables in postgres
podex.to_sql('pokedex', con = engine, if_exists='replace', index = False)
fight.to_sql('fighting', con, if_exists='replace', index = False)

