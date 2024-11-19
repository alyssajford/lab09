import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)

st.write("Baby Names Over the Years")

tab1, tab2 = st.tabs(["Names over Time", "Top Names by Years"])

with st.sidebar:
    input_name = st.text_input("Enter a name: ")
    year_input = st.slider("year", min_value = 1880, max_value = 2023, value = 2000)
    gender_filter = st.selectbox("Select gender", ["All", "M", "F"])
    min_count = st.number_input("Minimum count for name to be included", min_value=0, value=10)



# Tab 1: Names over Time
with tab1:
    # Filter data based on name and gender
    if gender_filter != "All":
        # Apply gender filtering if the user selects "Male" or "Female"
        name_data = data[
            (data["name"] == input_name) & 
            (data["sex"].str.lower() == gender_filter.lower()) & 
            (data["count"] >= min_count)
        ].copy()
    else:
        # Show data for all genders if "All" is selected
        name_data = data[
            (data["name"] == input_name) & 
            (data["count"] >= min_count)
        ].copy()
    
    fig = px.line(name_data, x="year", y="count", color="sex", title="Popularity of Name Over Time")
    st.plotly_chart(fig)


with tab2:
    fig2 = top_names_plot(data, year = year_input)
    st.plotly_chart(fig2)
    



