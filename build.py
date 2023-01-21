"""
This module defines all methods which deal with BUILDS
"""
import os
import subprocess

from github import Github
from github.GithubException import UnknownObjectException
from lxml import etree
from lxml.etree import XMLSyntaxError

from search import search_name_matches

g = Github(os.environ['GITHUB_GPG_KEY'])


def get_a_build_file(repo_address):
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


# Validates if a given xml follows the Maven XSD
def validate_maven_pom(xml_string: str, maven_xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(maven_xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    try:
        xml_doc = etree.fromstring(xml_string.encode())
        result = xmlschema.validate(xml_doc)
    except XMLSyntaxError:
        result = False
    return result


# Takes a string and a Path. If the path doesn't exist it creates it. Then it saves the string to the path file
def save_string_to_file(text, file_path):
    dir = os.path.dirname(file_path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(file_path, "w") as f:
        f.write(text)


def get_current_path():
    current_path = os.path.abspath(__file__)
    # The program name is main.py which is 9 characters w/ the last 2 backslashes. We don't want them
    current_path = current_path.strip()[:-8]
    # The backslashes are literals, so we prefer front slashes
    # Also, the gits are defined with forward slashes, so we want to keep consistency
    current_path = current_path.replace("\\", '/')
    return current_path


# Runs a gradle task in the specified path. the task is parsed via the task argument
def run_gradle_task(task, gradle_project_path):
    # We structure the command
    gradle_command = f"gradle {task} -p '{gradle_project_path}'"
    # We send it to run via powershell and wait for an answer
    result = subprocess.run(["powershell.exe", "-Command", gradle_command], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return result


def gradle_build_failure(repo, standard_error):
    print(f"[WARNING] {repo} BUILD FAILED. More info in results")
    path = f"./results/{repo}"
    if not os.path.exists(path):
        os.makedirs(path)
    with open(f"./results/{repo}/gradle_build_failure_info.txt", 'w+') as fp:
        fp.write(repo)
        fp.write("\n\n[WARNING] Build failed:")
        fp.write("\n")
        fp.write(standard_error)


# Returns true if a groovy build is valid
def validate_groovy_build(build_file_string, repo):
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
def validate_kotlin_build(build_file_string, repo):
    working_dir = get_current_path()
    # We save the Gradle file to a folder in our resources
    save_string_to_file(build_file_string, f"{working_dir}/resources/Gradle Builds/{repo}/build.gradle.kts")
    # We then try to run a gradle task with that build
    result = run_gradle_task("build", f"{working_dir}/resources/Gradle Builds/{repo}/")
    # The only thing we care about is if the gradle task succeeded
    if result.returncode != 0:
        gradle_build_failure(repo, result.stderr.decode("utf-8"))
    return result.returncode == 0
