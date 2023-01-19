"""
This module defines all methods which deal with grading the assignment
"""
from constants import *


# Function takes the grade dictionary and updates it with the new grade added to a module
def grade_update(current_grade_dict, module, grade):
    current_grade_dict[module] = grade
    return current_grade_dict


# Function initialises the grade dictionary with all the module grades as 0
# As new gradings are added the modules will be updated
def initialise_grade_dictionary(github_repositories):
    grade_dict = {}
    for repository in github_repositories:
        grade_dict[repository] = {}
        for module in MODULES:
            grade_dict[repository] = grade_update(grade_dict[repository], module, 0)

    return grade_dict


# Function calculates finalises grades
# Some grades are combined so this function dose the combination
def finalise_grades(grade_module_dict):
    grade_module_dict['PACKAGING'] = grade_module_dict['BUILD_EXISTS'] + grade_module_dict['BUILD_FILE_OK']
    return grade_module_dict


# Creates a grade file. File contains all grades and a total.
# A better layout is needed FIXME
def create_grade_file(grade_dict, repo):
    total = 0
    for module in MODULES:
        total += grade_dict[repo][module]
    total = round(total, 2)
    with open(f"./results/{repo}/results.txt", 'w+') as fp:
        fp.write(str(grade_dict[repo]))
        fp.write("\n Total Grade:")
        fp.write(str(total))
