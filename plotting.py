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

# import the custom validation loop
from utils import validate

# import plotting functions from plotting_utils
from plotting_utils import plot_crimes_by_month, plot_crimes_by_season, plot_crimes_by_type, plot_crimes_by_year, \
    plot_crimes_by_neighborhood

# import custom unsupported plot error
from custom_exceptions import UnsupportedPlotError

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

        - `crimes_by_type`: plots the counts of
            crimes that have been reported per crime type

        - `crimes_by_season`: plots the counts of crimes
            that have occurred in each season, beginning
            with winter 2018 and ending with fall 2023

        - `crimes_by_neighborhood`: plots the count of
            crimes that have occurred in each neighbor-
            hood over the course of data collection

    Arguments to be supported in the future:

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
    SUPPORTED_PLOTS = {"crimes_by_year", "crimes_by_month", "crimes_by_type", "crimes_by_season", "crimes_by_neighborhood"}
    if not set(kwargs.keys()).issubset(SUPPORTED_PLOTS):
        raise UnsupportedPlotError(f"Arguments contain an unsupported plot. Supported plots are {SUPPORTED_PLOTS}")
 
    # get the keyword argument values for the supported plots,
    # with the default being False if the keyword is not
    # included in kwargs
    crimes_by_year = kwargs.get("crimes_by_year", False)
    crimes_by_month = kwargs.get("crimes_by_month", False)
    crimes_by_type = kwargs.get("crimes_by_type", False)
    crimes_by_season = kwargs.get("crimes_by_season", False)
    crimes_by_neighborhood = kwargs.get("crimes_by_neighborhood", False)

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
        with open(os.path.join(DATA_DIR, 'crime_processed.csv'), 'r') as f:
            data = pd.read_csv(os.path.join(DATA_DIR, 'crime_processed.csv'), encoding=f.encoding)
            processed_flag = True

    except FileNotFoundError as e:
        # if we reach here, there doesn't exist a file called
        # 'crime_processed.csv` and we should try and read from
        # `crime.csv` instead

        try:
            with open(os.path.join(DATA_DIR, 'crime.csv'), 'r') as f:
                data = pd.read_csv(os.path.join(DATA_DIR, 'crime.csv'), encoding=f.encoding)

        except FileNotFoundError as e:
            print("Could not read from either `crime_processed.csv` or `crime.csv`")
            return False

    # At this point we should either have the data collected, or we should
    # have returned with a False flag that will error the execution of the
    # main `run.py` script. We can do a bit of preprocessing with the dates
    # in the data so that we can easily access the month and year data that
    # we will need for the plots
    if crimes_by_year:
        crimes_by_year_flag = plot_crimes_by_year(data=data, outfile_name="crimes_by_year")
        # this either plots what we're looking for and returns True, or errors and
        # returns false
        if not crimes_by_year_flag:
            print("There was an error plotting the number of crimes per year from the data")
            return False 
        
    if crimes_by_month:
        crimes_by_month_flag = plot_crimes_by_month(data=data, outfile_name="crimes_by_month", sort_months='year_order')

        if not crimes_by_month_flag:
            print("There was an error plotting the number of crimes per month from the data")
            return False
        
    if crimes_by_type:

        crimes_by_type_flag = plot_crimes_by_type(data=data, outfile_name="crimes_by_type")

        if not crimes_by_type_flag:
            print("There was an error plotting the number of crimes by type from the data")
            return False
        
    if crimes_by_season:

        by_season_flag = plot_crimes_by_season(data=data, outfile_name="crimes_by_season", season_order='year')

        if not by_season_flag:
            print("There was an error plotting the crimes count by season")
            return False
        
    if crimes_by_neighborhood:

        by_neighborhood_flag = plot_crimes_by_neighborhood(data=data, order_neighborhoods='alphabetical', outfile_name="crimes_by_neighborhood")

        if not by_neighborhood_flag:
            print("There was an error plotting the crime counts by neighborhood")
            return False
        
    return True