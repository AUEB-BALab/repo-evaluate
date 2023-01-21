"""
This module defines all methods which look for usage of GitHub features.
Such as Issues, Actions, Projects or Workflows.
Also, it can also check if some requiermnts are met (amount of commits and contributors)
"""
import os

from github import Github

from constants import *

g = Github(os.environ['GITHUB_GPG_KEY'])


def repo_uses_issues(repo_address: str) -> bool:
    repo = g.get_repo(repo_address)
    events = repo.get_events()
    for event in events:
        if event.type == "IssuesEvent" or event.type == "IssueCommentEvent":
            return True
    return False


def repo_uses_projects(repo_address: str) -> bool:
    repo = g.get_repo(repo_address)
    return repo.get_projects().totalCount > 0


def repo_uses_workflows(repo_address: str) -> bool:
    repo = g.get_repo(repo_address)
    return repo.get_workflow_runs().totalCount > 0


def repo_uses_actions(repo_address: str) -> bool:
    # Actions are not available as a part of the python wrapper for
    # GitHub RESTful API, so we need to directly request them using HTTP requests

    # Imports happen here in order to not strain the whole module if this never runs!
    import requests
    import json

    # Set the GitHub API endpoint
    restful_endpoint = f'https://api.github.com/repos/{repo_address}/actions/runs'

    response = requests.get(restful_endpoint, headers={'Authorization': os.environ['GITHUB_GPG_KEY']})
    total_actions_count = json.loads(response.text)['total_count']
    return total_actions_count > 0


# Checks if a repository has used a GitHub feature (actions, issues etc).
# Issues checked first as they are the most common feature
# Actions checked last as an HTTP request required
def repo_uses_github_features(repository_address) -> bool:
    # if statement instead of multiple 'or' because it's cleaner and explains what is happening better!
    if repo_uses_issues(repository_address):
        return True
    elif repo_uses_workflows(repository_address):
        return True
    elif repo_uses_projects(repository_address):
        return True
    elif repo_uses_actions(repository_address):
        return True
    else:
        return False


def commit_count_ok(repository_address) -> bool:
    repo = g.get_repo(repository_address)
    return repo.get_commits().totalCount > MINIMUM_AMOUNT_OF_COMMITS


def contributor_count_ok(repository_address) -> bool:
    repo = g.get_repo(repository_address)
    return repo.get_contributors().totalCount > 7 # fixme temporarily is set to 7
#   return repo.get_contributors().totalCount > MINIMUM_AMOUNT_OF_CONTRIBUTORS
#    OR
#    return repository_address.get_contributors().totalCount > MINIMUM_AMOUNT_OF_CONTRIBUTORS_FACTOS * CONTRIBUTORS_AMOUNT(
#        repository_address)
