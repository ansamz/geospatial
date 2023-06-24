#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.cm as cm
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os.path
from PIL import Image


# In[2]:


def read_data(path):
    df = pd.read_parquet(path)
    return df

def read_json(path):
    with open(path) as response:
        result = json.load(response)
    return result


# Data Processing

# In[3]:


data = read_data('C:\\Users\\Ansam\\Documents\\github\\geospatial\\data\\final_dataset.parquet')

data = data.drop(columns = ['kingdom', 'class', 'Unnamed: 0', 'phylum', 'order', 'scientificName', 'verbatimScientificName', 'countryCode'])

regions = read_json('C:\\Users\\Ansam\\Documents\\github\\geospatial\\data\\georef-switzerland-kanton.geojson')

data = data[data['Year'] >= 1980]

data = data.replace({'PRESENT': 1})

alpine_Cantons = ['Valais', 'Graubünden', 'Uri', 'Bern', 'Ticino', 'Schwyz', 'Glarus', 'Obwalden', 'Nidwalden', 'Appenzell', 'St. Gallen']
plateau_Cantons = ['Zürich', 'Aargau', 'Luzern', 'Thurgau', 'Solothurn', 'Basel', 'Schaffhausen', 'Zug', 'Fribourg', 'Genève']
jura_Cantons = ['Neuchâtel', 'Jura', 'Vaud']

# Create a mapping dictionary for each type
mapping = {}
for canton in alpine_Cantons:
    mapping[canton] = 'Alpine'
for canton in plateau_Cantons:
    mapping[canton] = 'Plateau'
for canton in jura_Cantons:
    mapping[canton] = 'Jura'

# Map the types to a new 'Type' column in the DataFrame
data['Landscape'] = data['stateProvince'].map(mapping)

data['day'] = 1
data['date'] = pd.to_datetime(data[['Year', 'Month', 'day']])


# Map 1: Spiders biodiversity swiss cantons

# In[ ]:


df_filtered_gr = data.groupby(['stateProvince', 'species','Year','decimalLatitude','decimalLongitude']).agg({'occurrenceStatus' : 'count', 'Temperature' : 'mean', 'Precipitation': 'mean'}).reset_index()
df_filtered_gr = data.sort_values(by=['Year'], ascending=True)

fig = px.choropleth_mapbox(df_filtered_gr, geojson=regions, locations='stateProvince',
                    color='occurrenceStatus', hover_data=['Temperature', 'Precipitation', 'stateProvince'],
                    animation_frame = 'Year',
                    featureidkey="properties.kan_name",
                    center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                    mapbox_style="carto-positron", zoom=7, opacity=0.8, width=1500, height=750,
                    title='Spider Biodiversity in Switzerland',
                    labels={"stateProvince":"Canton",
                           "occurrenceStatus":"Number of spiders present"},
                    color_continuous_scale="Viridis")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Sans"})
fig.show()


# In[5]:


fig.write_html("C:\\Users\\Ansam\\Documents\\github\\geospatial\\maps_html\\map1_spiders_biodiversity_swiss_cantons.html")


# Map2: choose which spider family you would like to explore

# In[6]:


data.family.unique()


# In[ ]:


data_sub = data[data['family'].isin(['Tetragnathidae', 'Theridiidae', 'Scytodidae', 'Araneidae', 'Zoropsidae'])]
counts_per_fam = data_sub.groupby(['species', 'stateProvince', 'decimalLatitude', 'decimalLongitude', 'Year', 'Month', 'Landscape']).agg({'occurrenceStatus':'size', 'Temperature': 'mean', 'Precipitation': 'mean'}).reset_index()


fig3 = px.scatter_mapbox(
    counts_per_fam.sort_values('Year'),
    color="species",
    #size='occurrenceStatus',
    lat='decimalLatitude', lon='decimalLongitude',
    animation_frame="Year",
    center={"lat": 46.8, "lon": 8.3},
    hover_data=['stateProvince', 'Temperature', 'Precipitation', 'occurrenceStatus'],
    mapbox_style="open-street-map",
    zoom=6.3,
    opacity=0.8,
    width=1400,
    height=750,
    labels={"stateProvince":"Canton",
            "Temperature": "Temperature",
            "Precipitation": "Precipitation",
            "occurrenceStatus":"Number of occurrences"},
    title="<b>Number of spider spottings for specific families per species</b>",
    color_continuous_scale="Viridis"
)
fig3.update_layout(margin={"r":0,"t":35,"l":0,"b":0},
                  font={"family":"Sans",
                       "color":"maroon"},
                  hoverlabel={"bgcolor":"white",
                              "font_size":15,
                             "font_family":"Arial"},
                  title={"font_size":20,
                        "xanchor":"left", "x":0.01,
                        "yanchor":"bottom", "y":0.95}
                 )

fig3.show()


# In[8]:


fig3.write_html("C:\\Users\\Ansam\\Documents\\github\\geospatial\\maps_html\\map2_spider_family_exploration.html")


# Map3: Explore the effects of Temperature on the spider families selected before

# In[9]:


counts_per_fam_2 = counts_per_fam.copy(deep=True)
counts_per_fam_2 = counts_per_fam_2.sort_values('Year', ascending=True)


# In[ ]:


temp_per = "Temperature"
df_filtered_gr2 = counts_per_fam_2.groupby(['stateProvince', 'species','Year','decimalLatitude','decimalLongitude','Landscape']).agg({'occurrenceStatus' : 'sum', 'Temperature' : 'mean', 'Precipitation': 'mean'}).reset_index()
df_filtered_gr2 = counts_per_fam_2.sort_values(by=['Year'], ascending=True)

fig4 = px.choropleth_mapbox(df_filtered_gr2, geojson=regions, locations='stateProvince',
                    color=temp_per, hover_data=['stateProvince', 'occurrenceStatus'],
                    animation_frame = 'Year',
                    featureidkey="properties.kan_name",
                    center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                    mapbox_style="carto-positron", zoom=7, opacity=0.8, width=1500, height=750,
                    title='Spider Biodiversity in Switzerland',
                    labels={"stateProvince":"Canton",
                           temp_per : temp_per},
                    color_discrete_sequence="RdBu")

fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Sans"})

fig5 = px.scatter_mapbox(df_filtered_gr2, lat="decimalLatitude", lon="decimalLongitude", hover_name="species", hover_data=["occurrenceStatus", "Temperature", "Precipitation"],
                        color="occurrenceStatus", animation_frame = 'Year',
                        color_continuous_scale=px.colors.sequential.Viridis, size_max=15, zoom=7, width=1500, height=750,
                        title='Spider Biodiversity in Switzerland',
                        labels={"stateProvince":"Canton",
                               "occurrenceStatus":"Number of spiders present"},
                        center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                        mapbox_style="carto-positron")

fig4.add_trace(fig5.data[0])
for i,frame in enumerate(fig4.frames):
    fig4.frames[i].data += (fig5.frames[i].data[0],)

fig4.show()


# In[11]:


fig4.write_html("C:\\Users\\Ansam\\Documents\\github\\geospatial\\maps_html\\map3_spider_family_exploration_num_temp.html")


# Map4: Explore the effects of Precipitation on the spider families selected before

# In[ ]:


temp_per = "Precipitation"
df_filtered_gr2 = counts_per_fam_2.groupby(['stateProvince', 'species','Year','decimalLatitude','decimalLongitude','Landscape']).agg({'occurrenceStatus' : 'sum', 'Temperature' : 'mean', 'Precipitation': 'mean'}).reset_index()
df_filtered_gr2 = counts_per_fam_2.sort_values(by=['Year'], ascending=True)

fig4 = px.choropleth_mapbox(df_filtered_gr2, geojson=regions, locations='stateProvince',
                    color=temp_per, hover_data=['stateProvince', 'occurrenceStatus'],
                    animation_frame = 'Year',
                    featureidkey="properties.kan_name",
                    center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                    mapbox_style="carto-positron", zoom=7, opacity=0.8, width=1500, height=750,
                    title='Spider Biodiversity in Switzerland',
                    labels={"stateProvince":"Canton",
                           temp_per : temp_per},
                    color_discrete_sequence="RdBu")

fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Sans"})

fig5 = px.scatter_mapbox(df_filtered_gr2, lat="decimalLatitude", lon="decimalLongitude", hover_name="species", hover_data=["occurrenceStatus", "Temperature", "Precipitation"],
                        color="occurrenceStatus", animation_frame = 'Year',
                        color_continuous_scale=px.colors.sequential.Viridis, size_max=15, zoom=7, width=1500, height=750,
                        title='Spider Biodiversity in Switzerland',
                        labels={"stateProvince":"Canton",
                               "occurrenceStatus":"Number of spiders present"},
                        center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                        mapbox_style="carto-positron")

fig4.add_trace(fig5.data[0])
for i,frame in enumerate(fig4.frames):
    fig4.frames[i].data += (fig5.frames[i].data[0],)

fig4.show()


# In[13]:


fig.write_html("C:\\Users\\Ansam\\Documents\\github\\geospatial\\maps_html\\map4_spider_family_exploration_num_pre.html")

