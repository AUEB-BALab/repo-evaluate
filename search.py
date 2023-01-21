"""
This module defines all methods which deal with finding files
"""
import os

from github import Github

g = Github(os.environ['GITHUB_GPG_KEY'])


# Looks for names containing a specific element. For example .java
# Returns file names and sizes in a dictionairy
def search_name_contains_return_size(name_contains, repo):
    # recursively searching all the directories
    def search_directory(directory):
        contents = repo.get_contents(directory)
        file_sizes = {}
        for content in contents:
            if content.type == "dir":
                file_sizes.update(search_directory(content.path))
            elif name_contains in content.name:
                # get the name and size of the file
                file_sizes[content.name] = content.size
        return file_sizes

    return search_directory('')


# Looks for names containing a specific element. For example .java
# Returns files in dict with content
def search_name_contains_return_file(name_contains, name_doesnt_contain, repo_address):
    # recursively searching all the directories
    repo = g.get_repo(repo_address)
    def search_directory(directory):
        contents = repo.get_contents(directory)
        files = {}
        for content in contents:
            if content.type == "dir":
                files.update(search_directory(content.path))
            elif name_contains in content.name and name_doesnt_contain not in content.name:
                # get the name and contents
                files[content.name] = content.decoded_content.decode('utf-8')
        return files

    return search_directory('')


# Looks for a  file everywhere in a repository (build files were found to not bee in the top DIR)
# Returns file contents
def search_name_matches(file_name, repo):
    # recursively searching all the directories
    def search_directory(directory):
        contents = repo.get_contents(directory)
        for content in contents:
            if content.type == "dir":
                file_content = search_directory(content.path)
                if file_content is not None:
                    return file_content
            elif content.name == file_name:
                # get the contents of the file
                file_content = repo.get_contents(content.path)
                return file_content

    return search_directory('')
