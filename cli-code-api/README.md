# GenAI CLI on Palm2 for Development

This example demonstrates ways to integrate LLM models into a custom command line utility for use by developers both locally and in automation processes such as CICD pipelines.

This directory contains a sample cli implementation called devai, as well as a tutorial describing how to use it.

## Getting started

To start, setup your virtualenv, install requirements and run the sample command

```sh
cd cli-code-api
python3 -m venv venv
. venv/bin/activate
pip install -r src/requirements.txt

```

Sample commands

Change into the src directory

```
cd src
```

```sh
python devai.py  echo
python devai.py  sub 

python devai.py prompt with_context  
python devai.py prompt with_msg
python devai.py prompt with_msg_streaming

python devai.py review code -c ../testfiles/ef
python devai.py review performance -c ../testfiles/perf
python devai.py review security -c ../testfiles/sec

python devai.py release notes_user_tag -t "v5.0.0"
python devai.py release notes_user -s "main" -e "feature-branch-name" 

```

## Adding dependencies

When adding new dependencies, first install the package with pip as seen in the following example. Then be sure to freeze the dependencies in the requirements.txt file.

The following command is run from the projects base folder. 

```sh
pip install click
pip freeze > src/requirements.txt
```

## Working with an installable app

To create an installable CLI from the source, use setuptools to create the dai cli with the following command from the project base folder.

```sh
pip install --editable ./src
```

Once installed you can use the CLI with its short name `devai` as follows

```sh
devai echo
```

## Testing integrations with Cloud Build Jobs

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

## Containerized CLI

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

## Cleanup

To uninstall the package run the following command

```sh
python setup.py develop -u
```

To deactivate virtual env run the following command

```sh
deactivate
```
