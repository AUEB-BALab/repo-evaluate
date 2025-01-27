"""
This module defines all methods which deal with the licence file
"""
import os

from github import Github
from github.GithubException import UnknownObjectException

g = Github(os.environ["GITHUB_ACCESS_TOKEN"])


# Method gets licence file from git and decodes it
def get_licence_files(repo_addresses: list[str]) -> dict[str, str]:
    """Method gets multiple licence files from git and decodes them in utf-8 form.
    Then it adds these files to a dictionairy

    :param repo_addresses: repository addresses in a list formatted as ['author1/name1', 'author2/name2'...]
    :type repo_addresses: list[str]
    :return: A dictionairy from a repository address to its licence file
    :rtype dict[str, str]
    """
    licence_files = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        try:
            licence_contents = repo.get_license().decoded_content.decode('utf-8')  # decode to utf-8
        except UnknownObjectException:
            licence_contents = None
        licence_files[address] = licence_contents
    return licence_files
