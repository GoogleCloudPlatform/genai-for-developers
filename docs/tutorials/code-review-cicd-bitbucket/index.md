# Bitbucket - Code review automation with GenAI

This tutorial utilizes Gemini to assist with code reviews within the CICD process. An example integration and workflow are included to demonstrate the capabilities and bootstrap your effort. Additional modifications and customizations can be made by providing your own prompts as well as extending the provided CLI tool.

In this tutorial you will:

- Configure GCP for access to Gemini APIs
- Configure Bitbucket to integrate with GCP
- Review Bitbucket workflow and Gemini API calls
- Execute a CICD job and Review GenAI output

## Get Started

- Open the [google cloud console](https://console.cloud.google.com/)
- Activate Cloud Shell

## Configure GCP for access to Gemini APIs

The following steps prepare your Google Cloud project to enable and access Gemini API through Vertex.

### Enable APIs

In the opened terminal, enable required services to use Vertex AI APIs and Gemini chat.

```sh
gcloud services enable \
    aiplatform.googleapis.com \
    cloudaicompanion.googleapis.com \
    cloudresourcemanager.googleapis.com \
    secretmanager.googleapis.com
```

If prompted to authorize, click "Authorize" to continue.

### Create Service Account in GCP

Run following commands to create a new service account and download the keys to your workspace.

You will use this service account to make API calls to Vertex AI Gemini API from CICD pipelines.

```sh
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_NAME='vertex-client'
DISPLAY_NAME='Vertex Client'
KEY_FILE_NAME='vertex-client-key'

gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME --display-name "$DISPLAY_NAME"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/aiplatform.admin" --condition None

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --condition None

gcloud iam service-accounts keys create $KEY_FILE_NAME.json --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

## Configure Bitbucket to integrate with GCP

### Import GitHub Repo to Bitbucket Repo

Login to https://bitbucket.org/ and select “Create” / Repository / Import repository” option.

Git repository url:
```
https://github.com/GoogleCloudPlatform/genai-for-developers.git
```

Select your workspace and project and provide a name for the new repository.

Click - “Import repository” to start the import process.


### Add Bitbucket pipeline variables

Next you are going to enable the Bitbucket CICD pipeline to run code review when changes are pushed to the repository.

Open the Bitbucket repository in the browser and navigate to the “Repository settings / PIPELINES / Settings” section. Enable pipelines for this repository.

Navigate to the “Repository settings / PIPELINES / Repository variables” section.

Add 3 variables:

*   `PROJECT_ID` - your GCP project id
*   `LOCATION` - us-central1
*   `GOOGLE_CLOUD_CREDENTIALS`

For `GOOGLE_CLOUD_CREDENTIALS` variable value, use the service account key created in section above. Run this command in the Google Cloud Shell and copy/paste the value.

```
cat ~/vertex-client-key.json
```

### Run Bitbucket pipeline
Open “Pipelines” section and click “Run initial pipeline”.

Select “main” branch and “default” pipeline and click “Run”.

### Review Bitbucket pipeline output
Open/refresh the “Pipelines” section and review the pipeline output.

### Clone Bitbucket Repo locally
Return to Google Cloud Shell terminal and set up a new SSH key. 
Update your email before running the commands.
```
ssh-keygen -t ed25519 -C “your-email-address”
```

```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

cat ~/.ssh/id_ed25519.pub
```

Add an access key to your Bitbucket repository.
Open “Repository settings / SECURITY / Access keys” and click “Add key”.

For the key value copy/paste the output of the last command.


Under the “Source” section, click “Clone” and copy the Url.

Go back to the terminal and clone the repository. 

Replace with your Bitbucket `project` and `repository` url.
```
git clone git@bitbucket.org:YOUR_PROJECT/genai-for-developers.git
```

## Review Bitbucket pipeline and Gemini API calls

### Review Bitbucket pipeline

Change directory and open `bitbucket-pipelines.yml` file. If you changed the repository name during import, update the folder name before running following commands.
```
cd genai-for-developers

cloudshell edit bitbucket-pipelines.yml
```
### Review command and Gemini API calls

Review the source code for the devai cli.

In cloudshell you can open the specific file with the following command.

```sh
cloudshell edit devai-cli/src/devai/commands/review.py 
```

Review the prompt used in the `code` function. The function begins with

```py
@click.command(name='code')
@click.option('-c', '--context', required=False, type=str, default="")
def code(context):
```

Review the other functions and prompts used in this workflow such as testcoverage, performance, security, blockers.

## Integrations

Take a look at other tutorials to enable integrations with [JIRA](../setup-jira.md), [GitLab](../setup-gitlab.md) and [LangSmith](../setup-langsmith.md).
