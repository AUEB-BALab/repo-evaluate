"""
This module defines all methods which deal with READMES
"""
import os
import re

from github import Github
from github.GithubException import UnknownObjectException

g = Github(os.environ["GITHUB_ACCESS_TOKEN"])


def get_decoded_readmes(repo_addresses: list[str]) -> dict[str, str]:
    """
    Returns multiple GitHub repository README in a dictionary. Data is decoded to utf-8!

    :param repo_addresses: Repository addresses in a list formatted as ['author1/name1', 'author2/name2'...]
    :return: A Dictionairy from repository address to README
    """
    readmes = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        try:
            readme_contents = repo.get_readme().decoded_content.decode('utf-8')  # decode to uts-8
        except UnknownObjectException:
            readme_contents = None
        readmes[address] = readme_contents
    return readmes


def get_raw_readmes(repo_addresses):
    """
    Returns multiple GitHub repository readmes in a dictionary. Data is plain-text!

    :param repo_addresses: Repository addresses in a list formatted as ['author1/name1', 'author2/name2'...]
    :return: A Dictionairy from repository address to README
    """
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
