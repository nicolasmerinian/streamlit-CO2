# Imports
import plotly.express as px
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import os
import plotly.io as pio
import streamlit as st


st.title("Emissions of CO2 by countries")

# Read the CSV
filepath = os.path.join("data", "CO2_per_capita.csv")
df = pd.read_csv(filepath, sep=";")


# Remove the NA values
df = df[df["CO2 Per Capita (metric tons)"].isna() == False]


# Function to get the N top emitters
def top_n_emitters(df, start_year=2008, end_year=2011, nb_displayed=10):
    #years filter
    df_period_mask = (df["Year"] >= start_year) & (df["Year"] < end_year)
    df_period = df[df_period_mask]
    
    #do the mean for each country
    highest_emitters = df_period.groupby("Country Name")["CO2 Per Capita (metric tons)"]\
                                .mean()\
                                .reset_index()
                       
                       
    #sort the values and keep nb_displayed
    highest_emitters = highest_emitters.sort_values(by=["CO2 Per Capita (metric tons)", "Country Name"], ascending=[False, True])\
                                       .head(nb_displayed)

    #create the fig
    fig = px.bar(highest_emitters, x="Country Name", y="CO2 Per Capita (metric tons)")
    
    #return the fig
    return fig



# Display a vertical bar chart of the top 5 emitters between 1965 and 1970
st.markdown("## Top 5 emitters between 1965 and 1970")
fig_bar_chart = top_n_emitters(df, 1965, 1970, 5)
fig_bar_chart.show()
st.plotly_chart(fig_bar_chart)


# Display a bubble chart map to show the emissions of every country across time
st.markdown("## Evolution of CO2 emissions between 1965 and 1970")
fig_map = px.scatter_geo(df
                     , locations="Country Code"
                     , size="CO2 Per Capita (metric tons)"
                     , animation_frame="Year"
                     , hover_name="Country Name"
                     , projection="natural earth"
                     , color="CO2 Per Capita (metric tons)"
                     )
fig_map.update_geos(visible=False
                , resolution=110
                , scope="europe"
                , showcountries=True
                , countrycolor="Black"
                , showsubunits=True
)
fig_map.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map)


st.chat_input
