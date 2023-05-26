import streamlit as st
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.cm as cm
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os.path
from PIL import Image

###################################
# Page configuration and layout:

st.set_page_config(page_title="Spiders Biodiversity in Switzerland App", # page title, displayed on the window/tab bar
        		   page_icon="spider", # favicon: icon that shows on the window/tab bar (tip: you can use emojis)
                   layout="wide", # use full width of the page
                   menu_items={
                       'About': "Spiders biodiversity in switzerland"
                   })

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.write(' ')

with col2:
    st.write(' ')

with col3:
    image = Image.open("data/spiderman.png")
    #new_image = image.resize((200, 300))
    st.image(image)

with col4:
    st.write(' ')

with col5:
    st.write(' ')

st.markdown("<h1 style='text-align: center; color: red;'>Exploring changes in spider species distribution and their relationship with the average temperature</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: grey;'>Team members: Robin Portmann, Michelle Peter and Ansam Zedan</h4>", unsafe_allow_html=True)

###########################
# Read Data and Cleaning

data = pd.read_parquet('data/final_dataset.parquet')

data = data.drop(columns = ['kingdom', 'class', 'Unnamed: 0', 'phylum', 'order', 'scientificName', 'verbatimScientificName', 'countryCode'])

with open('data/georef-switzerland-kanton.geojson') as response:
    regions = json.load(response)

data = data[data['Year'] >= 1980]

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
data['landscape'] = data['stateProvince'].map(mapping)

##################
# side bar

with st.sidebar:
    bulletpoints = ['Introduction', 'Data Description and Source', 
                    'Has the composition of spider species in Switzerland changed between 1896 and 2021, and is there a correlation between the distribution of spider species and average temperature fluctuations?',
                    'Methods Used', 'Maps Plotted', 'Geographical Scope', 'Outlook']
    s2 = ''
    for i in bulletpoints:
        s2 += "- " + i + "\n"
    st.markdown(s2)

###################
# Maps

# Spiders biodiversity swiss cantons

# df_filtered_gr = data.groupby(['stateProvince', 'species','Year','decimalLatitude','decimalLongitude']).agg({'occurrenceStatus' : 'count', 'Temperature' : 'mean', 'Precipitation': 'mean'}).reset_index()
# df_filtered_gr = data.sort_values(by=['Year','stateProvince','species'], ascending=True)

# st.write('done')
# fig = px.choropleth_mapbox(df_filtered_gr, geojson=regions, locations='stateProvince',
#                     color='occurrenceStatus', hover_data=['Temperature', 'Precipitation', 'stateProvince'],
#                     animation_frame = 'Year',
#                     featureidkey="properties.kan_name",
#                     center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
#                     mapbox_style="carto-positron", zoom=7, opacity=0.8, width=1500, height=750,
#                     title='Spider Biodiversity in Switzerland',
#                     labels={"stateProvince":"Canton",
#                            "occurrenceStatus":"Number of spiders present"},
#                     color_continuous_scale="Viridis")
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Sans"})

# fig2 = px.scatter_mapbox(df_filtered_gr, lat="decimalLatitude", lon="decimalLongitude", hover_name="species", hover_data=["occurrenceStatus", "Temperature", "Precipitation"],
#                         color="occurrenceStatus", animation_frame = 'Year',
#                         color_continuous_scale=px.colors.sequential.Hot, size_max=15, zoom=7, width=1500, height=750,
#                         title='Spider Biodiversity in Switzerland',
#                         labels={"stateProvince":"Canton",
#                                "occurrenceStatus":"Number of spiders present"},
#                         center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
#                         mapbox_style="carto-positron")

# fig.add_trace(fig2.data[0])
# for i,frame in enumerate(fig.frames):
#     fig.frames[i].data += (fig2.frames[i].data[0],)

# st.plotly_chart(fig)


# choose which spider family you would like to explore
spider_families = data.family.unique()
fam_selection = st.multiselect('Which spider families you would like to explore?', spider_families, default = 'Linyphiidae')

data_sub = data[data['family'].isin(fam_selection)]

agree = st.checkbox('Would you like to see the list of species in this family/families')
if agree:
    s = ''
    for i in data_sub.species.unique():
        s += "- " + i + "\n"
    st.markdown(s)

counts_per_fam = data_sub.groupby(['species', 'stateProvince', 'decimalLatitude', 'decimalLongitude', 'Year', 'Month']).agg({'occurrenceStatus':'size', 'Temperature': 'mean', 'Precipitation': 'mean'}).reset_index()


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

st.plotly_chart(fig3)

# Temperature and Per and Spiders's number
counts_per_fam_2 = counts_per_fam.copy(deep=True)
counts_per_fam_2['date'] = pd.to_datetime(counts_per_fam_2[['Year', 'Month']].assign(DAY=1))
counts_per_fam_2 = counts_per_fam_2.sort_values('date', ascending=True)
counts_per_fam_2['date'] = counts_per_fam_2['date'].dt.strftime('%m-%d-%Y')

st.write('finished')
fig4 = px.choropleth_mapbox(counts_per_fam_2, geojson=regions, locations='stateProvince',
                    color='Temperature', hover_data=['stateProvince'],
                    animation_frame = 'date',
                    featureidkey="properties.kan_name",
                    center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                    mapbox_style="carto-positron", zoom=7, opacity=0.8, width=1500, height=750,
                    title='Spider Biodiversity in Switzerland',
                    labels={"stateProvince":"Canton",
                           "Temperature":"Number of spiders present"},
                    color_discrete_sequence="RdBu")

fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Sans"})
st.write('finished')
fig5 = px.scatter_mapbox(counts_per_fam_2, lat="decimalLatitude", lon="decimalLongitude", hover_name="species", hover_data=["occurrenceStatus", "Temperature", "Precipitation"],
                        color="occurrenceStatus", animation_frame = 'date',
                        color_continuous_scale=px.colors.sequential.Hot, size_max=15, zoom=7, width=1500, height=750,
                        title='Spider Biodiversity in Switzerland',
                        labels={"stateProvince":"Canton",
                               "occurrenceStatus":"Number of spiders present"},
                        center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                        mapbox_style="carto-positron")
st.write('finished')
fig4.add_trace(fig5.data[0])
for i,frame in enumerate(fig4.frames):
    fig4.frames[i].data += (fig5.frames[i].data[0],)

st.plotly_chart(fig4)