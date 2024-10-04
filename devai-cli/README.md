# DevAI CLI with Gemini Pro for Development

![Devai CLI integration](../images/code-review-github.png "Devai CLI integration")

This example demonstrates ways to integrate LLM models into a custom command line utility for use by developers both locally and in automation processes such as CICD pipelines.

This directory contains a sample cli implementation called devai, as well as a tutorial describing how to use it.

## Developers Guide

Execute commands in your terminal.

### Clone repository
```sh
git clone https://github.com/GoogleCloudPlatform/genai-for-developers.git

cd genai-for-developers/devai-cli
```

### GCP Project config

Set GCP project and location.

```sh
export PROJECT_ID=YOUR-GCP-PROJECT
export LOCATION=us-central1

gcloud config set project $PROJECT_ID
```

### GCP access credentials
Obtain GCP user access credentials via a web flow. CLI will use these credentials to authenticate and make API calls.
```sh
gcloud auth application-default login
```

### Enable APIs

Enable Vertex AI and Secrets Manager APIs in your GCP project.

```sh
gcloud services enable \
    aiplatform.googleapis.com \
    cloudaicompanion.googleapis.com \
    cloudresourcemanager.googleapis.com \
    secretmanager.googleapis.com
```

### Init Python virtualenv

To start, setup your virtualenv, install requirements and run the sample command

```sh
python3 -m venv venv
. venv/bin/activate
pip install -r src/requirements.txt
```

### Working with an installable app

To create an installable CLI from the source, use setuptools to create the DEVAI cli with the following command from the project base folder.

```sh
pip install --editable ./src
```

### Sample commands

Once installed you can use the CLI with its short name `devai` as follows

```sh
devai review code -c ../sample-app/src/main/java
devai review performance -c ../sample-app/src/main/java
devai review security -c ../sample-app/src/main/java

devai review code -c ../sample-app/src/main/java/anthos/samples/bankofanthos/balancereader/BalanceReaderController.java

devai review testcoverage -c ../sample-app/src

devai document readme -c ../sample-app/src/main/
devai document update-readme -f ../sample-app/README.md -c ../sample-app/src/main/java/
devai document releasenotes -c ../sample-app/src/main/java
devai document update-releasenotes -f ../sample-app/releasenotes.md -c ../sample-app/src/main/java/ -t "v1.2.3"

devai review blockers -c ../sample-app/pom.xml
devai review blockers -c ../sample-app/setup.md

devai review impact \
  --current ~/github/repo/service-v1.0.0/modules/login \
  --target ~/github/repo/service-v2.0.0/modules/login

devai review imgdiff \
  -c /ui/main-page-after-upgrade.png \
  -t /ui/main-page-before-upgrade.png  

devai review image \
  -f "/tmp/diagram.png" \
  -p "Review and summarize this diagram"

devai review video \
  -f "/tmp/video.mp4" \
  -p "Review and summarize this video"  

devai release notes_user_tag -t "v5.0.0"
devai release notes_user -s "main" -e "feature-branch-name" 

devai rag load -r "https://github.com/GoogleCloudPlatform/genai-for-developers"
devai rag query -q "What does devai do"

devai prompt with_context  
devai prompt with_msg
devai prompt with_msg_streaming
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

## Use in CICD

### Configure Service Account

Run commands below to create service account and keys.

```sh
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_NAME='vertex-client'
DISPLAY_NAME='Vertex Client'
KEY_FILE_NAME='vertex-client-key'

gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME --display-name "$DISPLAY_NAME"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/aiplatform.admin" --condition None

gcloud iam service-accounts keys create $KEY_FILE_NAME.json --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --condition None
```

### Configure Environment Variables in CICD

Add following environment variables/secrets to your CICD pipeline.

If you have JIRA, GitLab and LangSmith integrations enabled, add additional env variables for respective systems, see details in sections below.

- GOOGLE_CLOUD_CREDENTIALS
- PROJECT_ID
- LOCATION

For GOOGLE_CLOUD_CREDENTIALS variable value, use service account key created in section above.

```sh
cat $KEY_FILE_NAME.json
```

DevAI CLI can be added in any build pipeline following the examples below:

### GitHub Actions (Full example at ${repoRoot/.github/workflows/devai-review.yml})

[devai-review.yaml](../.github/workflows/devai-review.yml)

```sh
      - name: Code Review
        run: echo '## Code Review Results 🚀' >> $GITHUB_STEP_SUMMARY
      - run: echo "$(devai review code -c ${{ github.workspace }}/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader)" >> $GITHUB_STEP_SUMMARY
        shell: bash
```

### GitLab Pipeline example

[.gitlab-ci.yml](../.gitlab-ci.yml)

```sh
build-job:
  stage: build
  script:
  .
  .
    - devai review code -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
    - devai review performance -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
    - devai review security -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
```

### Jenkins Pipeline example

[Jenkinsfile](../Jenkinsfile)

```sh
pipeline {
    agent any

    stages {
        stage('build') {
            steps {
                dir("${env.WORKSPACE}/devai-cli") {
                    sh '''
                    python3 -m venv ./venv
                    . ./venv/bin/activate
                    ./venv/bin/pip install -r src/requirements.txt
                    ./venv/bin/pip install --editable ./src
                    '''
                    
                    withCredentials([
                            file(credentialsId: 'GOOGLE_APPLICATION_CREDENTIALS', variable: 'GOOGLE_APPLICATION_CREDENTIALS'),
                            string(credentialsId: 'PROJECT_ID', variable: 'PROJECT_ID'),
                            string(credentialsId: 'LOCATION', variable: 'LOCATION'),
                            
                        ]) {    
                            sh '''
                            ./venv/bin/devai review code -c /bitnami/jenkins/home/workspace/genai-cicd_genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
                            ./venv/bin/devai review performance -c /bitnami/jenkins/home/workspace/genai-cicd_genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
                            ./venv/bin/devai review security -c /bitnami/jenkins/home/workspace/genai-cicd_genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
                            '''
                            }
                }
            }
        }
    }
}         
```

### BitBucket Pipeline example

[BitBucket](../bitbucket-pipelines.yml)

```sh
image: python:3.11-slim

pipelines:
  default:
      - step:
          name: DevAI CLI
          caches:
            - pip
          script:
            - apt-get update && apt-get install -y git
            .
            .
            - devai review code -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
            - devai review performance -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
            - devai review security -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
  
```

### CircleCI Pipeline example

[config.yml](../.circleci/config.yml)

```sh
version: 2.1

jobs:
  ai-insights-code-review:
    docker:
      - image: python:3.11-slim
    steps:
      - checkout
      - run:
            command: |
              .
              .
              devai review code -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader            
```


## Testing integrations with Cloud Build Jobs

There are multiple cloudbuild files included in order to facilitate local builds and tests as well as automated CICD for this repo.

First ensure you have an AR repo created to hold your image

```sh
gcloud artifacts repositories describe app-image-repo --location=$LOCATION
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

## Containerized CLI

To work with the CLI inside the container, build it locally and run it with your .config folder mounted to provide access to gcloud credentials

```sh
docker build -t devai-img .
docker run -it -v ~/.config:/root/.config devai-img
```

Once in the container run commands against the cli

```sh
devai echo
```


## Publish to PyPi

To publish manually
- Update version number in setup.py
  - Follow semantic versioning
  - versioned in order as follows (`.devN, aN, bN, rcN, <no suffix>, .postN`)
- Retrieve a personal API key from https://pypi.org/manage/account/token/ to publish
  - You will need rights to publish to the pypi project
- Run the commands below an supply your API key when prompted

```sh
pip install build twine
```

```sh
rm -rf src/dist
rm -rf src/devai_cli.egg-info
python3 -m build src/

python3 -m twine upload src/dist/* --verbose
```


## Install and use PyPi package
The cli is provided as a package on PyPi for demonstration purposes only. It is not intended for production use as is. To install the package for use locally or in CICD systems run the following command

Set environment variables in your local environment or in CICD pipeline environment variables.

```sh
export PROJECT_ID=YOUR_GCP_PROJECT_ID
export LOCATION=us-central1
```

Install cli:
```sh
pip install devai-cli
```

Install specific version:
```sh
pip install devai-cli==0.0.0a1
```

Test cli:
```sh
devai echo
```

## Integrations

### JIRA command configuration

Create JIRA API token for your project.

https://id.atlassian.com/manage-profile/security/api-tokens

Set environment variables required for JIRA integration.

```sh
export JIRA_API_TOKEN=your-jira-api-token
export JIRA_USERNAME="email that you used to register with JIRA"
export JIRA_INSTANCE_URL="https://YOUR-PROJECT.atlassian.net"
export JIRA_PROJECT_KEY="JIRA project key"
export JIRA_CLOUD=true
```

#### Enable functionality
Un-comment imports and function calls to use JIRA commands
- cli.py
- review.py

#### Commands to test JIRA integration

```sh
# Will return list of JIRA issues in specified JIRA project
devai jira list -c YOUR_JIRA_PROJECT_KEY

# Will create a new JIRA issue with provided details as is
devai jira create -c "New Feature request to implement Login Page.\nExample code block:\n {code}print(\"devai cli\"){code}"

# Will generate implementation and create a new JIRA issue with details
devai jira fix -c "write ring buffer implementation in Rust"
```

### GitLab command configuration

Create Project Access Token with following details:

- role: Maintainer
- selected scopes: api

https://gitlab.com/YOUR-USERID/YOUR-PROJECT/-/settings/access_tokens

Set environment variables required for GitLab integration.

```sh
export GITLAB_PERSONAL_ACCESS_TOKEN=your-gitlab-token

export GITLAB_URL="https://gitlab.com"
export GITLAB_REPOSITORY="USERID/REPOSITORY"
export GITLAB_BRANCH="devai"
export GITLAB_BASE_BRANCH="main"
```

#### Enable functionality
Un-comment imports and function calls to use GitLab commands
- cli.py
- review.py

#### Commands to test GitLab integration

```sh
# Will create a new merge request with provided details
# Requires a branch to be created off main - manual step at this point
# export GITLAB_BRANCH="fix-branch"
devai gitlab create-pr -c "Details with file changes, docs, etc"

# Will create a new GitLab issue with provided details as is
devai gitlab fix-issue -c 4

# Will add a comment to GitLab issue 
# issue name defaults to 'CICD AI Insights' for demonstration
devai gitlab create-comment -c "new comment content goes here"

# Will add a comment to GitLab issue with name 'CICD AI Insights'
devai gitlab create-comment -i "CICD AI Insights" -c "new comment content goes here"
```


### LangSmith LLM tracing configuration
Create an account and generate API key.

https://docs.smith.langchain.com/

Set environment variables required for LangSmith integration.

```sh
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

read -s LANGCHAIN_API_KEY
export LANGCHAIN_API_KEY
```
