"""
Developer Info
--------------
Developed By: Nicholas Gambirasi
Created On: 02 October 2023
Last Edited: 02 October 2023

Purpose
--------------
This file defines the functions related to plotting
the data to answer several questions related to the
crime data collected and processed.
"""
import os
import shutil
import sys

# pandas for data processing
import pandas as pd

# bokeh objects for generating plots
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.palettes import Bright6
from bokeh.io import export_png

# custom exceptions for error handling
from custom_exceptions import UnsupportedPlotError, NanException
from utils import validate

# settings
from settings import DATA_DIR, PLOTS_DIR

def plot_data(**kwargs) -> bool:

    """
    Function that creates the plots used in the 
    report to answer questions about the data.

    Parameters
    ----------
    Can take several keyword arguments, though
    none of them are required. They are all boolean
    variables, simply indicating whether or not
    the plots should be generated.

    Currently supported arguments:

        - `crimes_by_year`: plots the counts of crimes
            that took place in each year, beginning
            with 2018 and ending with 2023

        - `crimes_by_month`: plots the counts of crimes
            that took place in each month, beginning with
            January 2018 and ending with September 2023

    Arguments to be supported in the future:

        - `crimes_by_season`: plots the count of crimes
            that have occurred in each season, beginning
            with winter 2018 and ending with fall 2023

        - `crimes_by_neighborhood`: plots the count of
            crimes that have occurred in each neighbor-
            hood over the course of data collection

        - `county_crime_heatmap`: plots a count of the
            the selected crime (will require a dropdown)
            based on the county in Denver in which they
            occurred

        - `crime_map`: plots the specified crime type
            in the specified month or year on a map of
            the Denver metro area        
    """
    # here we either create a plots directory if none exists, or delete and recreate the
    # plots directory if the user is okay with it
    try:

        os.mkdir(PLOTS_DIR)

    except Exception as e:

        flag = validate(
            msg="Continuing will delete a non-empty plots directory.\nContinue? [y/n]: ",
            strings={
                'accept': ['Y', 'y'],
                'reject': ['N', 'n']
            }
        )

        if flag:

            shutil.rmtree(PLOTS_DIR)
            os.mkdir(PLOTS_DIR)

        else: 

            sys.exit("User exit")

    # define supported plots to verify that no extra arguments
    # are included
    SUPPORTED_PLOTS = {"crimes_by_year", "crimes_by_month"}
    if not set(kwargs.keys()).issubset(SUPPORTED_PLOTS):
        raise UnsupportedPlotError(f"Arguments contain an unsupported plot. Supported plots are {SUPPORTED_PLOTS}")
 
    # get the keyword argument values for the supported plots,
    # with the default being False if the keyword is not
    # included in kwargs
    crimes_by_year = kwargs.get("crimes_by_year", False)
    crimes_by_month = kwargs.get("crimes_by_month", False)

    # We try reading from the processed file first, if
    # the file exists, set a variable indicating that
    # we're working with a processed dataset to True.
    # If the file doesn't exist, try reading from the
    # unprocessed file next. If successful, set the
    # indicator to False, since the data has not been
    # processed. If unsuccessful, return False indicating
    # that there has been an error processing the file
    processed_flag: bool = False
    try:
        data = pd.read_csv(os.path.join(DATA_DIR, 'crime_processed.csv'))
        processed_flag = True

    except FileNotFoundError as e:
        # if we reach here, there doesn't exist a file called
        # 'crime_processed.csv` and we should try and read from
        # `crime.csv` instead

        try:
            data = pd.read_csv(os.path.join(DATA_DIR, 'crime.csv'))

        except FileNotFoundError as e:
            print("Could not read from either `crime_processed.csv` or `crime.csv`")
            return False

    # At this point we should either have the data collected, or we should
    # have returned with a False flag that will error the execution of the
    # main `run.py` script. We can do a bit of preprocessing with the dates
    # in the data so that we can easily access the month and year data that
    # we will need for the plots
    if crimes_by_year:
        flag = plot_crimes_by_year(data=data, outfile_name="crimes_by_year")
        # this either plots what we're looking for and returns True, or errors and
        # returns false
        if not flag:
            print("There was an error plotting the number of crimes per year from the data")
            return False 
    return True

def plot_crimes_by_year(data: pd.DataFrame, outfile_name: str) -> bool:

    """
    Function that plots the crime data by year. Takes
    no parameters, but returns a boolean flag indicating
    whether the data was plotted and the output file was
    saved or not
    """

    assert(
        "reported_date" in data.columns
    ), "column `reported_date` expected by not found in dataframe columns"

    data["reported_date"] = pd.to_datetime(data["reported_date"])

    try:
        # if we wish to plot the crime count by year, the `crime_year` column
        # must be created by grabbing a the year of the reported date
        data["crime_year"] = data["reported_date"].apply(lambda x: x.year)

        # we can quickly do a sanity check to ensure that there are no NaNs in
        # the collected crime year data
        num_year_nas = sum([int(x) for x in data["crime_year"].isna()])
        if num_year_nas:
            raise NanException("Collecting the years in which crimes occurred yielded NaN values")

        # collect the number of counts of crimes that occurred in each year
        crimes_by_year = dict(data["crime_year"].value_counts())

    except Exception as e:
        print("There was an error processing the data prior to plotting")
        return False
    
    try:
        # create data source for the bokeh plot which will be saved to the output directory
        source = ColumnDataSource(data=dict(years=list(crimes_by_year.keys()), counts=list(crimes_by_year.values()), color=Bright6))

        # build bokeh figure
        p = figure(
            y_range=(0, 90000),
            height=350,
            title="Number of Crimes Reported by Year",
            toolbar_location=None
        )

        # plot the data as a vertical bar...here we choose a single color vertical
        # bar that only includes the number of crimes, as separating by the crime type
        # would make the plot very noisy
        p.vbar(
            x="years",
            top="counts",
            width=0.9,
            color="color",
            # legend_field="years",
            source=source
        )

        # add some additional characteristics to the plot to improve the aesthetic
        p.xgrid.grid_line_color = None
        p.title.align = "center"
        # p.legend.orientation = "horizontal"
        # p.legend.location = "top_center"

    except Exception as e:
        print("There was an error greating the plot from the processed data")
        return False
    
    try:
        # save the file to the directory
        export_png(p, filename=os.path.join(PLOTS_DIR, f"{outfile_name}.png"))
        return True
    
    except Exception as e:
        print(e)
        print("There was an error saving the plot to the specified location")
        return False
    

    
