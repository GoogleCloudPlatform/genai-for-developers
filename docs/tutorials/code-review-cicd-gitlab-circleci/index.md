# CircleCI - Code review automation with GenAI

This tutorial utilizes Gemini to assist with code reviews within the CICD process. An example integration and workflow are included to demonstrate the capabilities and bootstrap your effort. Additional modifications and customizations can be made by providing your own prompts as well as extending the provided CLI tool.

In this tutorial you will:

- Configure GCP for access to Gemini APIs
- Configure CircleCI to integrate with GCP
- Review CircleCI workflow and Gemini API calls
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


## Import GitHub Repo to GitLab Repo

Go to https://gitlab.com/projects/new and select “`Import project`” / “`Repository by URL`” option:

Git repository url:


```
https://github.com/GoogleCloudPlatform/genai-for-developers.git
```


Under Project URL - select your gitlab userid

Set Visibility to `Public`.

Click - “`Create Project`” to start the import process.

If you see an error about invalid GitHub Repository URL, [create a new GitHub token](https://github.com/settings/tokens)(fine-grained) with Public repositories read-only access, and retry import again providing your GitHub userid and token.


### Disable GitLab workflow execution
Edit the `.gitlab-ci.yml` file in the GitLab UI and uncomment the lines to disable GitLab workflow execution on code push events. 
You can still execute the workflow from UI on demand.

```
# workflow:
#   rules:
#     - if: $CI_PIPELINE_SOURCE == "web"
```



## Setup CircleCI

Next you are going to enable the CircleCI CICD pipeline to run code review when changes are pushed to the repository.

Open CircleCI[https://app.circleci.com/] website and create a new Project. 

Select `“GitLab” / “Cloud”` for your repo.
Grant CircleCI access to your GitLab account.

Under the `Fastest` option, select the `main` branch. CircleCI might detect an existing config file and skip this step.

### Configure Environment Variables

After the project is created, click on the “`Project Settings” / “Environment Variables`” section.

Add the environment variables that you used so far.

*   `PROJECT_ID` - your GCP project id
*   `LOCATION` - us-central1
*   `GOOGLE_CLOUD_CREDENTIALS`

For `GOOGLE_CLOUD_CREDENTIALS` variable value, use the service account key created in section above. Run this command in the Google Cloud Shell and copy/paste the value.

```
cat ~/vertex-client-key.json
```
### Start the workflow

Start the workflow from the CircleCI UI and review the output.


## Clone the repository locally

Return to the Cloud Shell terminal and clone the repository.
Replace with your GitLab userid and repository url that was just created.

```sh
git clone https://gitlab.com:YOUR_GITLAB_USERID/genai-for-developers.git
```

Change into the directory before continuing with the rest of the tutorial.

```sh
cd genai-for-developers
```

## Review CircleCI workflow config and Gemini API calls

### Review CircleCI workflow config

Change directory and open `.circleci/config.yml` file.

```sh
cloudshell edit .circleci/config.yml
```

Review the tasks at the bottom of the file that use the `devai` cli. 

For example the code review step includes `devai review code -c [source to review]`

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
