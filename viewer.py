from datetime import timedelta

import altair as alt
import pandas as pd
import streamlit as st

# run by running 'streamlit run viewer.py' in the command prompt


def wide_space_default():
    st.set_page_config(layout="wide")


wide_space_default()
st.title("Forecast Viewer")


# Load data
@st.cache_data
def load_data():
    data = pd.read_csv("forecast_withdate.csv")
    data["Date"] = pd.to_datetime(data["Date"])
    return data


df = load_data()


default_entity = sorted(df["Entity"].unique())  # Sort the entity list alphabetically
default_entity_selection = [default_entity[0]] if default_entity else []


# default_start_date = df["Date"].min()
# default_end_date = default_start_date + timedelta(days=1000)
default_start_date = df["Date"].min().to_pydatetime()
default_end_date = df["Date"].max().to_pydatetime()
date_range = [default_start_date, default_end_date]

entity = st.sidebar.multiselect(
    "Select Entity (Push x to see all):", options=default_entity, default=default_entity_selection
)
# date_range = st.sidebar.date_input("Select Date Range:", value=date_range)

date_range = st.sidebar.slider(
    "Select Date Range:",
    min_value=default_start_date,
    max_value=default_end_date,
    value=(default_start_date, default_end_date),
)
# Convert date_range to pandas timestamps
date_range = pd.to_datetime(date_range)
likelihood = st.sidebar.multiselect("Select Likelihood", options=df["Likelihood"].unique(), default="Mid")


# Function to filter data based on selection
def filter_data(df, entity, date_range) -> pd.DataFrame:
    """
    Filters the data based on the selected entity, date range, and likelihood.

    Args:
    df (pd.DataFrame): The original DataFrame.
    entity (list): List of selected entities.
    date_range (tuple): Tuple containing the start and end date.
    likelihood (list): List of selected likelihoods.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    if entity:
        df = df[df["Entity"].isin(entity)]
    if not date_range.empty:
        df = df[(df["Date"] >= date_range[0]) & (df["Date"] <= date_range[1])]
    if likelihood:
        df = df[df["Likelihood"].isin(likelihood)]
    return df


def plot_stacked_area(df: pd.DataFrame, rate_stream: str) -> alt.Chart:
    """
    Creates a stacked area chart for the specified rate stream.

    Args:
    df (pd.DataFrame): The csv loaded as a dataframe with wells and forecasts.
    rate_stream (str): Oil Rate, Form Gas Rate, or Water Rate

    Returns:
    alt.Chart: The Altair chart object.
    """
    if df.empty:
        return None
    chart = (
        alt.Chart(df)
        .mark_area()
        .encode(
            x="Date:T",
            y=alt.Y(f"{rate_stream}:Q", stack=True),
            color="Entity:N",
            tooltip=["Entity", rate_stream, "Date"],
        )
        .interactive()
        .properties(width=2500, height=1000)
    )
    return chart


filtered_df = filter_data(df, entity, date_range)


if not filtered_df.empty:
    st.title("Oil Forecasts")
    st.altair_chart(plot_stacked_area(filtered_df, "Oil Rate"), use_container_width=True)
    st.title("Gas Forecasts")
    st.altair_chart(plot_stacked_area(filtered_df, "Form Gas Rate"), use_container_width=True)
    st.title("Water Forecasts")
    st.altair_chart(plot_stacked_area(filtered_df, "Water Rate"), use_container_width=True)
else:
    st.write("No data to display. Please select different filters.")
