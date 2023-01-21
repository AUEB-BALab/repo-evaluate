import os

from github import Github

import testing
import contributing
import licence
import readme
import build
import features
from grades import *

g = Github(os.environ['GITHUB_GPG_KEY'])


# Gets GitHub repositories from a file. Returns them as a list of strings
def get_repo_addresses(file_location):
    with open(file_location) as fp:
        contents = fp.read()
    return contents.splitlines()


if __name__ == '__main__':
    repos = get_repo_addresses("resources/GitHub Repositories.txt")
    print("[INFO] Scraping GitHub. This might take some time!")
    print("[INFO]   Progress: 0%")
    grades = initialise_grade_dictionary(repos)
    print("[INFO]   Progress: 10%")
    READMES = readme.get_decoded_readmes(repos)
    print("[INFO]   Progress: 20%")
    RAW_READMES = readme.get_raw_readmes(repos)
    print("[INFO]   Progress: 30%")
    LICENCE_FILES = licence.get_licence_files(repos)
    print("[INFO]   Progress: 40%")
    CONTRIBUTING_FILES = contributing.get_contributing_files(repos)
    print("[INFO]   Progress: 50%")
    BUILD_FILES, BUILD_TOOLS = build.get_build_files(repos)
    print("[INFO]   Progress: 70%")
    JAVA_NON_TEST_COUNT, JAVA_TEST_COUNT = testing.get_java_file_count(repos)
    print("[INFO]   Progress: 90%")
    print("[INFO]   Progress: 100%")

    # This loop will determine all the Repos in GitHub Repositories.txt grades
    for repo in repos:
        print(f"[INFO] Now evaluating: {repo}")
        # Evaluate README
        if READMES[repo] is not None:
            grades[repo] = grade_update(grades[repo], 'README', README)

            # Evaluate big README extra credit
            if len(READMES[repo]) > BIG_README_SIZE:
                grades[repo] = grade_update(grades[repo], 'BIG_README', BIG_README)

            # Evaluate README markdown usage for extra credit
            if len(READMES[repo]) > FACTOR_README_MARKDOWN * len(RAW_READMES[repo]):
                grades[repo] = grade_update(grades[repo], 'README_USES_MARKDOWN', README_USES_MARKDOWN)

        # Evaluate LICENCE file
        if LICENCE_FILES[repo] is not None:
            grades[repo] = grade_update(grades[repo], 'LICENCE_FILE', LICENCE_FILE)

        # Evaluate CONTRIBUTING file
        if CONTRIBUTING_FILES[repo] is not None:
            grades[repo] = grade_update(grades[repo], 'CONTRIBUTING_FILE', CONTRIBUTING_FILE)

        # Evaluate package
        if BUILD_TOOLS[repo] is not None:  # does a build file exist?
            # We use the percent of the file existing times the points packaging gets
            grades[repo] = grade_update(grades[repo], 'BUILD_EXISTS', EXISTENCE_OF_BUILD_FILE * PACKAGING)

            match BUILD_TOOLS[repo]:
                case "Maven":
                    if build.validate_maven_pom(str(BUILD_FILES[repo]), "./resources/maven-4.0.0.xsd"):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
                case "Gradle - Groovy":
                    if build.validate_groovy_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
                case "Gradle - Kotlin":
                    if build.validate_kotlin_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)

        # evaluate testing
        # evaluate test file existence
        if JAVA_TEST_COUNT[repo] > 0:
            grades[repo] = grade_update(grades[repo], 'TESTING_EXISTENCE', TESTING_EXISTENCE * TESTING)
        # find test ratio
        testing_ratio = testing.find_test_ratio(JAVA_TEST_COUNT[repo], JAVA_NON_TEST_COUNT[repo])
        if testing_ratio == -1:
            print(f"[WARNING] {repo} has no java files! That's an issue!")
        # evaluate test raio
        if testing_ratio > 0.25:
            grades[repo] = grade_update(grades[repo], 'TESTING_COVERAGE', TESTING_COVERAGE * TESTING)
        else:
            grades[repo] = grade_update(grades[repo], 'TESTING_COVERAGE', 0)

        # Evaluate use of GitHub features
        result = features.repo_uses_github_features(repo)
        if result:
            grades[repo] = grade_update(grades[repo], 'GITHUB_FEATURES', GITHUB_FEATURES)
        else:
            grades[repo] = grade_update(grades[repo], 'GITHUB_FEATURES', 0)

        # finalise grades (sum low level modules to high level modules)
        grades[repo] = finalise_grades(grades[repo])

    for repo in repos:
        print(f"[INFO] Now creating result file for: {repo}")
        path = f"./results/{repo}"
        if not os.path.exists(path):
            os.makedirs(path)
        create_grade_file(grades, repo, BUILD_TOOLS[repo])
