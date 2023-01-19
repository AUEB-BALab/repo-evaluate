import os

from lxml.etree import XMLSyntaxError
import subprocess
from constants import *
from github import Github
from github.GithubException import UnknownObjectException
from lxml import etree
from bs4 import BeautifulSoup

g = Github("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")


# returns a GitHub build file
def get_a_build_file(repo_address):
    # Get a repo
    repo = g.get_repo(repo_address)
    try:
        # If the build is Maven this will not throw an exception
        packaging_file = repo.get_contents("pom.xml")
        packaging_type = "Maven"

    except UnknownObjectException:  # build is not Maven
        try:
            # If the build is Gradle /w Groovy this will not throw an exception
            packaging_file = repo.get_contents("build.gradle")
            packaging_type = "Gradle - Groovy"

        except UnknownObjectException:  # build is not Gradle /w Groovy or Maven
            # If the build is Gradle /w Kotlin this will not throw an exception
            try:
                packaging_file = repo.get_contents("build.gradle.kts")
                packaging_type = "Gradle - Kotlin"

            except UnknownObjectException:  # build is not Gradle or Maven
                packaging_file = None
                packaging_type = None

    return (packaging_file, packaging_type)


# Gets build files of repos given as a list. Returns a tuple with the build_file dictionary and a build_tool Dictionary
# The build_file dictionary connects a repo address with its build file
# The build_tool dictionary connects a repo address with its build tool
def get_build_files(repo_addresses) -> (str, str):
    build_files = {}
    build_tool = {}
    for address in repo_addresses:
        contents, tool = get_a_build_file(address)
        build_tool[address] = tool
        if (contents is None):
            build_files[address] = None
        else:
            build_files[address] = contents.decoded_content.decode(
                'utf-8')  # We decode the content to bytes and then the bytes to UTF-8
    return build_files, build_tool


# returns multiple GitHub repository readmes in a dictionary
def get_readmes(repo_addresses):
    readmes = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        try:
            readme_contents = repo.get_readme().decoded_content.decode('utf-8')
        except UnknownObjectException:
            readme_contents = None
        readmes[address] = readme_contents
    return readmes


# Validates if a given xml follows the Maven xsd
def validate_maven_pom(xml_string: str, maven_xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(maven_xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    try:
        xml_doc = etree.fromstring(xml_string)
        result = xmlschema.validate(xml_doc)
    except XMLSyntaxError:
        result = False
    return result


# Gets GutHub repositories from a file. Returns them a list of strings
def get_repo_addresses(file_location):
    with open(file_location) as fp:
        contents = fp.read()
    return contents.splitlines()


# Takes a string and a Path. If the path dosent exist it creates it. Then it saves the string to file
def save_string_to_file(text, file_path):
    dir = os.path.dirname(file_path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(file_path, "w") as f:
        f.write(text)


def get_current_path():
    current_path = os.path.abspath(__file__)
    # The program name is main.py which is 7 characters and the last 2 backslashes we don't need we remove them
    current_path = current_path.strip()[:-8]
    # The backslashes are literals, so we don't want them
    # Also, the gits are defined with forward slashes, so we need to keep consistency
    current_path = current_path.replace("\\", '/')
    return current_path


# Runs a gradle task in the spesified path. the task is parced via the task argument
def run_gradle_task(task, gradle_project_path):
    # We structure the command
    gradle_command = f"gradle {task} -p '{gradle_project_path}'"
    # We send it to run via powershell and wait for an answer
    result = subprocess.run(["powershell.exe", "-Command", gradle_command], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return result


# Returns true if a groovy_build is valid
def validate_groovy_build(build_file_string, repo):
    working_dir = get_current_path()
    # We save the Gradle file to a folder in our resources
    save_string_to_file(build_file_string, f"{working_dir}/resources/Gradle Builds/{repo}/build.gradle")
    # We then try to run a gradle task with that build
    result = run_gradle_task("build", f"{working_dir}/resources/Gradle Builds/{repo}/")
    return result.returncode == 0


# Returns true if a kotlin_build is valid
def validate_kotlin_build(build_file_string, repo):
    working_dir = get_current_path()
    # We save the Gradle file to a folder in our resources
    save_string_to_file(build_file_string, f"{working_dir}/resources/Gradle Builds/{repo}/build.gradle.kts")
    # We then try to run a gradle task with that build
    result = run_gradle_task("build", f"{working_dir}/resources/Gradle Builds/{repo}/")
    return result.returncode == 0


if __name__ == '__main__':
    repos = get_repo_addresses("resources/GitHub Repositories.txt")
    grades = {}
    READMES = get_readmes(repos)
    BUILD_FILES, BUILD_TOOLS = get_build_files(repos)
    # This loops will determine the grades
    for repo in repos:
        grades[repo] = 0
        # Evaluate README
        if READMES[repo] is not None:
            grades[repo] += README

            # Evaluate big README extra credit
            if len(READMES[repo]) > BIG_README_SIZE:
                grades[repo] += BIG_README

        # Evaluate package
        if BUILD_TOOLS is not None:  # does a build file exist?
            # We use the percent of the file existing times the points packaging gets
            grades[repo] += EXISTENCE_OF_BUILD_FILE * PACKAGING

            match BUILD_TOOLS[repo]:
                case "Maven":
                    if validate_maven_pom(str(BUILD_FILES[repo]), "./resources/maven-4.0.0.xsd"):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] += FILE_IS_WELL_FORMED * PACKAGING
                case "Gradle - Groovy":
                    if validate_groovy_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] += FILE_IS_WELL_FORMED * PACKAGING
                case "Gradle - Kotlin":
                    if validate_kotlin_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] += FILE_IS_WELL_FORMED * PACKAGING
        grades[repo] = round(grades[repo], 2)
        if grades[repo] > 10:
            grades[repo] = 10

    print(grades)
