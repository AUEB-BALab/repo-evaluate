import os

from lxml.etree import XMLSyntaxError
import subprocess
from constants import *
from github import Github
from github.GithubException import UnknownObjectException
from lxml import etree
import re

g = Github(os.environ['GITHUB_GPG_KEY'])


# Looks for a pom file everywhere in a repository as POM files were found to not bee in the top DIR
def search_github_repo(file_name, repo):
    # recursively searching all the directories
    def search_directory(directory):
        contents = repo.get_contents(directory)
        for content in contents:
            if content.type == "dir":
                file_content = search_directory(content.path)
                if file_content is not None:
                    return file_content
            elif content.name == file_name:
                # get the contents of the file
                file_content = repo.get_contents(content.path)
                return file_content

    return search_directory('')


def get_a_build_file(repo_address):
    # Get a repo
    repo = g.get_repo(repo_address)
    # If the build is Maven this will not throw an exception
    packaging_file = search_github_repo("pom.xml", repo)
    if packaging_file is not None:
        packaging_type = "Maven"
    else:  # build is not Maven
        packaging_file = search_github_repo("build.gradle", repo)
        if packaging_file is not None:
            packaging_type = "Gradle - Groovy"
        else:  # build is not Gradle /w Groovy or Maven
            packaging_file = search_github_repo("build.gradle.kts", repo)
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


# returns multiple GitHub repository readmes in a dictionary. Data is decoded!
def get_decoded_readmes(repo_addresses):
    readmes = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        try:
            readme_contents = repo.get_readme().decoded_content.decode('utf-8')  # decode to uts-8
        except UnknownObjectException:
            readme_contents = None
        readmes[address] = readme_contents
    return readmes


# returns multiple GitHub repository readmes in a dictionary. Data is raw!
def get_raw_readmes(repo_addresses):
    readmes = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        try:
            readme_contents = repo.get_readme().decoded_content.decode()  # decode
            # remove Markdown elements using regular expressions
            readme_contents = re.sub(r'[#*_`]', '', readme_contents)
            # remove Markdown links
            readme_contents = re.sub(r'\[.*\]\(.*\)', '', readme_contents)
            # remove Markdown images
            readme_contents = re.sub(r'!\[.*\]\(.*\)', '', readme_contents)
            # remove Markdown headings
            readme_contents = re.sub(r'^#.*', '', readme_contents, flags=re.MULTILINE)
        except UnknownObjectException:
            readme_contents = None
        readmes[address] = readme_contents
    return readmes


# Validates if a given xml follows the Maven XSD
def validate_maven_pom(xml_string: str, maven_xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(maven_xsd_path)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    try:
        xml_doc = etree.fromstring(xml_string)
        result = xmlschema.validate(xml_doc)
    except XMLSyntaxError:
        result = False
    return result


# Gets GitHub repositories from a file. Returns them as a list of strings
def get_repo_addresses(file_location):
    with open(file_location) as fp:
        contents = fp.read()
    return contents.splitlines()


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


# Returns true if a groovy build is valid
def validate_groovy_build(build_file_string, repo):
    working_dir = get_current_path()
    # We save the Gradle file to a folder in our resources
    save_string_to_file(build_file_string, f"{working_dir}/resources/Gradle Builds/{repo}/build.gradle")
    # We then try to run a gradle task with that build
    result = run_gradle_task("build", f"{working_dir}/resources/Gradle Builds/{repo}/")
    # The only thing we care about is if the gradle task succeeded
    if result.returncode != 0:
        print(repo)
        print(result.stderr.decode("utf-8"))
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
        print(repo)
        print(result.stderr.decode("utf-8"))
    return result.returncode == 0


# Function takes the grade dictionary and updates it with the new grade added to a module
def grade_update(current_grade_dict, module, grade):
    current_grade_dict[module] = grade
    return current_grade_dict


# Function initialises the grade dictionary with all the module grades as 0
# As new gradings are added the modules will be updated
def initialise_grade_dictionairy(github_repositories):
    grade_dict = {}
    modules = ['README', 'BIG_README', 'README_USES_MARKDOWN', 'BUILD_EXISTS', 'BUILD_FILE_OK']
    for repository in github_repositories:
        grade_dict[repository] = {}
        for module in modules:
            grade_dict[repository] = grade_update(grade_dict[repository], module, 0)

    return grade_dict


# Function calculates finalises grades
#Some grades are combined so this function dose the combination
def finalise_grades(grade_module_dict):
    grade_module_dict['PACKAGING'] = EXISTENCE_OF_BUILD_FILE * grade_module_dict[
        'BUILD_EXISTS'] + FILE_IS_WELL_FORMED * grade_module_dict['BUILD_FILE_OK']
    return grade_module_dict

# Creates a grade file. File contains all grades and a total.
# A better layout is needed FIXME
def create_grade_file(grade_dict, repo):
    total = 0
    for module in grade_dict[repo]:
        total += grade_dict[repo][module]
    total = round(total, 2)
    with open(f"./results/{repo}/results.txt", 'w+') as fp:
        fp.write(str(grade_dict[repo]))
        fp.write("\n Total Grade:")
        fp.write(str(total))


if __name__ == '__main__':
    repos = get_repo_addresses("resources/GitHub Repositories.txt")
    grades = initialise_grade_dictionairy(repos)
    READMES = get_decoded_readmes(repos)
    RAW_READMES = get_raw_readmes(repos)
    BUILD_FILES, BUILD_TOOLS = get_build_files(repos)
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

        # Evaluate package
        if BUILD_TOOLS is not None:  # does a build file exist?
            # We use the percent of the file existing times the points packaging gets
            grades[repo] = grade_update(grades[repo], 'BUILD_EXISTS', EXISTENCE_OF_BUILD_FILE * PACKAGING)

            match BUILD_TOOLS[repo]:
                case "Maven":
                    if validate_maven_pom(str(BUILD_FILES[repo]), "./resources/maven-4.0.0.xsd"):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
                case "Gradle - Groovy":
                    if validate_groovy_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
                case "Gradle - Kotlin":
                    if validate_kotlin_build(BUILD_FILES[repo], repo):
                        # We use the percent of the file being well-formed times the points packaging gets
                        grades[repo] = grade_update(grades[repo], 'BUILD_FILE_OK', FILE_IS_WELL_FORMED * PACKAGING)
        grades[repo] = finalise_grades(grades[repo])

    for repo in repos:
        path = f"./results/{repo}"
        if not os.path.exists(path):
            print("YOOOoo")
            os.makedirs(path)
        create_grade_file(grades, repo)
