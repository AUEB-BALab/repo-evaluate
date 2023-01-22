import os

from github import Github

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
        java_files_exist = True

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
        else:
            grades[repo] = grade_update(grades[repo], 'GITHUB_FEATURES', 0)

        if java_files_exist:
            # Evaluate Comments and Code quality (CheckStyle)
            # Get java file stats
            repo_non_test_java_files = search.search_name_contains_return_file('.java', "Test", repo)
            java_files_stats = code_quality.get_repository_java_files_stats(repo_non_test_java_files)
            method_coverage_avg = 0
            line_coverage_avg = 0
            checkstyle_avg = 0

            for java_file in java_files_stats:
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

                # Evaluate Checkstyle
                if code_quality.style_ok(java_files_stats[java_file]):
                    checkstyle_avg += 1
                else:
                    pass

            method_coverage_avg = method_coverage_avg / len(java_files_stats)
            grades[repo] = grade_update(grades[repo], 'COMMENTING_METHOD_COVERAGE',
                                        method_coverage_avg * PERCENTAGE_METHOD_PER_COMMENT * COMMENTING)

            line_coverage_avg = line_coverage_avg / len(java_files_stats)
            grades[repo] = grade_update(grades[repo], 'COMMENTING_LINE_COVERAGE',
                                        line_coverage_avg * PERCENTAGE_LINES_PER_COMMENT * COMMENTING)

            checkstyle_avg = checkstyle_avg / len(java_files_stats)
            grades[repo] = grade_update(grades[repo], 'CHECKSTYLE',
                                        checkstyle_avg * CHECKSTYLE)
        else:
            grades[repo] = grade_update(grades[repo], 'COMMENTING_METHOD_COVERAGE', 0)
            grades[repo] = grade_update(grades[repo], 'COMMENTING_LINE_COVERAGE', 0)
            grades[repo] = grade_update(grades[repo], 'CHECKSTYLE', 0)

        # finalise grades (sum low level modules to high level modules)
        grades[repo] = finalise_grades(grades[repo])

    for repo in repos:
        print(f"[INFO] Now creating result file for: {repo}")
        path = f"./results/{repo}"
        if not os.path.exists(path):
            os.makedirs(path)
        create_grade_file(grades, repo, BUILD_TOOLS[repo])
