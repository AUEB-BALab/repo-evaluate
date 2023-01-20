"""
This module defines all methods which deal with the contributing files
"""
import os

from github import Github
from github.GithubException import UnknownObjectException

g = Github(os.environ['GITHUB_GPG_KEY'])


# Method gets licence file from git and decodes it
def get_contributing_files(repo_addresses):
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
