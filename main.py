import os

from github import Github

import licence
import readme
import build
from grades import *

g = Github(os.environ['GITHUB_GPG_KEY'])


# Gets GitHub repositories from a file. Returns them as a list of strings
def get_repo_addresses(file_location):
    with open(file_location) as fp:
        contents = fp.read()
    return contents.splitlines()


if __name__ == '__main__':
    repos = get_repo_addresses("resources/GitHub Repositories.txt")
    grades = initialise_grade_dictionary(repos)
    READMES = readme.get_decoded_readmes(repos)
    RAW_READMES = readme.get_raw_readmes(repos)
    LICENCE_FILES = licence.get_licence_files(repos)
    BUILD_FILES, BUILD_TOOLS = build.get_build_files(repos)
    # This loop will determine all the Repos in GitHub Repositories.txt grades
    for repo in repos:
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
        # Evaluate package
        if BUILD_TOOLS is not None:  # does a build file exist?
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
        grades[repo] = finalise_grades(grades[repo])

    for repo in repos:
        path = f"./results/{repo}"
        if not os.path.exists(path):
            os.makedirs(path)
        create_grade_file(grades, repo)
