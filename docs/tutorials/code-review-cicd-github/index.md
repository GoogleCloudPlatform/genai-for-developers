# CICD Code Review with GitHub

This tutorial utilizes Gemini to assist with code reviews within the CICD process. An example integration and workflow are included to demonstrate the capabilities and bootstrap your effort. Additional modifications and customizations can be made by providing your own prompts as well as extending the provided CLI tool.

In this tutorial you will:

- Configure GCP for access to Gemini APIs
- Configure GitHub to integrate with GCP
- Review GitHub workflow and Gemini API calls
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
    cloudresourcemanager.googleapis.com
```

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

gcloud iam service-accounts keys create $KEY_FILE_NAME.json --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

If prompted to authorize, click "Authorize" to continue.

## Configure GitHub to integrate with GCP

### Fork the Repo

This tutorial uses a sample repository to demostrate the features. Start by forking the repo for your own use. 

- [Fork GitHub repo](https://github.com/GoogleCloudPlatform/genai-for-developers/fork)
- Select your github userid as an owner.
- Uncheck option to copy only the "main" branch.
- Click "Create fork".

### Enable GitHub Actions

A GitHub workflow is provided in the repo, however you will need to enable GitHub actions in your forked repo in order to run the process.

- Open the forked repo in the browser
- Switch to the "Actions" tab
- Enable GitHub workflows

### Make GCP secret available to your workflow

In this step you will create a repository secret to hold the GCP API credentials and make them available to Actions within this repo.

- In your GCP terminal run the following command to view the GCP secret created earlier.

```sh
cat ~/vertex-client-key.json
```

- Copy the secret output to your clipboard. You'll paste it in the following steps

- In GitHub, navigate to "Settings -> Secrets and variables -> Actions" in the GitHub repository.
- Add Repository secret called "GOOGLE_API_CREDENTIALS"
- Paste the secret you copied earlier into the value field for the secret.
- Click Add Secret

### Configure local git

The steps in this section assume you have not previously configured git in your workspace, which is often the case for lab enviroments and first time CloudShell uses. If your local git client is already configured you can skip this section.

In your GCP terminal set the Git user name and email. Update the values before running the commands.

```sh
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"

```

Now configure your git client to access your repo by generating an SSH key and adding it to your GitHub account.

Update your email before running the following command

`ssh-keygen -t ed25519 -C "your-email-address"`

Add the key to your auth agent with the following commands. Do not enter passphrase and hit enter multiple times to complete key generation.

```sh
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

Add generated public key to your GitHub account.

- Open https://github.com/settings/keys 
- Click "New SSH key".
- Provide a name such as "qwiklabs-key"
- Copy & paste the output from the last command

### Clone the repository locally

With your local git client configured, you can clone the forked repo locally.

Be sure to replace your user ID in the next command.

```sh
git clone git@github.com:YOUR-USERID/genai-for-developers.git
```

Change into the directory before continuing with the rest of the tutorial.

```sh
cd genai-for-developers
```

## Review GitHub workflow and Gemini API calls

### Review and the Gemini API calls

Inspect the key lines of the CLI that is used in the workflow to understand how it functions.

In cloudshell your can open the specific file with the following command.

```sh
cloudshell edit devai-cli/src/devai/commands/review.py 
```

Review the prompt used in the `code` function. The function begins with

```py
@click.command(name='code')
@click.option('-c', '--context', required=False, type=str, default="")
def code(context):
```

Review the other functions and prompts used in this workflow such as testcoverage, performance, security, blockers

## Review GitHub workflow

Open the GitHub workflow by opening the file below.

```sh
cloudshell edit .github/workflows/devai-review.yml 
```

Review the 5 tasks at the bottom of the file that use the `devai` python script you reviewed in the previous step. For example the code review step includes `devai review code -c [source to review]`

## Execute a CICD job and Review GenAI output

In this step you will commit a change then review the GenAI output in the GitHub logs and summary

### Make changes and push the commit

The workflow file needs to be updated to reference your GCP project.

- Update 2 instances in the file. Replace project id on lines 8 and 30 with your GCP project id. Example: qwiklabs-gcp-02-71a9948ae110

- Stage, commit and push your changes to GitHub. The change will enable the workflow to run correctly and pushing to your repo will execute the workflow. 

### Review AI Output in CICD

With the commit pushed, the workflow will have started executing. You can review the execution and resulting summary in GitHub.

- In the browser, Open the GitHub "Actions" tab and review the workflow output.
- When the job completes click on Summary and scroll down to see the AI generated output.
