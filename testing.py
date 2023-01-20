"""
This module defines all methods which deal with testing
"""
import os
from typing import List, Dict
import copy
import search

from github import Github

g = Github(os.environ['GITHUB_GPG_KEY'])


# Gets all files which contain a .java extension
def get_java_file_names_from_repo(repo_addresses):
    global_java_file_names = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        files = search.search_name_contains(".java", repo)
        for file_name in files:
            if files[file_name] == 0:
                files.pop(file_name)
        global_java_file_names[address] = files
    return global_java_file_names


# Finds how many .java files a repository has (not test files)
def return_non_test_java_files(java_file_name_dict: Dict[str, str]):
    java_file_names = list(java_file_name_dict.keys())
    for file in java_file_names:
        if ("test" in file) or ("Test" in file):
            java_file_name_dict.pop(file)
    return java_file_name_dict


# Finds how many test .java files a repository has
def return_test_java_files(java_file_name_dict: Dict[str, str]):
    java_file_names = list(java_file_name_dict.keys())
    for file in java_file_names:
        if ("test" in file) or ("Test" in file):
            pass
        else:
            java_file_name_dict.pop(file)
    return java_file_name_dict


# Returns a tuple with a dictionairy of the count of test and non-test java files as keys
# and the size of the files as values to the keys
def get_java_file_count(repo_addresses: List[str]):
    java_file_names = get_java_file_names_from_repo(repo_addresses)
    non_test_files_count = {}
    test_files_count = {}
    for repo in repo_addresses:
        all_files = java_file_names[repo]
        non_test_files_count[repo] = len(return_non_test_java_files(copy.deepcopy(all_files)))
        test_files_count[repo] = len(return_test_java_files(copy.deepcopy(all_files)))
    return non_test_files_count, test_files_count


# Finds the test ratio of a repository
def find_test_ratio(num_test_files: int, num_of_non_test_java_files: int) -> float:
    test_ratio = -1.0
    try:
        test_ratio = num_test_files / num_of_non_test_java_files
    except ZeroDivisionError:
        pass
    finally:
        return round(test_ratio, 2)
