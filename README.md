# dai

## Getting started
To start, setup your virtualenv, install requirements and run the sample command

```sh
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python cli.py  ai 
python cli.py  query 
```

## Adding dependencies

When adding new dependencies, first install the package with pip as seen in the following example. Then be sure to freeze the dependencies in the requirements.txt file

```sh
pip install click
pip freeze > requirements.txt
```

## Working with an installable app

To create an installable CLI from the source, use setuptools to create the dai cli with the following command

```sh
pip install --editable .
```

Once installed you can use the CLI with its short name `dai` as follows

```sh
dai ai
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
gcloud builds submit . --config=cloudbuild-local.yaml \
    --substitutions=_ARTIFACT_REGISTRY_REPO=app-image-repo
```

To test the CLI as it would be used in a typcal pipeline, run the following command.

```sh
gcloud builds submit . --config=cloudbuild-pipeline-test.yaml 

```

## Containerized CLI

To work with the CLI inside the container, build it locally and run it with your .config folder mounted to provide access to gcloud credentials

```sh
docker build -t dai-img .
docker run -it -v ~/.config:/root/.config dai-img
```

Once in the container run commands against the cli

```sh
dai ai
dai query
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
