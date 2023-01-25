## Vathmologia Ergasion

This is a Python application which aims at partly grading the semester assignments for the Programming II class taught
by [dspinellis](https://github.com/dspinellis/).

### Features

#### It will grade the following

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

#### It will also grade as a bonus:

* LICENCE file existence
* CONTRIBUTING file existence
* A thorough README file
* A README file which actively uses Markdown
* Use of GitHub features (Issues, Actions, Projects etc)

#### It will also determine if the following surpass specific thresholds:

* The number of contributors
* The number of commits

#### CSV:
- Raw data from all the grading will be outed to a `.CSV` file which can be used for anything

#### Usage:

1) In `resources/GitHub Repositories.txt`  place the repositories you want to grade
2) Tweak the constants in `constants.py` to your liking
3) Run `main.py`
4) Results are outputted to the `./results` folder

#### Requirements

- You must have an environmental variable `GITHUB_GPG_KEY` with your GitHub GPG key otherwise you will hit the GitHub
  API limit pretty fast
- PowerShell is used and must be installed (by default It's available on Windows)
- Java must be installed in order to evaluate Checkstyle
- Gradle must be installed in order to evaluate Gradle builds

#### Contributing:

- Outsider contributing to this repository is not open at the moment

#### Limitations

- Gradle validation doesn't work 100% of the time. When a Gradle build fails standard error is saved to sort manually
  later
- Evaluation of comment coverage compared to number of methods is off. Sometimes it underestimates the number of methods
  in java files
- The number of contributors required is currently set as a hard number not a factor of group participants

#### Licencing

- Unless otherwise stated all of this repository is covered by the EUROPEAN UNION PUBLIC LICENCE v. 1.2
- My permanent address is in Greece, so as per EUPL v1.2 the governing law is the Greek law
- You are required to read what is stated in
  the [LICENCE.md](https://github.com/panos1b/Vathmologia_Ergasion/blob/master/docs/LICENSE.md) before using this
  repository
  in any way
