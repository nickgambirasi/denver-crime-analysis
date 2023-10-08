import os

import pandas as pd

# bokeh objects for generating plots
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.palettes import Bright6, Bokeh6
from bokeh.io import export_png

from math import pi

# custom exceptions for error handling
from custom_exceptions import UnsupportedPlotError, NanException

# plots directory from settings
from settings import PLOTS_DIR

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

    data["reported_date"] = pd.to_datetime(data["reported_date"], format='mixed')

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
        print("There was an error saving the plot to the specified location")
        return False
    
def plot_crimes_by_month(data: pd.DataFrame, outfile_name: str, sort_months: str = ['count_order', 'year_order']) -> bool:

    """
    Function that plots a vertical bar chart of 
    the crimes by month, with multiple colors in each
    bar corresponding to the year...returns a boolean
    flag indicating the the plot has been successfully
    generated
    """
    assert(
        "reported_date" in data.columns
    ), "column `reported_date` expected but not found in columns"

    data["reported_date"] = pd.to_datetime(data["reported_date"], format='mixed')

    try:
        # if we wish to plot the crime count by year, the `crime_year` column
        # must be created by grabbing a the year of the reported date
        data["crime_year"] = data["reported_date"].apply(lambda x: x.year)

        # we can quickly do a sanity check to ensure that there are no NaNs in
        # the collected crime year data
        num_year_nas = sum([int(x) for x in data["crime_year"].isna()])
        if num_year_nas:
            raise NanException("Collecting the years in which crimes occurred yielded NaN values")

        # repeat the previous process, but with the crime months

        # define month map
        MONTHS_MAP = {
            '1': 'jan',
            '2': 'feb',
            '3': 'mar',
            '4': 'apr',
            '5': 'may',
            '6': 'jun',
            '7': 'jul',
            '8': 'aug',
            '9': 'sep',
            '10': 'oct',
            '11': 'nov',
            '12': 'dec'
        }
        data["crime_month"] = data["reported_date"].apply(lambda x: x.month)
        data["crime_month"] = data["crime_month"].apply(lambda x: MONTHS_MAP[str(x)])

        num_month_nas = sum([int(x) for x in data["crime_month"].isna()])
        if num_month_nas:
            raise NanException("Collecting the months in which crimes occurred yielded NaN values")
        
        crimes_by_month = data["crime_month"].value_counts().to_dict()

        match sort_months:

            case 'count_order':
                # collect the total number of crimes in each month and order the keys
                ordered_months = sorted(crimes_by_month, key=lambda x: crimes_by_month[x])

            case 'year_order':

                ordered_months = list(MONTHS_MAP.values())

        # add the ordered keys
        for_plot = {
            'months': ordered_months
        }

        # we now iterate through the years of the crime data and get the crime
        # counts for each month in the order specified on the list
        for year in data["crime_year"].unique():

            year_crime_counts = data.query("crime_year == @year")["crime_month"].value_counts().to_dict()
            ordered_year_by_month_counts = []

            for month in ordered_months:

                ordered_year_by_month_counts.append(year_crime_counts.get(month, 0))

            for_plot.update({
                str(year): ordered_year_by_month_counts
            })

        # we now build the plot of crimes by month, with different colors for
        # each year
        years = sorted([str(x) for x in for_plot.keys() if x != 'months'])

    except Exception as e:
        print("There was an error processing the data prior to plotting")
        return False

    # we now build the plot of crimes by month, with different colors for
    # each year
    try:

        p = figure(
            x_range=ordered_months,
            y_range=(0, max(crimes_by_month.values()) + 10000),
            height=350,
            width=900,
            title="Crime Counts by Month",
            toolbar_location=None,
            tools="hover",
            tooltips="$name @months: @$name"
        )

        p.vbar_stack(years, x='months', width=0.9, color=Bokeh6, source=for_plot, legend_label=years)

        p.title.align="center"
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color=None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = pi/4

    except Exception as e:

        print("There was an error plotting the data")
        return False
    
    try:

        export_png(p, filename=os.path.join(PLOTS_DIR, f"{outfile_name}.png"))
    
    except Exception as e:

        print("There was an error saving the file to the specified location")
    
    return True

def plot_crimes_by_type(data: pd.DataFrame, outfile_name: str) -> bool:

    """
    Plots the number of crimes that occurred by the type of crime in
    the report...returns a boolean flag that indicates whether the
    data was plotted, or whether there were errors during the data
    processing and plotting process
    """

    assert(
        {"reported_date", "offense_type_id"}.issubset(set(data.columns))
    ), "columns `reported_date` and `offense_type_id` expected but not found in dataset"

    # here we convert the dates of the reported crimes into datetime objects so we
    # can grab important information from the date without having to split the date
    # into separate strings ourselves
    data["reported_date"] = pd.to_datetime(data["reported_date"], format='mixed')

    try:
        # collect the year of the reported crimes
        data["reported_year"] = data["reported_date"].apply(lambda x: x.year)

        # get the counts of crimes that occurred
        crime_counts = data["offense_category_id"].value_counts().to_dict()

        # order the crimes by the amount of reports
        ordered_crimes = sorted(crime_counts, key=lambda x: crime_counts[x])
        
        # create the data object used for plotting
        for_plot = {
            'crimes': ordered_crimes,
        }

        # iterate through the years in the dataset and collect the crimes counts by
        # year
        years = sorted(data["reported_year"].unique())

        for year in years:

            year_crime_counts = data.query("reported_year == @year")["offense_category_id"].value_counts().to_dict()

            ordered_year_crime_counts = []

            for crime in ordered_crimes:

                ordered_year_crime_counts.append(year_crime_counts.get(crime, 0))

            for_plot.update({
                str(year): ordered_year_crime_counts
            })

            str_years = [str(year) for year in years]

    except Exception as e:

        print("There was an error processing the data prior to plotting")
        return False
   
    try:

        p = figure(
            x_range=ordered_crimes,
            y_range=(0, max(crime_counts.values()) + 10000),
            height=350,
            width=1000,
            title="Crime Counts by Crime Type",
            toolbar_location=None
        )

        p.vbar_stack(
            str_years,
            x="crimes",
            width=0.9,
            color=Bokeh6,
            source=for_plot,
            legend_label=str_years
        )

        p.title.align="center"
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color=None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = pi/4

    except Exception as e:
        print("There was an error creating the plot for the data by crime type")
        return False
    
    try:

        export_png(p, filename=os.path.join(PLOTS_DIR, f"{outfile_name}.png"))

    except Exception as e:
        print("There was an error saving the plot to the specified directory")
        return False
    
    return True

def plot_crimes_by_season(data: pd.DataFrame, outfile_name: str, season_order: str=['year', 'frequency']) -> bool:

    """
    Function to plot the crime by the season of the year
    in which they occur. Returns a boolean flag indicating
    whether the plot was generated successfully, or if there
    were errors during the plotting process
    """
    # check that the necessary columns are in the data
    assert(
        'reported_date' in data.columns
    ), "column `reported_date` expected but not found in the dataframe"

    # convert the reported_date to a datetime object
    data["reported_date"] = pd.to_datetime(data["reported_date"], format='mixed')

    try:
        # collect the month and year reported of each crime
        data["reported_year"] = data["reported_date"].apply(lambda x: x.year)
        data["reported_month"] = data["reported_date"].apply(lambda x: x.month)

        # generate the reported season using the reportead month and the 
        # below month that maps the months to seasons:

        #   Dec - Feb -> Winter
        #   Mar - May -> Spring
        #   Jun - Aug -> Summer
        #   Sep - Nov -> Fall

        MONTH_TO_SEASON = {
            1: 'winter',
            2: 'winter',
            3: 'spring',
            4: 'spring',
            5: 'spring',
            6: 'summer',
            7: 'summer',
            8: 'summer',
            9: 'fall',
            10: 'fall',
            11: 'fall',
            12: 'winter'
        }
        
        data["reported_season"] = data["reported_month"].apply(lambda x: MONTH_TO_SEASON[x])

        # count the number of crimes that occur in each season and sort the seasons
        # as defined by the user
        crimes_by_season = data["reported_season"].value_counts().to_dict()

        match season_order:

            case 'year':

                ordered_seasons = ['winter', 'spring', 'summer', 'fall']

            case 'frequency':

                ordered_seasons = sorted(crimes_by_season, key=lambda x: crimes_by_season[x])

            case _:

                pass
            
        # create the plotted data by iterating through the years and the
        # ordered seasons, getting the counts of crimes for each season
        # by year
        for_plot = {
            'seasons': ordered_seasons
        }

        years = sorted(data["reported_year"].unique())

        for year in years:

            year_seasonal_crime = data.query("reported_year == @year")["reported_season"].value_counts().to_dict()

            ordered_season_crime_counts = []

            for season in ordered_seasons:

                ordered_season_crime_counts.append(year_seasonal_crime.get(season, 0))

            for_plot.update({
                str(year): ordered_season_crime_counts
            })

        str_years = [str(year) for year in years]

    except Exception as e:
        print("There was an error processing the data prior to plotting")
        return False
    
    # create the figure for saving to the image file
    try:

        p = figure(
            x_range=ordered_seasons,
            y_range=(0, max(crimes_by_season.values()) + 10000),
            height=350,
            title="Crime Counts by Season",
            toolbar_location=None
        )

        p.vbar_stack(
            str_years,
            x="seasons",
            width=0.9,
            color=Bokeh6,
            source=for_plot,
            legend_label=str_years
        )

        p.title.align="center"
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color=None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = pi/4

    except Exception as e:
        print("There was an error generating the plot of crime counts by season")
        return False
    
    # save the generated plot to the specified file location
    try:
        export_png(p, filename=os.path.join(PLOTS_DIR, f"{outfile_name}.png"))

    except Exception as e:
        print("There was an error saving the generated plot to the specified directory")
        return False
    
    return True

def plot_crimes_by_neighborhood(data: pd.DataFrame, order_neighborhoods: str=['frequency', 'alphabetical'], outfile_name=str) -> bool:

    """
    Function to plot the crimes that occurred by year in the neighborhood
    """
    assert(
        {'reported_date', 'neighborhood_id'}.issubset(set(data.columns))
    ), "columns `reported_date` and `neighborhood_id` expected but nor present in the dataframe"

    # convert the reported year into datetime format, then
    # collect the year of the crimes into its own column
    data["reported_date"] = pd.to_datetime(data["reported_date"], format="mixed")
    data["reported_year"] = data["reported_date"].apply(lambda x: x.year)

    # first count the total number of crimes that appear by neighborhood
    # then order the neighborhoods based on the method specified by the
    # user
    crime_counts_by_neighborhood = data["neighborhood_id"].value_counts().to_dict()

    match order_neighborhoods:

        case "frequency":

            ordered_neighborhoods = sorted(crime_counts_by_neighborhood, key=lambda x: crime_counts_by_neighborhood[x])

        case "alphabetical":

            ordered_neighborhoods = sorted(list(crime_counts_by_neighborhood.keys()))

        case _:

            pass

    # create the data used to build the bokeh plot, starting with the ordered neighborhoods
    for_plot = {
        'neighborhoods': ordered_neighborhoods,
    }
    try:
        # iterate through the years and get the counts by year for each neighborhood
        # in the ordered neighborhoods list
        for year in sorted(data["reported_year"].unique()):

            year_crimes = data.query("reported_year == @year")["neighborhood_id"].value_counts().to_dict()

            crime_counts_neighborhood_year = []

            for nhood in ordered_neighborhoods:

                crime_counts_neighborhood_year.append(year_crimes.get(nhood, 0))

            for_plot.update({
                str(year): crime_counts_neighborhood_year
            })
        
        years = [key for key in for_plot.keys() if key != 'neighborhoods']

    except Exception as e:
        print("There was an error processing the data prior to plotting")
        return False
    
    # create the figure for saving to the image file
    try:

        p = figure(
            x_range=ordered_neighborhoods,
            y_range=(0, max(crime_counts_by_neighborhood.values()) + 10000),
            height=350,
            width=1500,
            title="Crime Counts by Neighborhood",
            toolbar_location=None
        )

        p.vbar_stack(
            years,
            x="neighborhoods",
            width=0.9,
            color=Bokeh6,
            source=for_plot,
            legend_label=years
        )

        p.title.align="center"
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xgrid.grid_line_color=None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"
        p.xaxis.major_label_orientation = pi/4

    except Exception as e:
        print("There was an error generating the plot of crime counts by season")
        return False
    
    # save the generated plot to the specified file location
    try:
        export_png(p, filename=os.path.join(PLOTS_DIR, f"{outfile_name}.png"))

    except Exception as e:
        print("There was an error saving the generated plot to the specified directory")
        return False
    
    return True

def plot_crime_heatmap_by_county(data: pd.DataFrame, outfile_name: str) -> bool:

    """
    Function that plots the crimes on a heatmap by county
    """