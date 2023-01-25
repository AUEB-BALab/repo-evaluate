"""
This module defines all methods which deal with grading code quality
"""
import os
import re
import shutil
import subprocess

from constants import *


# FIXME methods are not counted correctly sometimes underestimated...
def count_methods(contents: str) -> int:
    """
    Counts how many methods a java source code file contains

    :param contents: The contents of the Java file
    :type contents: str
    :return: The method count
    :rtype: int
    """
    # regex pattern is an adaptation of the patterns found at
    # https://gist.github.com/nrosner/70bed930684f467dddd5fc68cbf39e82
    # Those patterns didn't work but the adapted version does most of the time...

    regex_type = r'[a-zA-Z0-9.<>, ?$[\]]+'
    pattern = re.compile(
        r'^(?:(public|private|protected) )?((?:static|abstract|final|void) ?)*(?:(' + regex_type + ') )?([a-zA-Z]+)\\(([^\\)]*)\\)')

    method_count = 0
    for line in contents.splitlines():
        matches = pattern.findall(line)
        if len(matches) > 0:
            method_count += 1

    if method_count == 0:  # FIXME temp patch
        method_count = 2

    return method_count


# Counts how many comments a java file passed as a string contains
def count_comments(contents: str) -> int:
    """
    Counts how many comments a java file passes as a string contains

    :param contents: The contents of the Java file
    :type contents: str
    :return: The comment count
    :rtype: int
    """
    lines = contents.splitlines()
    comment_count = 0
    currently_in_block_comment = False
    for line in lines:
        line = line.strip()
        if not line:  # line is empty after strip
            continue
        if currently_in_block_comment:
            if "*/" in line:  # block comment finished
                currently_in_block_comment = False
                comment_count += line.count("*/")
            else:
                comment_count += 1
        elif line.startswith("/*"):  # block comment starts
            currently_in_block_comment = True
            comment_count += line.count("/*")
        elif "//" in line:  # an inline comment
            comment_count += 1
    return comment_count


def count_lines(contents: str) -> int:
    """
    Counts how many lines a java file passes as a string contains.

    :param contents: The contents of the Java file
    :type contents: str
    :return: The line count
    :rtype: int
    """
    lines = contents.splitlines()
    return len(lines)


def check_style(contents: str, class_name: str) -> int:
    """
    Checks weather a java file follows check_style sun rules (except Javadoc)
    and returns the amount of errors it encountered

    :param contents: The contents of the Java file
    :param class_name: The public class name that the file contains
    :return: The heck_style error count
    :rtype: int
    """
    check_style_path = './resources/CheckStyle'
    path = os.path.join(check_style_path, 'temp')
    filepath = os.path.join(path, f"{class_name}.java")
    try:
        os.mkdir(path)
        os.remove(filepath)
    except FileNotFoundError:
        pass
    except FileExistsError:
        pass

    with open(filepath, 'w+') as fp:
        fp.write(contents)

    command = ["java", "-jar", f"{check_style_path}/checkstyle-10.6.0-all.jar", "-c",
               f'{check_style_path}/sun_no_javadoc.xml',
               filepath]
    output = subprocess.run(command, capture_output=True, text=True).stdout
    errors = output.count("ERROR")
    return errors


def clean_temporary_checkstyle_java_files() -> None:
    """
    Deletes all the temporary java files needed for checkstyle checks

    :return: None
    """
    try:
        shutil.rmtree('./resources/CheckStyle/temp')
    except FileNotFoundError:
        pass


def get_java_file_stats(contents: str, main_class: str) -> dict[str, int]:
    """
    Takes a java file and the name of its public class and returns a dictionary with statistics about it

    :param contents: The contents of the java file
    :type contents: str
    :param main_class: The name of the public class in the java file
    :type main_class: str
    :return: Dict with the following keys
        'NUMBER_OF_METHODS', 'NUMBER_OF_COMMENTS', 'NUMBER_OF_LINES', 'CHECKSTYLE_ERRORS'
    """
    results = {
        'NUMBER_OF_METHODS': count_methods(contents),
        'NUMBER_OF_COMMENTS': count_comments(contents),
        'NUMBER_OF_LINES': count_lines(contents),
        'CHECKSTYLE_ERRORS': check_style(contents, main_class)
    }
    clean_temporary_checkstyle_java_files()
    return results


def get_repository_java_files_stats(files_dict: dict[str, str]) -> dict[str, dict[str, int]]:
    """
    Takes a dictionairy of java files and returns a dictionairy which contains Stats about them

    :param files_dict: a dictionairy from the file name to the file contents
    :return: A dictionairy of dictionaries. First order of dictionaries connect a java file name (string)
        to the dictionairy with that files statistics.
        The sub-dictionaries contain statistics about each file and connect one of the following keys
        'NUMBER_OF_METHODS', 'NUMBER_OF_COMMENTS', 'NUMBER_OF_LINES', 'CHECKSTYLE_ERRORS' to their count
    """
    result_dict = {}
    for file in files_dict:
        result_dict[file] = get_java_file_stats(files_dict[file], file)
    return result_dict


# Returns in a tuple of 2 boolean values
# If comments per method and comments per line are enough
# True means they are ok!
def commenting_ok(stats_dict: dict[str, int]) -> (bool, bool):
    """
    Checks if a java file has the required comment coverage

    :param stats_dict: Dictionairy of a java files statistics
    :return: Boolean tuple (method_coverage, line_coverage). True where criteria met, else False
    """
    comments_per_method_ok = stats_dict['NUMBER_OF_COMMENTS'] / stats_dict[
        'NUMBER_OF_METHODS'] > 1 / METHODS_PER_COMMENT
    comments_per_line_ok = stats_dict['NUMBER_OF_COMMENTS'] / stats_dict['NUMBER_OF_LINES'] > 1 / LINES_PER_COMMENT
    return comments_per_method_ok, comments_per_line_ok

