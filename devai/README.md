# DevAI - Developer Productivity Utilities

The apps contained in this folder provide various features to support developers throughout the SDLC.

The apps are published to pypi at the following locations:
- https://test.pypi.org/project/devaicore
- https://test.pypi.org/project/devaicli

**DevAI Core** contains centralized logic and prompts to be used by many different interfaces including: CLI, Chrome Extensions, Slackbot and more.

**DevAI CLI** is a command line interface exposing devai capabilities directly to developer in the terminal or utilized in CICD processes for automation.

## Usage

Create your virtual environment

```sh
python3 -m venv venv
source venv/bin/activate
```

NOTE:

    google-cloud-aiplatform is not availble in the pypi repo and needs to be installed first with:

    pip install google-cloud-aiplatform

Install and run the devai cli with the following commands:

```sh
pip install -i https://test.pypi.org/simple/ devaicli

devai echo
```

Include devaicore in your application with the following command:

```sh
pip install -i https://test.pypi.org/simple/ devaicore
```

## Local dev

To develop locally install the components in editable mode with the following commands:

```sh
python3 -m venv venv
source venv/bin/activate

pip install -e devai-core/
pip install -e devai-cli

devai echo
```

Any changes in either app will be reflected on new executions.
