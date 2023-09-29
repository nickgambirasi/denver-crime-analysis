"""

Developer Info
--------------
Developed By: Nicholas Gambirasi
Created On: 29 September 2023
Last Edited: 29 September 2023

Purpose
-------------
This file is an auxilary file for the Denver Crime analysis project and
contains utility functions related to the project
"""

def validate(msg: str, strings: dict) -> bool:

    """
    Simple validation loop used for verifying that a user
    wants to continue with a process.
    
    Parameters
    -----------
     - `msg`: message displayed to the user when they're
        prompted for input

     - `strings`: user-defined strings that either accept
        or reject the input prompt...should be a dictionary
        with 'accept' and 'reject' as the keys, and the corresponding
        lists of accepting and rejecting strings as the values
    
    Returns
    -----------
     - `flag`: boolean indicating whether the user wants
        to continue or exit the process

    """
    
    # collect strings that reject and strings that accept
    ACCEPT_STRINGS = strings['accept']
    REJECT_STRINGS = strings['reject']

    # loop until user enters a correct choice
    while True:
        
        user_input = input(msg)

        if user_input in ACCEPT_STRINGS:

            return True
        
        elif user_input in REJECT_STRINGS:

            return False
        
        else:

            print(f"Your input `{user_input}` is not valid.\nPlease enter a valid input.")