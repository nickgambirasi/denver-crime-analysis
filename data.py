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

from tqdm.auto import tqdm
import requests

from utils import validate
from settings import DATA_DIR

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

        print(e)
        
        return False
    

    
if __name__ == "__main__":



    # test the data collection function
    if collect_data():

        print("Data collected successfully.")
    
    else:

        sys.exit("There was an error collecting the data")