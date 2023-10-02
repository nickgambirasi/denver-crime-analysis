"""

Developer Info
--------------
Developed By: Nicholas Gambirasi
Created On: 02 October 2023
Last Edited: 02 October 2023

Purpose
--------------
This file is the main executable file of the project. From this
file, procedures to collect data, process data, and generate
plots used in the technical report can be executed using the
command line
"""
# python libraries
from argparse import ArgumentParser
import sys

# custom exceptions
from custom_exceptions import ActionArgumentsException

# data functions
from data import collect_data, process_data

# argument parser for the command line
parser = ArgumentParser()


# the actions argument will store all possible actions that
# can be taken during execution of `run.py` in the command
# line. There are three possible steps that are taken for
# this project. This argument includes a parameter that will
# execute for all of them, so we will error out if more than
# two arguments are present, or if two arguments are present
# and one of them is the `all` argument.
parser.add_argument(
    '--actions',
    nargs='+', # should contain at least one argument
    choices=['collect', 'process', 'plot', 'all'],
    action='store',
    dest='actions',
    required=True,
    help='actions to be taken during execution'
)

# parse the arguments from the command line
args = parser.parse_args()
actions = args.actions

# evaluate the given actions and assert that validation criteria
# are met:
#   1) No more than two arguments present (use `all` to run all
#       processes)
#   2) `all` cannot be used in conjunction with other arguments

num_actions = len(actions)

# no more than two arguments can be present
if num_actions > 2:
    raise ActionArgumentsException("Expected no more than 2 action arguments. Please use the `all` argument to execute all possible actions")
# if two arguments are present, `all` cannot be one of them
elif num_actions == 2 and 'all' in actions:
    raise ActionArgumentsException("`all` cannot be included with other action arguments")

# given a list of arguments, pop the argument off of the list and
# execute the associated process
while actions:
    match actions.pop():
        # run data collection code
        case 'collect':
            flag = collect_data()
            if not flag:
                sys.exit("There was an error collecting the data")

        case 'process':
            flag = process_data()
            if not flag:
                sys.exit("There was an error processing the data")

        case 'plot':
            flag = plot_data()

        # include action argument for plotting data
        # and action argument for all actions

        case _:

            pass


