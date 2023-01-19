"""
This module defines all methods which deal with READMES
"""
import os
import re

from github import Github
from github.GithubException import UnknownObjectException

g = Github(os.environ['GITHUB_GPG_KEY'])


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
