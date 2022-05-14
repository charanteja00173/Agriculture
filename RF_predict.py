
import sys
import pandas as pd
import datetime
from bs4 import BeautifulSoup
import pickle
import requests, json 
import gzip
import sklearn
from sklearn.ensemble import RandomForestRegressor

import numpy as np
dataset = pd.read_csv(r'C:\xampp\htdocs\mp.csv')
X = dataset.iloc[:, 3:].values
y = dataset.iloc[:, 2].values
from sklearn.ensemble import RandomForestRegressor
regressor = RandomForestRegressor(n_estimators = 10, random_state = 0)
regressor.fit(X, y)
  

# print ('Number of arguments:', len(sys.argv), 'arguments.')
# print ('Argument List:', str(sys.argv))
  

dist_list = ['ADILABAD', 'HANUMAKONDA', 'BHADRADRI KOTHAGUDEM', 'HYDERABAD', 'JAGTIAL', 'JANGOAN', 'WANAPARTHY', 'JOGULAMBA GADWAL', 'KAMAREDDY', 'KARIMNAGAR', 'KHAMMAM', 'KOMARAM BHEEM ASIFABAD', 'MAHABUBABAD', 'MAHABUBNAGAR', 'MANCHERIAL', 'MEDAK', 'MEDCHAL-MALKAJGIRI', 'MULUG', 'NAGARKURNOOL', 'NALGONDA', 'NARAYANPET', 'NIRMAL', 'NIZAMABAD', 'PEDDAPALLI', 'WARANGAL', 'RANGAREDDY', 'SANGAREDDY', 'SIDDIPET', 'SURYAPET', 'VIKARABAD']
crop_list = ['Jowar', 'Bajra', 'Wheat']
soil_list = ['chalky', 'clay', 'loamy', 'peaty', 'sandy', 'silty']

district = sys.argv[1]
Crop = sys.argv[2]
Area = int(sys.argv[3])
soil_type = sys.argv[4]

# district = 'HYDERABAD'
# Crop = 'Jowar'
# Area = 598400
# soil_type = 'clay'

district = "District:_"+district
Crop = "Crop:_"+Crop
soil_type = "Soil_type:_"+soil_type




api_key = "9198e09168f94f8ad8131f6f6058bc95"    # Use your own API key. You can get it for free from openweathermap
  
base_url = "http://api.openweathermap.org/data/2.5/weather?"
  
# city_name = sys.argc[1]
city_name = 'HYDERABAD'

complete_url = base_url + "appid=" + api_key + "&q=" + city_name 

response = requests.get(complete_url) 

x = response.json() 

# print(x)
if x["cod"] != "404": 
    y = x["main"] 
    temp = y["temp"]-273
    humi = y["humidity"]  
    try:
        preci_humi_link = 'https://www.worldweatheronline.com/lang/en-in/pune-weather/maharashtra/in.aspx'
        p2 = requests.get(preci_humi_link)
        s2 = BeautifulSoup(p2.content, 'html.parser')
        preci_table = ((s2.find_all('div', attrs={'class':'tb_cont_item', 'style':'background-color:#ffffff;'})))
        preci = 0
        for ele in preci_table[21::2]:
            if ele.text == '0.00 mm':
                preci += float(ele.text.replace("mm", "").strip())        
        preci *= 6
        # print("Average precipitation: ", preci)
        humi_table = ((s2.find_all('div', attrs={'class':'tb_row tb_rain'})))
        humi = 0
        for ele in humi_table:
            if len(ele.text) > 15:
                humi = ele.text.replace("Rain", "").split("%")[:-1]
        humi = sum(list(map(float, humi)))
        humi *= 6
        # print ("Average humidity: ", humi)
    except:
        preci = 0
        humi = 0


    X = ['Area', 'Temperature', 'Precipitaion', 'Humidity', 'Soil_type:_chalky',
       'Soil_type:_clay', 'Soil_type:_loamy', 'Soil_type:_peaty',
       'Soil_type:_sandy', 'Soil_type:_silt', 'Soil_type:_silty',
       'District:_ADILABAD', 'District:_HANUMAKONDA', 'District:_BHADRADRI KOTHAGUDEM',
       'District:_HYDERABAD', 'District:_JAGTIAL', 'District:_JANGOAN',
       'District:_WANAPARTHY', 'District:_JOGULAMBA GADWAL', 'District:_KAMAREDDY',
       'District:_KARIMNAGAR', 'District:_KHAMMAM', 'District:_KOMARAM BHEEM ASIFABAD',
       'District:_MAHABUBABAD', 'District:_MAHABUBNAGAR', 'District:_MANCHERIAL',
       'District:_MEDAK', 'District:_MEDCHAL-MALKAJGIRI', 'District:_MULUG',
       'District:_NAGARKURNOOL', 'District:_NALGONDA', 'District:_NARAYANPET',
       'District:_NIRMAL', 'District:_NIZAMABAD', 'District:_PEDDAPALLI',
       'District:_WARANGAL', 'District:_RANGAREDDY', 'District:_SANGAREDDY',
       'District:_SIDDIPET', 'District:_SURYAPET', 'District:_VIKARABAD',
       'Crop:_Bajra', 'Crop:_Jowar', 'Crop:_Wheat', 'Season:_Kharif',
       'Season:_Rabi', 'Season:_zaid']

    index_dict = dict(zip(X,range(len(X))))

    vect = {}
    for key, val in index_dict.items():
        vect[key] = 0
    try:
        vect[district] = 1
    except Exception as e:
        print("Exception occered for DISTRICT!", e)
    try:
        vect[Crop] = 1
    except Exception as e:
        print("Exception occered for CROP!")
    try:
        vect[soil_type] = 1
    except Exception as e:
        print("Exception occered for SOIL TYPE!")
    try:
        vect['Area'] = Area
    except Exception as e:
        print("Exception occered for AREA!", e)
    try:
        vect['Temperature'] = temp
    except Exception as e:
        print("Exception occered for TEMP!", e)
    try:
        vect['Precipitaion'] = preci
    except Exception as e:
        print("Exception occered for PRECI!", e)
    try:
        vect['Humidity'] = humi
    except Exception as e:
        print("Exception occered for HUMI!", e)

    now = datetime.datetime.today()
    season = "Season:_Kharif" if (now.month >= 7 and now.month <= 10) else "Season:_Rabi"
    vect[season] = 1

    #print(vect, len(vect))
    df = pd.DataFrame.from_records(vect, index=[0])

    res = regressor.predict(df)[0]

    #res = regressor.predict([[Area,temp,preci,humi,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0]])

    print ("The predicted YIELD for given attributes is approximately: ", (res), "tons.")


else: 
    print(" District Not Found ")