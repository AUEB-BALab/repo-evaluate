import os
import sys
import shutil

from github import Github

import continuous_integration
import csvcreator
import search
import testing
import contributing_scraper
import licence_scraper
import readme_scraper
import build
import code_quality
from grades import *

g = Github(os.environ['GITHUB_GPG_KEY'])


def get_repo_addresses(file_location: str) -> list[str]:
    """
    Gets GitHub repository addresses from a file. Returns them as a list of strings

    :param file_location: txt file which contains the GitHub repositories
    :return: Repository addresses in a list formatted as ['author1/name1', 'author2/name2'...]
    """
    with open(file_location) as fp:
        contents = fp.read()
    return contents.splitlines()


def copy_results_to_destination(destination_folder, source_folder="./repo_evaluate/results/"):
    """
    Copies a folder and all its subfolders and contents to a new directory.
    """
    try:
        # Check if the destination folder exists, if not, create it
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Walk through the source folder and copy files and sub-folders to the destination folder
        for root, dirs, files in os.walk(source_folder):
            for directory in dirs:
                source_dir = os.path.join(root, directory)
                destination_dir = os.path.join(destination_folder, os.path.relpath(source_dir, source_folder))
                if not os.path.exists(destination_dir):
                    os.makedirs(destination_dir)
            for file in files:
                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination_folder, os.path.relpath(source_file, source_folder))
                shutil.copy2(source_file, destination_file)

    except Exception as e:
        print("[ERROR] Something went wrong with result finalization. You can navigate to the "
              "result folder in the installation path to get the results manually")


def delete_result_folder_contents():
    """
    Deletes all files and subfolders within results exept .gitkeep.

    """

    try:
        # Iterate over all the files and subfolders in the folder
        for root, dirs, files in os.walk("./repo_evaluate/results/", topdown=False):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                # Check if the file has a .pdf extension
                if not file_name.lower().endswith('.gitkeep'):
                    # Delete the file
                    os.remove(file_path)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                # Delete the subfolder
                os.rmdir(dir_path)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    delete_result_folder_contents()
    repos = get_repo_addresses(sys.argv[1])
    print("[INFO] Scraping GitHub. This might take some time!")
    print("[INFO]   Progress: 0%")
    grades = initialise_grade_dictionary(repos)
    print("[INFO]   Progress: 10%")
    READMES = readme_scraper.get_decoded_readmes(repos)
    print("[INFO]   Progress: 20%")
    RAW_READMES = readme_scraper.get_raw_readmes(repos)
    print("[INFO]   Progress: 30%")
    LICENCE_FILES = licence_scraper.get_licence_files(repos)
    print("[INFO]   Progress: 40%")
    CONTRIBUTING_FILES = contributing_scraper.get_contributing_files(repos)
    print("[INFO]   Progress: 50%")
    BUILD_FILES, BUILD_TOOLS = build.get_build_files(repos)
    print("[INFO]   Progress: 70%")
    JAVA_NON_TEST_COUNT, JAVA_TEST_COUNT = testing.get_java_file_count(repos)
    print("[INFO]   Progress: 90%")
    CONTINUOUS_INTEGRATION = continuous_integration.repos_use_ci(repos)
    print("[INFO]   Progress: 100%")

    csvcreator.initialise(CSV_HEADERS)
    csv_list = []
    # This loop will determine all the Repos in GitHub Repositories.txt grades
    for repo in repos:
        java_files_exist = True
        csv_list.clear()
        csv_list.append(repo)

        print(f"[INFO] Now evaluating: {repo}")
        # Evaluate README
        if READMES[repo] is not None:
            grades[repo] = grade_update(grades[repo], 'README', README)
            csv_list.append(1)

            # Evaluate big README extra credit
            if len(READMES[repo]) > BIG_README_SIZE:
                grades[repo] = grade_update(grades[repo], 'BIG_README', BIG_README)
                csv_list.append(1)
            else:
                csv_list.append(0)

            # Evaluate README markdown usage for extra credit
            if len(READMES[repo]) > FACTOR_README_MARKDOWN * len(RAW_READMES[repo]):
                grades[repo] = grade_update(grades[repo], 'README_USES_MARKDOWN', README_USES_MARKDOWN)
                csv_list.append(1)
            else:
                csv_list.append(0)
        else:
            csv_list.append(0)
            csv_list.append(0)
            csv_list.append(0)

        # Evaluate LICENCE file
        if LICENCE_FILES[repo] is not None:
            grades[repo] = grade_update(grades[repo], 'LICENCE_FILE', LICENCE_FILE)
            csv_list.append(1)
        else:
            csv_list.append(0)

        # Evaluate CONTRIBUTING file
        if CONTRIBUTING_FILES[repo] is not None:
            grades[repo] = grade_update(grades[repo], 'CONTRIBUTING_FILE', CONTRIBUTING_FILE)
            csv_list.append(1)
        else:
            csv_list.append(0)

        # Evaluate package
        if BUILD_TOOLS[repo] is not None:  # does a build file exist?
            # We use the percent of the file existing times the points packaging gets
            grades[repo] = grade_update(grades[repo], 'BUILD_EXISTS', EXISTENCE_OF_BUILD_FILE * PACKAGING)
            csv_list.append(1)

            match BUILD_TOOLS[repo]:
                case "Maven":
                    if build.validate_maven_pom(str(BUILD_FILES[repo]), "repo_evaluate/resources/maven-4.0.0.xsd"):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
                        csv_list.append(1)
                    else:
                        csv_list.append(0)

                case "Gradle - Groovy":
                    if build.validate_groovy_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
                        csv_list.append(1)
                    else:
                        csv_list.append(0)

                case "Gradle - Kotlin":
                    if build.validate_kotlin_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
                        csv_list.append(1)
                    else:
                        csv_list.append(0)
        else:
            csv_list.append(0)  # NO BUILD FILE
            csv_list.append(0)  # obviously if it doesn't exist it's not correct...

        # evaluate testing
        # evaluate test file existence
        if JAVA_TEST_COUNT[repo] > 0:
            grades[repo] = grade_update(grades[repo], 'TESTING_EXISTENCE', TESTING_EXISTENCE * TESTING)
            csv_list.append(1)
        else:
            csv_list.append(0)

        # find test ratio
        testing_ratio = testing.find_test_ratio(JAVA_TEST_COUNT[repo], JAVA_NON_TEST_COUNT[repo])
        csv_list.append(JAVA_TEST_COUNT[repo])
        csv_list.append(JAVA_NON_TEST_COUNT[repo])
        if testing_ratio == -1:
            print(f"[WARNING] {repo} has no java files! That's an issue!")
            java_files_exist = False
        # evaluate test raio
        if testing_ratio > 0.25:
            grades[repo] = grade_update(grades[repo], 'TESTING_COVERAGE', TESTING_COVERAGE * TESTING)
        else:
            grades[repo] = grade_update(grades[repo], 'TESTING_COVERAGE', 0)

        # Evaluate use of GitHub features
        result = features.repo_uses_github_features(repo)
        if result:
            grades[repo] = grade_update(grades[repo], 'GITHUB_FEATURES', GITHUB_FEATURES)
            csv_list.append(1)
        else:
            grades[repo] = grade_update(grades[repo], 'GITHUB_FEATURES', 0)
            csv_list.append(0)

        if java_files_exist:
            # Evaluate Comments and Code quality (CheckStyle)
            # Get java file stats
            repo_non_test_java_files = search.search_name_contains_return_file('.java', "Test", repo)
            java_files_stats = code_quality.get_repository_java_files_stats(repo_non_test_java_files)
            method_number = 0
            method_coverage_avg = 0
            line_number = 0
            line_coverage_avg = 0
            comment_number = 0

            for java_file in java_files_stats:
                method_number += java_files_stats[java_file]['NUMBER_OF_METHODS']
                line_number += java_files_stats[java_file]['NUMBER_OF_LINES']
                comment_number += java_files_stats[java_file]['NUMBER_OF_COMMENTS']

                # Evaluate Comments
                (method_coverage_ok, line_coverage_ok) = code_quality.commenting_ok(java_files_stats[java_file])
                # Method Coverage
                if method_coverage_ok:
                    method_coverage_avg += 1
                else:
                    pass

                # Line Coverage
                if line_coverage_ok:
                    line_coverage_avg += 1
                else:
                    pass

            csv_list.append(comment_number)
            method_coverage_avg = method_coverage_avg / len(java_files_stats)
            grades[repo] = grade_update(grades[repo], 'COMMENTING_METHOD_COVERAGE',
                                        method_coverage_avg * PERCENTAGE_METHOD_PER_COMMENT * COMMENTING)

            csv_list.append(line_number)
            line_coverage_avg = line_coverage_avg / len(java_files_stats)
            grades[repo] = grade_update(grades[repo], 'COMMENTING_LINE_COVERAGE',
                                        line_coverage_avg * PERCENTAGE_LINES_PER_COMMENT * COMMENTING)

            csv_list.append(method_number)
            modularity = line_number / method_number
            if modularity < MODULARITY_AVG_METHOD_SIZE:
                grades[repo] = grade_update(grades[repo], 'MODULARITY', MODULARITY)
            else:
                grades[repo] = grade_update(grades[repo], 'MODULARITY', 0)



        else:
            grades[repo] = grade_update(grades[repo], 'COMMENTING_METHOD_COVERAGE', 0)
            csv_list.append(0)  # comments
            grades[repo] = grade_update(grades[repo], 'COMMENTING_LINE_COVERAGE', 0)
            csv_list.append(0)  # lines
            csv_list.append(0)  # methods

        if build.checkstyle_exists(str(BUILD_FILES[repo])):
            grades[repo] = grade_update(grades[repo], 'CHECKSTYLE', CHECKSTYLE)
            csv_list.append(1)
        else:
            grades[repo] = grade_update(grades[repo], 'CHECKSTYLE', 0)
            csv_list.append(0)

        if build.spotbugs_exists(str(BUILD_FILES[repo])):
            grades[repo] = grade_update(grades[repo], 'SPOTBUGS', SPOTBUGS)
            csv_list.append(1)
        else:
            grades[repo] = grade_update(grades[repo], 'SPOTBUGS', 0)
            csv_list.append(0)

        # Evaluate CI usage
        if CONTINUOUS_INTEGRATION[repo]:
            grades[repo] = grade_update(grades[repo], 'CI', CI)
            csv_list.append(1)
        else:
            grades[repo] = grade_update(grades[repo], 'CI', 0)
            csv_list.append(0)

        # finalise grades (sum low level modules to high level modules)
        grades[repo] = finalise_grades(grades[repo])

        # finalise CSV by adding row and some metadata
        tmprepo = g.get_repo(repo)
        csv_list.append(tmprepo.get_commits().totalCount)  # Commits total number
        csv_list.append(tmprepo.get_contributors().totalCount)  # Contributors total number
        csv_list.append(len(list(tmprepo.get_branches())))  # Branches total number
        csvcreator.add(csv_list)

    for repo in repos:
        print(f"[INFO] Now creating result file for: {repo}")
        path = f"./repo_evaluate/results/{repo}"
        if not os.path.exists(path):
            os.makedirs(path)
        create_grade_file(grades, repo, BUILD_TOOLS[repo])

    print("[INFO] Finalizing Results")
    copy_results_to_destination(sys.argv[2])
