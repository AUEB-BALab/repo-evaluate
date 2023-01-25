"""
This module defines all methods which look for usage of GitHub features.
Such as Issues, Actions, Projects or Workflows.
Also, it can also check if some requirements are met (amount of commits and contributors)
"""
import os
import continuous_integration

from github import Github

from constants import *

g = Github(os.environ['GITHUB_GPG_KEY'])


def repo_uses_issues(repo_address: str) -> bool:
    """
    Returns weather or not a repository uses GitHub feature Issues

    :param repo_address: repository address in format 'author/name'
    :return: True if it uses Issues, False if not
    :rtype: bool
    """
    repo = g.get_repo(repo_address)
    events = repo.get_events()
    for event in events:
        if event.type == "IssuesEvent" or event.type == "IssueCommentEvent":
            return True
    return False


def repo_uses_projects(repo_address: str) -> bool:
    """
    Returns weather or not a repository uses GitHub feature Projects

    :param repo_address: repository address in format 'author/name'
    :return: True if it uses Projects, False if not
    :rtype: bool
    """
    repo = g.get_repo(repo_address)
    return repo.get_projects().totalCount > 0


def repo_uses_workflows(repo_address: str) -> bool:
    """
    Returns weather or not a repository uses GitHub feature Workflows

    :param repo_address: repository address in format 'author/name'
    :return: True if it uses Workflows, False if not
    :rtype: bool
    """
    repo = g.get_repo(repo_address)
    return repo.get_workflow_runs().totalCount > 0




def repo_uses_github_features(repository_address: str) -> bool:
    """
    Checks if a repository has used a GitHub feature (actions, issues etc).
    Issues checked first as they are the most common feature
    Actions checked last as an HTTP request required

     :param repository_address: repository address in format 'author/name'
     :return: True if it uses at least ONE feature, False if it uses NON
     :rtype: bool
     """
    # if statement instead of multiple 'or' because it's cleaner and explains what is happening better!
    if repo_uses_issues(repository_address):
        return True
    elif repo_uses_workflows(repository_address):
        return True
    elif repo_uses_projects(repository_address):
        return True
    elif continuous_integration.repo_uses_actions(repository_address):
        return True
    else:
        return False


def commit_count_ok(repository_address: str) -> bool:
    """
    Checks if a repository has had enouph commits to justify GitHub usage

     :param repository_address: repository address in format 'author/name'
     :return: True if it uses at least a bigger amount of commits than MINIMUM_AMOUNT_OF_COMMITS in constants
        , False otherwise
     :rtype: bool
     """
    repo = g.get_repo(repository_address)
    return repo.get_commits().totalCount > MINIMUM_AMOUNT_OF_COMMITS


def contributor_count_ok(repository_address) -> bool:
    """
    Checks if a repository has had enough different contributors to justify team work

     :param repository_address: repository address in format 'author/name'
     :return: True if it has had enough different contributors, False otherwise
     :rtype: bool
     """
    repo = g.get_repo(repository_address)
    return repo.get_contributors().totalCount > 4  # fixme temporarily is set to 4, consider the following

#   return repo.get_contributors().totalCount > MINIMUM_AMOUNT_OF_CONTRIBUTORS
#   OR
#   return repository_address.get_contributors().totalCount > MINIMUM_AMOUNT_OF_CONTRIBUTORS_FACTORS *
#   CONTRIBUTORS_AMOUNT(repository_address)
