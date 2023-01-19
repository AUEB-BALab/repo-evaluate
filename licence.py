"""
This module defines all methods which deal with the licence file
"""
import os

from github import Github
from github.GithubException import UnknownObjectException

g = Github(os.environ['GITHUB_GPG_KEY'])


def get_licence_files(repo_addresses):
    licence_files = {}
    for address in repo_addresses:
        repo = g.get_repo(address)
        try:
            licence_contents = repo.get_license().decoded_content.decode('utf-8')  # decode to utf-8
        except UnknownObjectException:
            licence_contents = None
        licence_files[address] = licence_contents
    return licence_files
