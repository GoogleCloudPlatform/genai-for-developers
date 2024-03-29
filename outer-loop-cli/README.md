# GenAI CLI on Palm2 for Development

This example demonstrates ways to integrate LLM models into a custom command line utility for use by developers both locally and in automation processes such as CICD pipelines.

This directory contains a sample cli implementation called devai, as well as a tutorial describing how to use it.

## Install and use
The cli is provided as a package on PyPi for demonstration purposes only. It is not intended for production use as is. To install the package for use locally or in CICD systems run the following command

```sh
pip install -i https://test.pypi.org/simple/ devai
```

## Local execution

Once installed you can use the CLI with its short name `devai` as follows

```sh
devai echo
devai echo
devai sub 

devai prompt with_context  
devai prompt with_msg
devai prompt with_msg_streaming

devai review code -c ../../sample-app/src/main/java
devai review performance -c ../../sample-app/src/main/java
devai review security -c ../../sample-app/src/main/java

devai release notes_user_tag -t "v5.0.0"
devai release notes_user -s "main" -e "feature-branch-name" 
```

## Use in CICD

This can be added in any build pipeline following the examples below:

GitHub Actions (Full example at ${repoRoot/.github/workflows/devai-review.yml})

```sh
      - name: Code Review
        run: echo '## Code Review Results 🚀' >> $GITHUB_STEP_SUMMARY
      - run: echo "$(devai review code -c ${{ github.workspace }}/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader)" >> $GITHUB_STEP_SUMMARY
        shell: bash
```

## Developers Guide

### Getting started

To start, setup your virtualenv, install requirements and run the sample command

```sh
python3 -m venv venv
. venv/bin/activate
pip install -r src/requirements.txt

```

Sample commands

Change into the src directory

```sh
cd src
```

```sh
python -m devai echo
python -m devai sub 

python -m devai prompt with_context  
python -m devai prompt with_msg
python -m devai prompt with_msg_streaming

python -m devai review code -c ../../sample-app/src/main/java
python -m devai review performance -c ../../sample-app/src/main/java
python -m devai review security -c ../../sample-app/src/main/java

python -m devai release notes_user_tag -t "v5.0.0"
python -m devai release notes_user -s "main" -e "feature-branch-name" 

```

### Working with an installable app

To create an installable CLI from the source, use setuptools to create the dai cli with the following command from the project base folder.

```sh
pip install --editable ./src
```

### Testing integrations with Cloud Build Jobs

There are multiple cloudbuild files included in order to facilitate local builds and tests as well as automated CICD for this repo.

First ensure you have an AR repo created to hold your image

```sh
gcloud artifacts repositories create app-image-repo \
    --repository-format=docker \
    --location=us-central1
```

To trigger a build in Cloud Build manually run the following command. This build file does not use the ${SHORT_SHA} tag as seen in the standard webhook model

```sh
gcloud builds submit . --config=build/cloudbuild-local.yaml \
    --substitutions=_ARTIFACT_REGISTRY_REPO=app-image-repo
```

To test the CLI as it would be used in a typical pipeline, run the following command.

```sh
gcloud builds submit . --config=build/cloudbuild-pipeline-test.yaml 

```

### Containerized CLI

To work with the CLI inside the container, build it locally and run it with your .config folder mounted to provide access to gcloud credentials

```sh
docker build -t devai-img .
docker run -it -v ~/.config:/root/.config devai-img
```

Once in the container run commands against the cli

```sh
devai ai
devai echo
```

### Cleanup

To uninstall the package run the following command

```sh
python setup.py develop -u
```

To deactivate virtual env run the following command

```sh
deactivate
```

### Publish to PyPi

```sh
pip install build twine
```

```sh
rm -rf src/dist
python3 -m build src/

python3 -m twine upload --repository testpypi src/dist/* --verbose
```

```sh
pip install -i https://test.pypi.org/simple/ devai==0.1.4.2
devai
```

### LangSmith LLM tracing configuration
Create an account and generate API key.

https://docs.smith.langchain.com/setup

Set environment variables required for LangSmith integration.

```sh
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

read -s LANGCHAIN_API_KEY
export LANGCHAIN_API_KEY

```

### JIRA command configuration

Create JIRA API token for your project.

https://id.atlassian.com/manage-profile/security/api-tokens

Set environment variables required for JIRA integration.

```sh
read -s JIRA_API_TOKEN
export JIRA_API_TOKEN

export JIRA_USERNAME = "email that you used to register with JIRA"
export JIRA_INSTANCE_URL = "https://YOUR-PROJECT.atlassian.net"
export JIRA_PROJECT_KEY = "JIRA project key"
```

Commands to test JIRA integration

```sh
# Will return list of JIRA issues in specified JIRA project
devai jira list -c YOUR_JIRA_PROJECT_KEY

# Will create a new JIRA issue with provided details as is
devai jira create -c "New Feature request to implement Login Page.\nExample code block:\n {code}print(\"devai cli\"){code}"

# Will generate implementation and create a new JIRA issue with details
devai jira fix -c "write ring buffer implementation in Rust"
```

### GitLab command configuration