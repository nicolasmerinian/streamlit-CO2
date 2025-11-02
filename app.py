# Imports
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Wide mode
st.set_page_config(layout="wide")


# Title of the app (centered)
st.markdown("<h1 style='text-align: center; margin-bottom: 0.25rem;'>CO2 emissions per capita</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-top: 0.25rem;'>Interactive dashboard to monitor per-country CO2 emissions per capita and support policy/strategic decisions.</p>", unsafe_allow_html=True)

# Read the CSV
filepath = os.path.join("data", "CO2_per_capita.csv")
df = pd.read_csv(filepath, sep=";")

filepath_geo = os.path.join("data", "geo_data.csv")
df_geo = pd.read_csv(filepath_geo)

# We are going to add the column Continent_Name early so we can filter by continent in the sidebar
df_continents = df_geo[["Three_Letter_Country_Code", "Continent_Name"]]
# Make the join (on Country Code)
df = df.join(df_continents.set_index('Three_Letter_Country_Code'), on='Country Code')

# Add an expander to show dataset info after the join (rows, columns, first 5 rows including joined columns)
with st.expander("Preview of the dataset after joining (click to open)", expanded=False):
    st.write(f"Number of rows: {df.shape[0]}")
    st.write(f"Number of columns: {df.shape[1]}")
    st.write("5 first rows:")
    st.dataframe(df.head(5))

# Remove the NA values
df = df[df["CO2 Per Capita (metric tons)"].isna() == False]


# We sort the dataframe on Year
df = df.sort_values("Year")

min_date = df["Year"].min()
max_date = df["Year"].max()

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


# Select Box to choose the date range
# Replace auto min/max with fixed range 1960-2011
date_range = st.sidebar.slider(
    "Please select a date range",
    min_value=1960,
    max_value=2011,
    value=(1960, 2011)
)


# Select Box to choose the continent to display (filters all charts)
continents_selected = st.sidebar.selectbox(
    "Select a continent to filter countries",
    ('World', 'Africa', 'Antarctica', 'Asia', 'Europe', 'North America', 'Oceania', 'South America'),
)

# Apply continent filter to the main dataframe so all charts use only the selected continent
if continents_selected != "World":
    df = df[df["Continent_Name"] == continents_selected]

    # If no data for the selected continent, notify user and stop further plotting
    if df.empty:
        st.warning(f"No data available for the selected continent: {continents_selected}. Please choose another continent.")
        st.stop()
# if "World" selected, keep df as-is (no continent filter)

# Add a selectbox to control the number of countries displayed in the line chart
nb_of_items_line_chart = st.selectbox(
    "Number of countries displayed?",
    (5, 10, 15),
)

# Filter the data based on the selected date range
df_filtered_by_date = df[(df["Year"] >= date_range[0]) & (df["Year"] <= date_range[1])]

# Display a line chart of CO2 emissions over time
st.markdown("## CO2 Emissions Over Time by Country")
# Sort data by "CO2 Per Capita (metric tons)" in descending order and select top countries
sorted_items = df_filtered_by_date.groupby("Country Name")["CO2 Per Capita (metric tons)"].mean().sort_values(ascending=False).head(nb_of_items_line_chart).index
filtered_df = df_filtered_by_date[df_filtered_by_date["Country Name"].isin(sorted_items)]

# Calculate the world average for each year
world_avg = df_filtered_by_date.groupby("Year")["CO2 Per Capita (metric tons)"].mean().reset_index()
world_avg["Country Name"] = "World"

# Combine the filtered data with the world average
combined_df = pd.concat([filtered_df, world_avg], ignore_index=True)

# Ensure the legend is sorted in descending order of CO2 production
combined_df["Country Name"] = pd.Categorical(
    combined_df["Country Name"],
    categories=list(sorted_items) + ["World"],
    ordered=True
)

fig_line_chart = px.line(
    combined_df,
    x="Year",
    y="CO2 Per Capita (metric tons)",
    color="Country Name",
    title="CO2 Emissions Over Time",
    labels={"CO2 Per Capita (metric tons)": "CO2 Emissions (metric tons per capita)"}
)

# Add annotations for each country's last data point
for country in sorted_items:
    last_year = combined_df[combined_df["Country Name"] == country]["Year"].max()
    last_value = combined_df[(combined_df["Country Name"] == country) & (combined_df["Year"] == last_year)]["CO2 Per Capita (metric tons)"].values[0]
    fig_line_chart.add_annotation(
        x=last_year,
        y=last_value,
        text=country,
        showarrow=False,
        xanchor="left",
        yanchor="middle",
        font=dict(size=10)
    )

# Add annotation for "World"
last_year_world = combined_df[combined_df["Country Name"] == "World"]["Year"].max()
last_value_world = combined_df[(combined_df["Country Name"] == "World") & (combined_df["Year"] == last_year_world)]["CO2 Per Capita (metric tons)"].values[0]
fig_line_chart.add_annotation(
    x=last_year_world,
    y=last_value_world,
    text="World",
    showarrow=False,
    xanchor="left",
    yanchor="middle",
    font=dict(size=10, color="gray")
)

fig_line_chart.update_layout(height=600, margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig_line_chart)

# Display a vertical bar chart of the top N emitters between 2008 and 2011
# Add a local selectbox that only controls this barplot
nb_of_countries_bar1 = st.selectbox(
    "Number of countries displayed?",
    (3, 5, 10, 20, 30),
)

st.markdown(f"## Top {nb_of_countries_bar1} emitters between {date_range[0]} and {date_range[1]}")
fig_bar_chart = top_n_emitters(df, date_range[0], date_range[1], nb_of_countries_bar1)
st.plotly_chart(fig_bar_chart)


# Add a switch to toggle between scatter_geo and choropleth maps
map_type = st.radio(
    "Select the type of map to display:",
    ("Scatter Geo", "Choropleth"),
    horizontal=True
)

st.markdown(f"## Evolution of CO2 emissions between {date_range[0]} and {date_range[1]}")

# Display a bubble chart map to show the emissions of every country across time
# filter dataframe to the selected period (inclusive)
df_period_map = df[(df["Year"] >= date_range[0]) & (df["Year"] <= date_range[1])]

if df_period_map.empty:
    st.warning("No data for the selected continent in the chosen date range. Adjust the date range or continent to see the maps.")
else:
    # ensure Year is integer for animation frames (avoid unexpected types)
    df_period_map["Year"] = df_period_map["Year"].astype(int).copy()  # Force Year to int on a copy

    if map_type == "Scatter Geo":
        fig_map = px.scatter_geo(df_period_map
                         , locations="Country Code"
                         , size="CO2 Per Capita (metric tons)"
                         , animation_frame="Year"
                         , hover_name="Country Name"
                         , projection="natural earth"
                         , color="CO2 Per Capita (metric tons)"
                         )
        fig_map.update_geos(visible=False
                    , resolution=110
                    , showcountries=True
                    , countrycolor="Black"
                    , showsubunits=True
        )
        fig_map.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map)

    elif map_type == "Choropleth":
        fig_choropleth = px.choropleth(df_period_map
                        , locations="Country Code"
                        , locationmode="ISO-3"  # Add locationmode
                        , color="CO2 Per Capita (metric tons)"
                        , animation_frame="Year"
                        , hover_name="Country Name"
                        , title="CO2 emissions per capita"
                        , color_continuous_scale=px.colors.sequential.YlOrRd)

        fig_choropleth.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_choropleth)


# Display a bar chart map to show the emissions of every country across time with continents colored
# Add a local selectbox that only controls this barplot
nb_of_countries_bar2 = st.selectbox(
    "Number of countries displayed",
    (3, 5, 10, 15, 20, 30),
)

st.markdown(f"## Top {nb_of_countries_bar2} emitters between {date_range[0]} and {date_range[1]} with colors by continents")
#The function
def top_n_emitters_v2(df, start_year=2008, end_year=2011, nb_displayed=10):
    print(df.columns)
    #years filter
    df_period_mask = (df["Year"] >= start_year) & (df["Year"] < end_year)
    df_period = df[df_period_mask]
    print(df_period.columns)
    
    #do the mean for each country
    highest_emitters = df_period.groupby(["Country Name", "Continent_Name"])["CO2 Per Capita (metric tons)"]\
                                .mean()\
                                .reset_index()
                       
                       
    #sort the values and keep nb_displayed
    highest_emitters = highest_emitters.sort_values(by=["CO2 Per Capita (metric tons)", "Country Name"], ascending=[False, True])\
                                       .head(nb_displayed)

    #create the fig
    fig = px.bar(highest_emitters, y="Country Name", x="CO2 Per Capita (metric tons)", color="Continent_Name")
    
    #return the fig
    return fig

fig_bar_continents = top_n_emitters_v2(df, date_range[0], date_range[1], nb_of_countries_bar2)
st.plotly_chart(fig_bar_continents)

# Add a phrase at the bottom of the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("The purpose of this dashboard was to experiment with Streamlit and Copilot.")


