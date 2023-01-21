"""
This module defines all methods which deal with grading code quality
"""
import os
import re
import subprocess
import shutil

from constants import *

# FIXME methods not counted correctly...
# Counts how many methods a java file passes as a string contains
def count_methods(contents: str):
    # regex pattern is an adaptation of the patterns found at
    # https://gist.github.com/nrosner/70bed930684f467dddd5fc68cbf39e82
    # Those patterns didn't work but the adapted version dose

    regex_type = r'[a-zA-Z0-9.<>, ?$[\]]+'
    pattern = re.compile(
        r'^(?:(public|private|protected) )?((?:static|abstract|final|void) ?)*(?:(' + regex_type + ') )?([a-zA-Z]+)\\(([^\\)]*)\\)')

    method_count = 0
    for line in contents.splitlines():
        matches = pattern.findall(line)
        if len(matches) > 0:
            method_count += 1
    return method_count


# Counts how many comments a java file passes as a string contains
def count_comments(contents: str):
    lines = contents.splitlines()
    comment_count = 0
    in_block_comment = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
                comment_count += line.count("*/")
            else:
                comment_count += 1
        elif line.startswith("/*"):
            in_block_comment = True
            comment_count += line.count("/*")
        elif "//" in line:
            comment_count += 1
    return comment_count


def count_lines(contents: str):
    lines = contents.splitlines()
    return len(lines)


def check_style(contents: str, class_name: str):
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


def clean_temporary_checkstyle_java_files():
    try:
        shutil.rmtree('./resources/CheckStyle/temp')
    except FileNotFoundError:
        pass


def get_java_file_stats(contents, main_class):
    results = {
        'NUMBER_OF_METHODS': count_methods(contents),
        'NUMBER_OF_COMMENTS': count_comments(contents),
        'NUMBER_OF_LINES': count_lines(contents),
        'CHECKSTYLE_ERRORS': check_style(contents, main_class)
               }
    clean_temporary_checkstyle_java_files()
    return results


def get_repository_java_files_stats(files_dict):
    result_dict = {}
    for file in files_dict:
        result_dict[file] = get_java_file_stats(files_dict[file], file)
    return result_dict


# Returns in a tuple of 2 boolean values
# If comments per method and comments per line are enough
# True means they are ok!
def commenting_ok(stats_dict) -> (bool, bool):
    if stats_dict['NUMBER_OF_METHODS'] == 0: # FIXME methods not counted correctly...
        stats_dict['NUMBER_OF_METHODS'] = 2

    comments_per_method_ok = stats_dict['NUMBER_OF_COMMENTS'] / stats_dict[
        'NUMBER_OF_METHODS'] > 1 / METHODS_PER_COMMENT
    comments_per_line_ok = stats_dict['NUMBER_OF_COMMENTS'] / stats_dict['NUMBER_OF_LINES'] > 1 / LINES_PER_COMMENT
    return comments_per_method_ok, comments_per_line_ok


def style_ok(stats_dict) -> bool:
    return stats_dict['CHECKSTYLE_ERRORS'] / stats_dict['NUMBER_OF_LINES'] < CHECKSTYLE_ERRORS_PER_LINE
