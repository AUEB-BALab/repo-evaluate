"""
This module defines all methods which deal with BUILDS
"""
import os
import subprocess
import re

from github import Github
from github.GithubException import UnknownObjectException
from lxml import etree
from lxml.etree import XMLSyntaxError

from search import search_name_matches

g = Github(os.environ["GITHUB_ACCESS_TOKEN"])


def get_a_build_file(repo_address):
    """
    Gets the build file and packaging_type for a repository
    :param repo_address: repository address in format 'author/name'
    :type repo_address: str
    :return: Tuple of (packaging_file, packaging_type)
    """
    # Get a repo
    repo = g.get_repo(repo_address)

    # look for build file in head of git
    try:
        # If the build is Maven this will not throw an exception
        packaging_file = repo.get_contents("pom.xml")
        packaging_type = "Maven"
        return (packaging_file, packaging_type)
    except UnknownObjectException:  # build is not Maven
        try:
            # If the build is Gradle /w Groovy this will not throw an exception
            packaging_file = repo.get_contents("build.gradle")
            packaging_type = "Gradle - Groovy"
            return (packaging_file, packaging_type)
        except UnknownObjectException:  # build is not Gradle /w Groovy or Maven
            # If the build is Gradle /w Kotlin this will not throw an exception
            try:
                packaging_file = repo.get_contents("build.gradle.kts")
                packaging_type = "Gradle - Kotlin"
                return (packaging_file, packaging_type)
            except UnknownObjectException:  # build is not Gradle or Maven
                pass  # We now move on to look for the file everywhere in the repository

    # If the build is Maven this will return a file
    packaging_file = search_name_matches("pom.xml", repo)
    if packaging_file is not None:
        packaging_type = "Maven"
    else:  # build is not Maven
        packaging_file = search_name_matches("build.gradle", repo)
        if packaging_file is not None:
            packaging_type = "Gradle - Groovy"
        else:  # build is not Gradle /w Groovy or Maven
            packaging_file = search_name_matches("build.gradle.kts", repo)
            if packaging_file is not None:
                packaging_type = "Gradle - Kotlin"
            else:  # build is not Gradle or Maven
                packaging_file = None
                packaging_type = None
    return (packaging_file, packaging_type)


def get_build_files(repo_addresses):
    """
    Gets build files of repos given as a list. Returns a tuple with the build_file dictionary
    and a build_tools Dictionary.

    :param repo_addresses: repositories in format ['author1/project1','author2/project2']
    :type repo_addresses: list
    :return: Tuple of build_files,build_tools
    | The build_files dictionary connects a repo address with its build file
    | The build_tools dictionary connects a repo address with its build tool
    """
    build_files = {}
    build_tools = {}
    for address in repo_addresses:
        contents, tool = get_a_build_file(address)
        build_tools[address] = tool
        if (contents is None):
            build_files[address] = None
        else:
            build_files[address] = contents.decoded_content.decode(
                'utf-8')  # We decode the content to bytes and then the bytes to UTF-8
    return build_files, build_tools


def validate_maven_pom(xml_string: str, maven_xsd_path: str) -> bool:
    """
    Validates if a given xml follows the Maven XSD.

    :param xml_string: the xml data
    :type xml_string: str
    :param maven_xsd_path: the path to the maven xsd
    :type maven_xsd_path: str
    :return: Weather It's valid or not
    :rtype: bool
    """
    xmlschema_doc = etree.parse(maven_xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    try:
        xml_doc = etree.fromstring(xml_string.encode())
        result = xmlschema.validate(xml_doc)
    except XMLSyntaxError:
        result = False
    return result


def save_string_to_file(text: str, file_path: str):
    """
    Takes a string and a Path to a file.
     If the path doesn't exist it creates it.
     Then it saves the string to the path file

    :param text: string we want to save
    :param file_path: path to the file (NOT A DIRECTORY!)
    :return: None
    """
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(file_path, "w") as f:
        f.write(text)


def get_current_path():
    """
         Gets the current path which the python program is executed in

        :return: Current path as string
    """
    current_path = os.path.abspath(__file__)
    # The program name is main.py which is 9 characters w/ the last 2 backslashes. We don't want them
    current_path = current_path.strip()[:-8]
    # The backslashes are literals, so we prefer front slashes
    # Also, the gits are defined with forward slashes, so we want to keep consistency
    current_path = current_path.replace("\\", '/')
    return current_path


#
def run_gradle_task(task: str, gradle_project_path: str):
    """
    Runs a gradle task in the specified path. The task is parsed via the task argument

    :param task: A gradle tast (Such as build)
    :param gradle_project_path: the path to the gradle project
    :return: CompletedProcess
    """
    # We structure the command
    gradle_command = f"gradle {task} -p '{gradle_project_path}'"
    # We send it to run via powershell and wait for an answer
    result = subprocess.run(["powershell.exe", "-Command", gradle_command], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return result


def gradle_build_failure(repo: str, standard_error: str) -> None:
    """
    Saves the standard_error from a Gradle build failure to a repository path in results

    :param repo: Repository address in format 'author/name'
    :param standard_error: Standard error from build in a human-readable format (ex. utf-8)
    :return: None
    """
    print(f"[WARNING] {repo} BUILD FAILED. More info in results")
    path = f"./repo_evaluate/results/{repo}"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"./repo_evaluate/results/{repo}/gradle_build_failure_info.txt", 'w+') as fp:
        fp.write(repo)
        fp.write("\n\n[WARNING] Build failed:")
        fp.write("\n")
        fp.write(standard_error)


# Returns true if a groovy build is valid
def validate_groovy_build(build_file_string: str, repo: str) -> bool:
    """
    Validates a Gradle Groovy build
    :param build_file_string: The Gradle build file
    :param repo: Repository address in format 'author/name'
    :return: Weather the build failed or not
    :rtype: bool
    """
    working_dir = get_current_path()
    # We save the Gradle file to a folder in our resources
    save_string_to_file(build_file_string, f"{working_dir}/resources/Gradle Builds/{repo}/build.gradle")
    # We then try to run a gradle task with that build
    result = run_gradle_task("build", f"{working_dir}/resources/Gradle Builds/{repo}/")
    # The only thing we care about is if the gradle task succeeded
    if result.returncode != 0:
        gradle_build_failure(repo, result.stderr.decode("utf-8"))
    return result.returncode == 0


# Returns true if a kotlin build is valid
def validate_kotlin_build(build_file_string: str, repo: str) -> bool:
    """
    Validates a Gradle Kotlin build
    :param build_file_string: The Gradle build file
    :param repo: Repository address in format 'author/name'
    :return: Weather the build failed or not
    :rtype: bool
    """
    working_dir = get_current_path()
    # We save the Gradle file to a folder in our resources
    save_string_to_file(build_file_string, f"{working_dir}/resources/Gradle Builds/{repo}/build.gradle.kts")
    # We then try to run a gradle task with that build
    result = run_gradle_task("build", f"{working_dir}/resources/Gradle Builds/{repo}/")
    # The only thing we care about is if the gradle task succeeded
    if result.returncode != 0:
        gradle_build_failure(repo, result.stderr.decode("utf-8"))
    return result.returncode == 0


def checkstyle_exists(build_file_string: str) -> bool:
    """
    This method takes a build file string as an input, and looks for 'checkstyle' decalration in it using a
    regular expression.
    It returns a Boolean value, True if the word 'checkstyle' is found, False otherwise.

    :param build_file_string: The build file string to be searched
    :type build_file_string: str
    :return: Boolean value indicating whether the word 'checkstyle' was found or not
    :rtype: bool
    """
    return not (re.search(r'checkstyle', build_file_string, re.IGNORECASE) is None)


def spotbugs_exists(build_file_string: str) -> bool:
    """
    This method takes a build file string as an input, and looks for 'spotbugs' declaration in it using a
    regular expression.
    It returns a Boolean value, True if the word 'spotbugs' is found, False otherwise.

    :param build_file_string: The build file string to be searched
    :type build_file_string: str
    :return: Boolean value indicating whether the word 'spotbugs' was found or not
    :rtype: bool
    """
    return not (re.search(r'spotbugs', build_file_string, re.IGNORECASE) is None)
