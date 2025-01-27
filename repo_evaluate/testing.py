"""
This module defines all methods which deal with testing
"""
import os
from typing import List, Dict
import copy
import search

from github import Github

g = Github(os.environ["GITHUB_ACCESS_TOKEN"])


def get_java_file_names_from_repo(repo_addresses: list[str]) -> dict[str, dict[str, int]]:
    """
    Gets all files which contain a .java extension and are not empty

    :param repo_addresses: Repository addresses in a list formatted as ['author1/name1', 'author2/name2'...]
    :return: A dictionairy of dictionary. The high level dictionary point from repository addresses to the java file
        dictionairy. The low level dictionairy points from java file name to java file size
    """
    global_java_file_names = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        files = search.search_name_contains_return_size(".java", repo)
        for file_name in files:
            # pops empty files
            if files[file_name] == 0:
                files.pop(file_name)
        global_java_file_names[address] = files
    return global_java_file_names


#
def return_non_test_java_files(java_file_name_dict: Dict[str, int]) -> Dict[str, int]:
    """
    Removes test files from java file dictionairy

    :param java_file_name_dict: The dictionairy of files from file name to size
    :return: the dictionary without test files
    """
    java_file_names = list(java_file_name_dict.keys())
    for file in java_file_names:
        if ("test" in file) or ("Test" in file):
            java_file_name_dict.pop(file)
    return java_file_name_dict


def return_test_java_files(java_file_name_dict: Dict[str, int]) -> Dict[str, int]:
    """
    Keeps only test files from a java file dictionairy

    :param java_file_name_dict: The dictionairy of files from file name (string) to size (int)
    :return: the dictionary without test files
    """
    java_file_names = list(java_file_name_dict.keys())
    for file in java_file_names:
        if ("test" in file) or ("Test" in file):
            pass
        else:
            java_file_name_dict.pop(file)
    return java_file_name_dict


def get_java_file_count(repo_addresses: List[str]) -> tuple[dict[str, int], dict[str, int]]:
    """
    Returns a two element tuple with a dictionairy of the repository addresses as keys
    and the count of .java files as the value (first tuple element non-test files, second tuple element test files)

    param repo_addresses: Repository addresses in a list formatted as ['author1/name1', 'author2/name2'...]
    :return: A tuple (dict1, dict2) where dict1 is a dictionairy with non-java file count and dict2 is a dictionairy
        only with test java file count. Both connect repository addresses to the respective counts
    """

    java_file_names = get_java_file_names_from_repo(repo_addresses)
    non_test_files_count = {}
    test_files_count = {}
    for repo in repo_addresses:
        all_files = java_file_names[repo]
        non_test_files_count[repo] = len(return_non_test_java_files(copy.deepcopy(all_files)))
        test_files_count[repo] = len(return_test_java_files(copy.deepcopy(all_files)))
    return non_test_files_count, test_files_count


def find_test_ratio(num_test_files: int, num_of_non_test_java_files: int) -> float:
    """
    Finds the test ratio of a repository

    :param num_test_files: The number of test files
    :param num_of_non_test_java_files: The number of non test files
    :return: Returns the ratio of normal to test files or -1 if no test files exist
    """
    test_ratio = -1.0
    try:
        test_ratio = num_test_files / num_of_non_test_java_files
    except ZeroDivisionError:
        pass
    finally:
        return round(test_ratio, 2)
