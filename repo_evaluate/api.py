"""Provide a shared GitHub object instance to all modules."""

import os
from github import Github, Auth


# Using an access token
auth = Auth.Token(os.environ['GITHUB_ACCESS_TOKEN'])


github_instance = Github(auth=auth)

def get_github_instance():
    """Return the shared GitHub instance object."""
    return github_instance
