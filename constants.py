"""
This module defines some constant names. These are Percentiles of grades and threshold for different checks
"""
# These are the high level modules that get graded
TOP_MODULES = ['README', 'PACKAGING', 'TESTING', 'COMMENTING', 'CHECKSTYLE', 'SPOTBUGS', 'CI', 'MODULARITY']

# These are the bonus modules
BONUS_MODULES = ['BIG_README', 'README_USES_MARKDOWN', 'LICENCE_FILE', 'CONTRIBUTING_FILE', 'GITHUB_FEATURES']

# These are the low level modules that get graded (for example PACKAGING is broken in to BUILD_EXISTS and BUILD_FILE_OK)
FINAL_MODULES = ['README', 'BIG_README', 'README_USES_MARKDOWN', 'BUILD_EXISTS', 'BUILD_FILE_OK', 'LICENCE_FILE',
                 'CONTRIBUTING_FILE', 'TESTING_EXISTENCE', 'TESTING_COVERAGE', 'GITHUB_FEATURES',
                 'COMMENTING_METHOD_COVERAGE', 'COMMENTING_LINE_COVERAGE', 'CHECKSTYLE', 'SPOTBUGS', 'CI', 'MODULARITY']

# Headers for the CSV file
CSV_HEADERS = ['REPOSITORY ADDRESS', 'README EXISTS', 'README IS BIG', 'README USES MARKDOWN', 'LICENCE FILE EXISTS',
               'CONTRIBUTING FILE EXISTS', 'BUILD FILE EXISTS', 'BUILD FILE IS OK', 'TEST FILES EXIST',
               'NUMBER OF TEST CLASSES', 'NUMBER OF NON TEST CLASSES', 'USES GITHUB FEATURES', 'NUMBER OF COMMENTS',
               'NUMBER OF LINES', 'NUMBER OF METHODS', 'USES CHECKSTYLE', 'USES SPOTBUGS', 'USES CI',
               'NUMBER OF COMMITS', 'NUMBER OF CONTRIBUTORS', 'NUMBER OF BRANCHES ']

# Top marks (what is the highest grade possible)
TOP_MARK = 10

# Percentiles of each assignment
CHECKSTYLE = 0.1
SPOTBUGS = 0.1
CI = 0.1
TESTING = 0.15
PACKAGING = 0.2
README = 0.1
MODULARITY = 0.15
COMMENTING = round(1 - (CHECKSTYLE + SPOTBUGS + CI + TESTING + PACKAGING + README + MODULARITY), 2)

# Internal Percentiles

# Package #
EXISTENCE_OF_BUILD_FILE = 0.5
FILE_IS_WELL_FORMED = 1 - EXISTENCE_OF_BUILD_FILE

# Comments #
PERCENTAGE_LINES_PER_COMMENT = 0.5
PERCENTAGE_METHOD_PER_COMMENT = round(1 - PERCENTAGE_LINES_PER_COMMENT, 2)

# Testing #
TESTING_EXISTENCE = 0.3
TESTING_COVERAGE = round(1 - TESTING_EXISTENCE, 2)

# Internal Thresholds

# Comments #
LINES_PER_COMMENT = 15
METHODS_PER_COMMENT = 1

# Testing #
TEST_CLASS_PER_NORMAL_CLASS = 0.5

# Modularity #
MODULARITY_AVG_METHOD_SIZE = 20

# TODO check if this is something we would like. Otherwise flag for removal.
#   This could change year on year to not be taken advantage of.
# Bonus points as a percentile of Top marks
LICENCE_FILE = 0.01
CONTRIBUTING_FILE = 0.01
BIG_README = 0.01
README_USES_MARKDOWN = 0.01  # it's not a txt, and it has used at least a couple of markdown elements
GITHUB_FEATURES = 0.01  # Issues, actions, wiki , projects

# Bonus Thresholds
BIG_README_SIZE = 1500
FACTOR_README_MARKDOWN = 1.08  # has to be X times bigger that raw data to be considered good

# Requirements
MINIMUM_AMOUNT_OF_COMMITS = 50
