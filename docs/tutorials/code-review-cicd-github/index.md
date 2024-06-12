# CICD Code Review with GitHub

## Setup

### Create Service Account

In the opened terminal, run following commands to create a new service account and keys.

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

### Enable APIs
Enable required services to use Vertex AI APIs and Gemini chat.

```sh
gcloud services enable \
    aiplatform.googleapis.com \
    cloudaicompanion.googleapis.com \
    cloudresourcemanager.googleapis.com
```

### Configure GitHub Repo

**Fork the Repo**

Fork GitHub repo to your personal GitHub repo
Go to https://github.com/GoogleCloudPlatform/genai-for-developers/fork and select your github userid as an owner. Uncheck option to copy only the "main" branch.

Click "Create fork".

**Enable GitHub Actions**

Open a forked repo in the browser and switch to the "Actions" tab to activate workflows.

**Create a secret**

Next create a repository secret, to hold the GCP API credentials,  under "Settings / Secrets and variables / Actions" in the GitHub repository.

Add Repository secret "GOOGLE_API_CREDENTIALS"

For secret value, run the command below in the terminal and copy/paste the file content.

```sh
cat ~/vertex-client-key.json
```

**Configure local git**

Go back to the terminal and set Git user name and email. Update the values before running the commands.

```sh
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"

```


**Configure ssh tokens for git**

Generate SSH key and add it in the GitHub repository.

Update your email before running the commands.

Do not enter passphrase and hit enter multiple times to complete key generation.

`ssh-keygen -t ed25519 -C "your-email-address"`

```sh
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

Add generated public key to your GitHub account.

Open https://github.com/settings/keys and click "New SSH key".

For the key name use "qwiklabs-key" and copy/paste the output from the last command.

**Clone the repository locally**

Go back to the terminal and clone the repository. Replace with your repository url.

mkdir github
cd github

git clone git@github.com:YOUR-USERID/genai-for-developers.git

cd genai-for-developers

## Make Code Changes

**Update sample code with project_id**

```sh
cloudshell edit .github/workflows/devai-review.yml 
```

Replace project id on lines 8 and 30 with your qwiklabs project id.

Example: qwiklabs-gcp-02-71a9948ae110

**Commit code**

Stage, commit and push the changes you made to update the project id.

**Review AI Output in CICD**

In the browser, Open the GitHub "Actions" tab and review the workflow output.
