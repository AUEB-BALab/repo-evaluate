"""
This module defines all methods which deal with finding files
"""
import os

from github import Github

g = Github(os.environ['GITHUB_GPG_KEY'])


def search_name_contains_return_size(name_contains: str, repo) -> dict[str, int]:
    """
    Looks for names containing a specific element. For example '.java'
    Returns file names and sizes in a dictionairy

    :param name_contains: What the name shall contain
    :param repo: The repository
    :type repo: Repository
    :return: A dictionairy from file name to size of file
    """

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


def search_name_contains_return_file(name_contains: str, name_doesnt_contain: str, repo_address: str):
    """
    Looks for names containing a specific element. For example '.java'
    Returns file names and contents in a dictionairy

    :return: A dictionairy from file name to size of file
    :param name_contains: What the name shall contain
    :param name_doesnt_contain: What the name shall NOT contain
    :param repo_address: The repository address
    :return: A dictionairy from file name to decoded contents of the file
    """
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


def search_name_matches(file_name: str, repo) -> str:
    """
    Looks for a  file everywhere in a repository
    Returns file contents

    :param file_name: The exact name of the file
    :param repo: The repository
    :type repo: Repository
    :return: file_contents
    """

    # build files were found to not bee in the top DIR...

    # recursively searching all the directories
    def search_directory(directory):
        """
        Sub method of search_name_matches()
        """
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
