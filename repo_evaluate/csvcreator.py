"""
This module deals with the creation of a raw CSV for later grading (externally)
"""
import csv


def initialise(headers):
    """
    This function is used to create and write the headers of a new CSV file

    :param headers: List of strings representing the headers of the CSV file
    :type headers: list of str
    :return: None
    :rtype: None
    """
    with open('./repo_evaluate/results/result.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)


def add(data):
    """
       This function is used to add a row of data to an existing CSV file

       :param data: List of strings representing the data to be added to the CSV file
       :type data: list of str
       :return: None
       :rtype: None
    """
    with open('./repo_evaluate/results/result.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)
