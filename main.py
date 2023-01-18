import os
import constants
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
# The build_file dictionary connects a repo adress with its build file
# The build_tool dictionary connects a repo adress with its build tool
def get_build_files(repo_addresses):
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
    xml_doc = etree.fromstring(xml_string)
    result = xmlschema.validate(xml_doc)
    return result


if __name__ == '__main__':
    repos = ["AnnaMariaDimareli/Java2", "vincentbrison/vb-android-app-quality", "dspinellis/alexandria3k",
             "T821362/T821362", "MichaelM97/Gradle-Kotlin-DSL-Android-Example"]

    # READMES = get_readmes(repos)
    # BUILD_FILES, BUILD_TOOLS = get_build_files(repos)
    # print(BUILD_TOOLS)
    # print(validate_maven_pom(str(BUILD_FILES["AnnaMariaDimareli/Java2"]), "./resources/maven-4.0.0.xsd"))
