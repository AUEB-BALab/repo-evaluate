"""
This module defines all methods which deal with the contributing files
"""
import os

from github import Github
from github.GithubException import UnknownObjectException

g = Github(os.environ['GITHUB_GPG_KEY'])


def get_contributing_files(repo_addresses: list[str]) -> dict[str, str]:
    """Method gets multiple contributing files from git and decodes them in utf-8 form.
    Then it adds these files to a dictionairy

    :param repo_addresses: repository addresses in a list formatted as ['author1/name1', 'author2/name2'...]
    :type repo_addresses: list[str]
    :return: A dictionairy from a repository address to its contributing file
    :rtype dict[str, str]
    """
    contributing_files = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        try:
            contributing_contents = repo.get_contents("CONTRIBUTING.md").decoded_content.decode(
                'utf-8')  # decode to utf-8
        except UnknownObjectException:
            contributing_contents = None
        contributing_files[address] = contributing_contents
    return contributing_files
