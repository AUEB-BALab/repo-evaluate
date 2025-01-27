## Repository evaluation
This is a Python application that evaluates the quality of work done in the specified repositories to aid in grading the Programming II team assignments.

### Features

#### The program evaluates the following aspects:

- README
- Testing
    * Test code existence
    * Test code coverage
- Packaging (Limited to Maven and Gradle)
    * Packaging file existence
    * Packaging file formation
- Commenting
- CheckStyle and SpotBugs
- Continuous Integration
    * Travis CI, GitHub Actions or Circle CI
- Modularity

#### It will also as a bonus evaluate :

* LICENCE file existence
* CONTRIBUTING file existence
* A thorough README file
* A README file which actively uses Markdown
* Use of GitHub features (Issues, Actions, Projects etc)

#### It will also determine if the following surpass specific thresholds:

* The number of contributors
* The number of commits

#### CSV:

- Raw data from all the evaluation will be outputed to a `.csv` file which can be used for visualisation and grading

### Building:

- This project uses [Python Poetry](https://python-poetry.org/) for dependency management wilts including a poetry.lock file
- There are two ways you can build the project:
  1) Using Poetry
     - Run `poetry install`
  2) Using pip (PEP-517)
     - Run `pip install -e`
     - _Keep in mind that pip will not use the lock file to determine dependency versions, therefore issues with newer versions may surface. Also, no run instructions will be given bellow. You are on your own_


### Usage:

1) Optionally tweak the constants in `repo_evaluate\constants.py` to your liking
2) Run `poetry run python .\repo_evaluate\main.py <repository.txt> <output\directory>`
    * _Replace python with your python installation name if it differs_
    * _`repository.txt` should contain the repositories for evaluation each on a new line. Check `test_repositories.txt` for an example_
    * _`output\directory` should point to where you want the results stored_

### Requirements

- You must have an environmental variable `GITHUB_ACCESS_TOKEN` with your [GitHub Pesonal Acess Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) otherwise you will hit the GitHub
  API limit pretty fast
- PowerShell is used and must be installed (by default It's available on Windows)
- Gradle must be installed in order to evaluate Gradle builds
  - The last 2 requirements are optional, if ignored Gradle and Kotlin builds will just always fail

### Contributing:

- Outsider contributing to this repository is not open at the moment

### Limitations

- Gradle validation doesn't work 100% of the time. When a Gradle build fails standard error is saved to sort manually
  later
- Evaluation of comment coverage compared to number of methods is off. Sometimes it underestimates the number of methods
  in java files
- The number of contributors required is currently set as a hard number not a factor of group participants

### Licencing

- Unless otherwise stated all of this repository is covered by the EUROPEAN UNION PUBLIC LICENCE v. 1.2
- My permanent address is in Greece, so as per EUPL v1.2 the governing law is the Greek law
- You are required to read what is stated in
  the [LICENCE.md](https://github.com/panos1b/Vathmologia_Ergasion/blob/master/docs/LICENSE.md) before using this
  repository
  in any way
