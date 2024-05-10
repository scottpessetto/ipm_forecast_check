from datetime import timedelta
from typing import Any

import pandas as pd


def process_well_data(excel_file: str) -> pd.DataFrame:
    """
    Processes well data from an Excel file to calculate and append a new date column based on start dates and month offsets.

    Args:
        excel_file (str): The path to the Excel file containing the well forecasts and start dates

    Returns:
        pd.DataFrame: The forecast DataFrame with an additional 'Date' column containing the calculated dates for
        each month of the forecast.

    This function loads data from two sheets in the forecast file: 'start_dates' and 'forecast'.
    The start_dates is sheet with each well and its production start date.
    It maps well names to their respective start dates, calculates new dates by adding a month offset to these start dates,
    and appends these dates to the 'forecast' DataFrame.
    """
    # Load the workbook and the specific sheets
    print("Loading start dates")
    start_dates_sheet = pd.read_excel(excel_file, sheet_name="start_dates", skiprows=1)
    print("Loading forecasts")
    forecast_sheet = pd.read_excel(excel_file, sheet_name="forecast", skiprows=1)

    # Convert date columns to datetime
    start_dates_sheet["Start Date"] = pd.to_datetime(start_dates_sheet["Forecast Start Date"]).dt.normalize()

    # Create a dictionary to map well names to start dates
    print("Creating start dict")
    start_date_dict = dict(zip(start_dates_sheet["Entity"], start_dates_sheet["Start Date"]))

    # Initialize a new 'Date' column in forecast_sheet with NaN 
    forecast_sheet["Date"] = pd.NaT

    # Process the forecast data
    for index, row in forecast_sheet.iterrows():
        well_name = row["Entity"]
        print(well_name)
        if well_name in start_date_dict:
            start_date = start_date_dict[well_name]

            month_offset = pd.DateOffset(months=row["Month"] - 1)
            calculated_date = start_date + month_offset
            calculated_date = calculated_date.replace(day=1)
            forecast_sheet.at[index, "Date"] = calculated_date

    return forecast_sheet


# Usage
result = process_well_data("Forecast Inputs Template - April 2024 with H and J Development graphed temp.xlsx")
print(result)
result.to_csv("forecast_withdate.csv")
