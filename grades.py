"""
This module defines all methods which deal with grading the assignment
"""
from constants import *
import features


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
        for module in FINAL_MODULES:
            grade_dict[repository] = grade_update(grade_dict[repository], module, 0)

    return grade_dict


# Function calculates finalises grades
# Some grades are combined so this function dose the combination
def finalise_grades(grade_module_dict):
    # Create top modules which are partly graded
    grade_module_dict['PACKAGING'] = grade_module_dict['BUILD_EXISTS'] + grade_module_dict['BUILD_FILE_OK']
    grade_module_dict['TESTING'] = grade_module_dict['TESTING_EXISTENCE'] + grade_module_dict['TESTING_COVERAGE']
    grade_module_dict['COMMENTING'] = round(grade_module_dict['COMMENTING_METHOD_COVERAGE'] + grade_module_dict[
        'COMMENTING_LINE_COVERAGE'], 2)

    # factor grades in acordance to top mark
    for module in grade_module_dict:
        grade_module_dict[module] *= TOP_MARK
    return grade_module_dict


# Creates a grade file. File contains all grades and a total.
# In a clean layout to make it clear how it was graded
def create_grade_file(grade_dict, repo, build):
    total = 0
    for module in FINAL_MODULES:
        total += grade_dict[repo][module]
    total = round(total, 3)

    # Bonuses might make the final grade over the top mark
    if total > TOP_MARK:
        total = TOP_MARK

    with open(f"./results/{repo}/results.txt", 'w+') as fp:
        fp.write(repo)
        fp.write("\nGrades:")
        for module in TOP_MODULES:
            fp.write(f"\n{module}:{round(grade_dict[repo][module], 2)}/{str(globals()[module] * TOP_MARK)}")

        fp.write(f"\n\nPACKAGING was evaluated from:\n"
                 f" -BUILD_EXISTS:{grade_dict[repo]['BUILD_EXISTS']}/{str(EXISTENCE_OF_BUILD_FILE * PACKAGING * TOP_MARK)}\n"
                 f" -BUILD_FILE_OK:{grade_dict[repo]['BUILD_FILE_OK']}/{str(FILE_IS_WELL_FORMED * PACKAGING * TOP_MARK)}")

        fp.write(f"\n\nTESTING was evaluated from:\n"
                 f" -TESTING_COVERAGE:{round(grade_dict[repo]['TESTING_COVERAGE'], 2)}"
                 f"/{str(TESTING_COVERAGE * TESTING * TOP_MARK)}\n"
                 f" -TESTING_EXISTENCE:{round(grade_dict[repo]['TESTING_EXISTENCE'], 2)}"
                 f"/{str(TESTING_EXISTENCE * TESTING * TOP_MARK)}")

        fp.write(f"\n\nCOMMENTING was evaluated from:\n"
                 f" -COMMENTING_METHOD_COVERAGE:{round(grade_dict[repo]['COMMENTING_METHOD_COVERAGE'], 2)}"
                 f"/{str(PERCENTAGE_LINES_PER_COMMENT * COMMENTING * TOP_MARK)}\n"
                 f" -COMMENTING_LINE_COVERAGE:{round(grade_dict[repo]['COMMENTING_LINE_COVERAGE'], 2)}"
                 f"/{str(PERCENTAGE_METHOD_PER_COMMENT * COMMENTING * TOP_MARK)}\n")

        fp.write("\n\nBonuses:")
        for module in BONUS_MODULES:
            fp.write(f"\n{module}:{grade_dict[repo][module]}")

        fp.write(f"\n\nTotal Grade:{str(total)}/{TOP_MARK}")

        if build != "Maven" and build is not None:
            # Warning if build is Gradle as issues with validation may occur
            fp.write(
                f"\n\n[WARNING] {build} was used to build this project. \n"
                "[WARNING] This might mean that the build file is incorrectly flagged as wrong\n"
                "[WARNING] (BUILD_FILE_OK:0). If you think this is the case please inform me!")
        elif build is None:
            # Warning if no build was detected as it might be ant or something else (renamed POM or build.gradle)
            fp.write(f"\n\n[WARNING] NOTHING was used to build this project. \n"
                     "[WARNING] If you think this is wrong please inform me!")

        if features.commit_count_ok(repo):
            pass
        else:
            fp.write("\n\n[WARNING] This Repository doesn't have enough commits ! \n"
                     "[WARNING] Please evaluate why!")

        if features.contributor_count_ok(repo):
            pass
        else:
            fp.write("\n\n[WARNING] This Repository doesn't have enough contributors ! \n"
                     "[WARNING] Please evaluate why!")
