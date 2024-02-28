"""
This module deals with evaluating CI usage
"""
import os

from github import Github
from github.GithubException import UnknownObjectException

import search

g = Github(os.environ['GITHUB_GPG_KEY'])


def repos_use_ci(repo_addresses: list[str]) -> dict[str, bool]:
    """
    Checks if multiple repositories use a continuous integration (CI) service.

    :param repo_addresses: A list of repository addresses in the format 'username/repo_name'
    :type repo_addresses: list of str
    :return: A dictionary where the keys are repository addresses and the values are booleans indicating
    whether the repository uses a CI service
    :rtype: dict of str to bool
    """
    ci_usage = {}
    for repo in repo_addresses:
        ci_usage[repo] = repo_uses_ci(repo)
    return ci_usage


def repo_uses_ci(repo_address: str) -> bool:
    """
    Checks if a repository uses a continuous integration (CI) service.

    :param repo_address: The address of the repository in the format 'username/repo_name'
    :type repo_address: str
    :return: True if the repository uses a CI service, False otherwise
    :rtype: bool
    """
    repo = g.get_repo(repo_address)
    try:
        repo.get_contents('.travis.yml')  # we check for Travis CI file
        return True
    except UnknownObjectException:
        try:
            repo.get_contents('circleci/config.yml')  # we check for a Circle CI file
            return True
        except UnknownObjectException:
            if repo_uses_actions(repo_address):  # we look for use of GitHub Actions
                return True
            elif bool(search.search_name_contains_return_file('.yml', '',
                                                              repo_address)):  # is there any yml file?
                return True
            else:
                return False


def repo_uses_actions(repo_address: str) -> bool:
    """
    Returns weather or not a repository uses GitHub feature Actions

    :param repo_address: repository address in format 'author/name'
    :return: True if it uses Actions, False if not
    :rtype: bool
    """

    # Actions are not available as a part of the python wrapper for
    # GitHub RESTful API, so we need to directly request them using HTTP requests

    # Imports happen here in order to not strain the whole module if this never runs!
    import requests
    import json

    # Set the GitHub API endpoint
    restful_endpoint = f'https://api.github.com/repos/{repo_address}/actions/runs'
    response = requests.get(restful_endpoint, headers={'Authorization': 'Bearer ' + os.environ['GITHUB_GPG_KEY']})
    try:
        total_actions_count = json.loads(response.text)['total_count']
    except KeyError:
        return False
    return total_actions_count > 0
