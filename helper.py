import csv
import time
from itertools import groupby

def csv_dict_aggregator(my_data, groupby_key):
    """ Aggregate the count based on the value of a field in this list of dictionaries

        Args:
            my_data (list of dictionary): input data
            groupby_key (string): The field we want to aggregate on

        Returns:
            Dictionary of scores

    """
    result_dict = {}
    for key, group in groupby(my_data, lambda x:x[groupby_key]):
        if key not in result_dict.keys():
            result_dict[key] = len(list(group))
        else:
            result_dict[key] += len(list(group))

    return result_dict

def format_token(my_tokens):
    """Clean up the tokens by removing punctuation (single length character) and lower case each terms

        Args: 
            my_tokens (string): raw input 

        Returns:
            list of terms (list of string)


    """
    #lower token and remove punctuation
    return [word.lower()  for word in my_tokens.split(" ")  if (len(word) > 1)]

def read_school_csv(csv_path):
    """ Helper function to read school csv file.  Since the file is for states that starts from A to I, we are going to drop off some bad data 

        Args:
            csv_path (string): path to the csv file

        Return:
            List of school documents 

    """
    output = []

    #We are opening the file with latin1 encoding to get around the non-ascii/utf-8 character
    with open(csv_path, encoding='latin1') as csv_file:
        output = csv.DictReader(csv_file, delimiter=',')
        #there are few bad data that we want to remove
        my_list_output = list(output)
        #['OR', 'NV', 'MD', 'C', 'OH']
        my_key_to_filter = [key for key, value in csv_dict_aggregator(my_list_output,"LSTATE05").items() if value==1]
        return list(filter(lambda x: x["LSTATE05"] not in my_key_to_filter,my_list_output ))