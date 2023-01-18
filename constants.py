"""
This module defines some constant names. Thet are Percentiles of grades and threshold for different checks
"""

# Percentiles of each assignment
CHECKSTYLE = 0.15
TESTING = 0.2
COVERAGE = 0.2
PACKAGING = 0.3
README = 0.1
COMMENTING = round(1 - (CHECKSTYLE + TESTING + COVERAGE + PACKAGING), 2)

# Internal Percentiles

# Package #
EXISTENCE_OF_BUILD_FILE = 0.5
FILE_IS_WELL_FORMED = 1 - EXISTENCE_OF_BUILD_FILE

# Comments #
PERCENTAGE_LINES_PER_COMMENT = 0.5
PERCENTAGE_LINES_PER_METHOD = 1 - PERCENTAGE_LINES_PER_COMMENT

# Internal Thresholds

# Coverage: #
PERCENT_OF_METHODS = 0.5
PERCENT_OF_LINES = 0.25

# Comments
LINES_PER_COMMENT = 10
METHODS_PER_COMMENT = 1

# TODO check if this is something we would like. Otherwise flag for removal.
#   This could change year ot year to not be taken advantage of.
# Bonus points out of 10 for
LICENCE_FILE = 0.1
CONTRIBUTING_FILE = 0.1
BIG_README = 0.1
README_USES_MARKDOWN = 0.1  # it's not a txt, and it has used at least a couple of markdown elements
GITHUB_FEATURES = 0.1  # Issues, actions, wiki , projects

# Bonus Thresholds
BIG_README_SIZE = 1500
