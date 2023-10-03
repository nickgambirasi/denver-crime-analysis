"""
Developer Info
--------------
Developed By: Nicholas Gambirasi
Created On: 29 September 2023
Last Edited: 29 September 2023

Purpose
--------------
This file is an auxilary file for the Denver Crime project
that defines functions related to the collection and processing
of data
"""
import sys
import os
import shutil
from typing import List

from tqdm.auto import tqdm
import requests

import pandas as pd

from utils import validate
from settings import DATA_DIR
from custom_exceptions import UnsupportedFileTypeError

def collect_data() -> bool:

    """

    Function to collect the data from the link on the city of
    Denver website. Returns a boolean value indicating whether
    the data has been downloaded properly (True) or whether
    there was an error in the downloading process (False)

    """
    try:

        os.mkdir(DATA_DIR)

    except Exception as e:

        flag = validate(
            msg="Continuing will delete a non-empty data directory.\nContinue? [y/n]: ",
            strings={
                'accept': ['Y', 'y'],
                'reject': ['N', 'n']
            }
        )

        if flag:

            shutil.rmtree(DATA_DIR)
            os.mkdir(DATA_DIR)

        else: 

            sys.exit("User exit")

    # Link to the data download
    DATA_LINK: str = "https://www.denvergov.org/media/gis/DataCatalog/crime/csv/crime.csv"
    BLOCK_SIZE = 1024

    # Send a get request to download the data
    r = requests.get(DATA_LINK, stream=True)

    TOTAL = int(r.headers.get('content-length', 0)) // BLOCK_SIZE

    try:

        # iterate over the content and download it to `crime.csv`
        with open(os.path.join(DATA_DIR, 'crime.csv'), 'wb') as f:

            for data in tqdm(r.iter_content(BLOCK_SIZE), total=TOTAL, desc="Downloading"):

                f.write(data)

        return True

    except Exception as e:

        return False
    
def process_data(drop_columns: List[str]=None, handle_na: str=None, normalization: str=None, outfile_format: str='csv', fname="crime.csv") -> bool:

    """
    Utility function used to process data after it has been
    downloaded locally.
    
    Parameters
    ----------
     - `drop_columns`: a list of columns from the dataset
        that should be dropped during processing
     - `handle_na`: method for handling NaN/empty values
        in the dataframe (options are 'drop_row' or 'drop_col')
     - `normalization`: methods of normalizing the text
        data in the dataset (options are `upper` for uppercase
        and `lower` for lowercase)
     - `outfile_format`: format of output file (current options
        are `csv` and `parquet`)
    
    Returns
    ----------
     - `flag`: flag indicating whether or not the data processing
        was successfully completed
    """
    print("Processing data...")
    # read the donwloaded data in a pandas dataframe
    with open(os.path.join(DATA_DIR, fname), 'r') as f:    
        try:
            frame = pd.read_csv(os.path.join(DATA_DIR, fname), encoding=f.encoding)
        except Exception as e:
            print("There was an error opening the specified file")
            return False
        
    # print some basic information about the dataframe
    print(f"\nThis dataframe contains {len(frame)} observations with {len(frame.columns)} features")
    
    # assert that all of the sepcified columns are in the dataframe,
    # then drop them in place
    assert(
        drop_columns is None or set(drop_columns).issubset(set(frame.solumns))
    ), "drop_columns included a column name not present in dataframe"

    try:
        if drop_columns is not None:
            frame.drop(columns=drop_columns, inplace=True)
    except Exception as e:
        print("There was an error dropping the specified columns from the dataframe")
        return False
    
    # handle na values as specified by the user
    match handle_na:

        case 'drop_row':

            try:
                frame.dropna(axis=0, inplace=True)
            except Exception as e:
                print("There was an error dropping the rows that contain NaN values")
                return False
        
        case 'drop_column':
            
            try:
                frame.dropna(axis=1, inplace=True)
            except Exception as e:
                print("There was an error dropping the columns that contain NaN values")
                return False
        
        # default case: do nothing to the NA values, leave them as they are
        case _:

            pass

    # normalize the data as specified by user
    match normalization:

        case 'lower':
            try:
                # change the non-numeric data in the dataframe to lowercase
                frame = frame.applymap(lambda x: x.lower() if type(x) == str else x)
                
                # change the columns to lowercase
                frame.columns = [c.lower() for c in frame.columns]
            except Exception as e:
                print("There was an error converting the data to lowercase")
                return False

        case 'upper':
            try:
                # change the non-numeric data in the dataframe to uppercase
                frame = frame.applymap(lambda x: x.upper() if type(x) == str else x)

                # change the column names to uppercase
                frame.columns = [c.upper() for c in frame.columns]
            except Exception as e:
                print("There was an error converting the data to uppercase")
                return False

        case _:

            pass

    file_name = fname.split('.')[0]
    match outfile_format:

        case 'csv':

            # write the file to a csv format
            frame.to_csv(os.path.join(DATA_DIR, f"{file_name}_processed.csv"), index=False)

        case 'parquet':

            frame.to_parquet(os.path.join(DATA_DIR, f"{file_name}_processed.parquet"), index=False)

        case _:

            raise UnsupportedFileTypeError(f"File type `{outfile_format}` not supported, must be `csv` or `parquet`")
    
    return True