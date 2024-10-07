# JIRA - User stories implementation with GenAI

## Overview
This tutorial utilizes Gemini to assist with code generation from JIRA user stories. An example integration and workflow are included to demonstrate the capabilities and bootstrap your effort. Additional modifications and customizations can be made by providing your own prompts as well as extending the provided code.


There are several main parts to the lab:

* Deploy Cloud Run application to integrate with Gemini APIs
* Create and deploy Atlassian Forge app for JIRA
* LangChain ReAct Agents for GitLab tasks automation


![JIRA - GitLab - Gemini Integration](../../../images/devai-api.png "JIRA - GitLab - Gemini Integration")


## Environment setup

### Cloud Project setup

Sign-in to the  [Google Cloud Console](http://console.cloud.google.com) and create a new project or reuse an existing one. If you don't already have a Gmail or Google Workspace account, you must  [create one](https://accounts.google.com/SignUp).

### Create Service Account

Open Google Cloud Console and activate Cloud Shell by clicking on the icon to the right of the search bar.

In the opened terminal, run following commands to create a new service account and keys.

You will use this service account to make API calls to Vertex AI Gemini API from Cloud Run application.

Configure project details using your GCP project details.

Example: `gcp-00-2c10937585bb`

```
gcloud config set project YOUR_GCP_PROJECT_ID
```

Create a service account and grant roles.

```
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_NAME='vertex-client'
DISPLAY_NAME='Vertex Client'
KEY_FILE_NAME='vertex-client-key'

gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME --project $PROJECT_ID --display-name "$DISPLAY_NAME"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/aiplatform.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"


gcloud iam service-accounts keys create $KEY_FILE_NAME.json --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

```

 If prompted to authorize, click "Authorize" to continue.


Enable required services to use Vertex AI APIs and Gemini chat.

```
gcloud services enable \
    generativelanguage.googleapis.com \
    aiplatform.googleapis.com \
    cloudaicompanion.googleapis.com \
    run.googleapis.com \
    cloudresourcemanager.googleapis.com
```

Enable required services to use Vertex AI APIs and Gemini chat.

```
gcloud services enable \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    runapps.googleapis.com \
    workstations.googleapis.com \
    servicemanagement.googleapis.com \
    secretmanager.googleapis.com \
    containerscanning.googleapis.com
```


### Clone GitHub Repository

Create a folder and clone the GitHub repository.

```
mkdir github
cd github
git clone https://github.com/GoogleCloudPlatform/genai-for-developers.git
```

Using the "`File / Open Folder`" menu item, open "`github/genai-for-developers`".


## Enable Gemini Code Assist

Click on the "Gemini" icon, in the bottom right corner, click "`Login to Google Cloud`".

Click the link in the terminal to start authorization flow. Click "Open" to follow the link. Select your account and click "Sign in" on the next screen.
Copy verification code, return to the terminal and paste the code.
Wait for authentication to complete and then click "Select a Google Project".
From the popup window, select your GCP project.

## Code explanation with Gemini Code Assist

Open file "`devai-api/app/routes.py`" and then right click anywhere in the file and select "`Gemini Code Assist > Explain this"` from the context menu.


Review Gemini's explanation for the selected file.


## LangChain Toolkits

[LangChain Toolkits](https://python.langchain.com/docs/integrations/toolkits/) are sets of tools designed to streamline and enhance the development of applications with LangChain. They offer various functionalities depending on the specific toolkit, but generally, they help with:

* **Connecting to external data sources**: Access and incorporate information from APIs, databases, and other external sources into your LangChain applications.
* **Advanced prompting techniques**: Utilize pre-built prompts or create custom ones to optimize interactions with language models.
* **Chain creation and management**: Build complex chains with ease and manage them efficiently.
* **Evaluation and monitoring**: Analyze the performance of your LangChain applications and chains.

Some popular LangChain Toolkits include:

* **Agent Executor Toolkits**: Tools for developing agents that can interact with the real world through actions like web browsing or code execution.
* **Prompt Engineering Toolkit**: A collection of resources for crafting effective prompts.

### GitLab Toolkit

In this lab, you will use the GitLab **Toolkit** to automate GitLab merge request creation.

The Gitlab toolkit contains tools that enable an LLM agent to interact with a gitlab repository. The tool is a wrapper for the `python-gitlab` library.

GitLab toolkit can perform following tasks:

* **Create File** - creates a new file in the repository.
* **Read File** - reads a file from the repository.
* **Update File** - updates a file in the repository.
* **Create Pull Request** - creates a pull request from the bot's working branch to the base branch.
* **Get Issue**s - fetches issues from the repository.
* **Get Issue** - fetches details about a specific issue.
* **Comment on Issue** - posts a comment on a specific issue.
* **Delete File** - deletes a file from the repository.


## GitLab Repository and Toolkit configuration



Open [GitLab](https://gitlab.com/), create a new public project and set up Project Access Token under "`Settings / Access Tokens`".

Use following details:

- Token name: `devai-api`

- Role: `Maintainer`

- Select scopes: `api`


Copy and paste the Access Token value into a temp file on your laptop, it will be used in the next steps. 

Create a new branch "`devai`" off the "`main`" branch under "`Code / Branches`".



## Prepare to deploy application on Cloud Run



Return to the Cloud Shell and use existing or open a new terminal.


Obtain access credentials for your user account via a web-based authorization flow.

Click on the link and follow the steps to generate verification code.

```
gcloud auth login
```

Configure project details using your GCP project details.

Example: `gcp-00-2c10937585bb`

```
gcloud config set project YOUR-GCP-PROJECT-ID
```

Set rest of the environment variables:

```
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1
export REPO_NAME=devai-api
export SERVICE_NAME=devai-api
```

Set environment variables required for GitLab integration.

```
export GITLAB_PERSONAL_ACCESS_TOKEN=gitlab-token
```

To avoid exposing sensitive information in the terminal, the best practice is to use `read -s` this is a secure way to set environment variables without value showing up in the console's command history. After running it, you have to paste the value and hit enter.

This command requires you to update your GitLab userid and repository name.

Example: `export GITLAB_REPOSITORY="gitrey/qwiklabs-test"`

```
export GITLAB_REPOSITORY="USERID/REPOSITORY"
```

Set rest of the environment variables:

```
export GITLAB_URL="https://gitlab.com"
export GITLAB_BRANCH="devai"
export GITLAB_BASE_BRANCH="main"
```


## LangSmith LLM tracing configuration



Create a LangSmith account and generate a Service API key in the Settings section.  [https://docs.smith.langchain.com/](https://docs.smith.langchain.com/) 

Set environment variables required for LangSmith integration.

```
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

export LANGCHAIN_API_KEY=langchain-service-api-key
```


## JIRA configuration



These values are not used in this lab, so you don't need to update it to your specific JIRA project values before executing the commands.

Set environment variables required for Cloud Run service deployment.

```
export JIRA_API_TOKEN=jira-token
export JIRA_USERNAME="YOUR-EMAIL"
export JIRA_INSTANCE_URL="https://YOUR-JIRA-PROJECT.atlassian.net"
export JIRA_PROJECT_KEY="YOUR-JIRA-PROJECT-KEY"
export JIRA_CLOUD=true
```


## Deploy Devai-API to Cloud Run



Check that you are in the right folder.

```
cd ~/github/genai-for-developers/devai-api
```

For this lab, we follow best practices and use  [Secret Manager](https://cloud.google.com/run/docs/configuring/services/secrets) to store and reference the Access Token and LangChain API Key values in Cloud Run.

Store JIRA Access Token in the Secret Manager.

```
echo -n $JIRA_API_TOKEN | \
 gcloud secrets create JIRA_API_TOKEN \
 --data-file=-
```

Store GitLab Access Token in the Secret Manager.

```
echo -n $GITLAB_PERSONAL_ACCESS_TOKEN | \
 gcloud secrets create GITLAB_PERSONAL_ACCESS_TOKEN \
 --data-file=-
```

Store LangChain API Key in the Secret Manager.

```
echo -n $LANGCHAIN_API_KEY | \
 gcloud secrets create LANGCHAIN_API_KEY \
 --data-file=-
```

Deploy application to Cloud Run.

```
gcloud run deploy "$SERVICE_NAME" \
  --source=. \
  --region="$LOCATION" \
  --allow-unauthenticated \
  --service-account vertex-client \
  --set-env-vars PROJECT_ID="$PROJECT_ID" \
  --set-env-vars LOCATION="$LOCATION" \
  --set-env-vars GITLAB_URL="$GITLAB_URL" \
  --set-env-vars GITLAB_REPOSITORY="$GITLAB_REPOSITORY" \
  --set-env-vars GITLAB_BRANCH="$GITLAB_BRANCH" \
  --set-env-vars GITLAB_BASE_BRANCH="$GITLAB_BASE_BRANCH" \
  --set-env-vars JIRA_USERNAME="$JIRA_USERNAME" \
  --set-env-vars JIRA_INSTANCE_URL="$JIRA_INSTANCE_URL" \
  --set-env-vars JIRA_PROJECT_KEY="$JIRA_PROJECT_KEY" \
  --set-env-vars JIRA_CLOUD="$JIRA_CLOUD" \
  --set-env-vars LANGCHAIN_TRACING_V2="$LANGCHAIN_TRACING_V2" \
  --update-secrets="LANGCHAIN_API_KEY=LANGCHAIN_API_KEY:latest" \
  --update-secrets="GITLAB_PERSONAL_ACCESS_TOKEN=GITLAB_PERSONAL_ACCESS_TOKEN:latest" \
  --update-secrets="JIRA_API_TOKEN=JIRA_API_TOKEN:latest" \
  --min-instances=1 \
  --max-instances=3
```

Answer `Y` to create Artifact Registry Docker repository.

```
Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in 
region [us-central1] will be created.

Do you want to continue (Y/n)?  y
```

Review `gcloud run deploy SERVICE_NAME --source=.` flow below.  [Learn more](https://cloud.google.com/run/docs/deploying-source-code).


Behind the scenes, this command uses Google Cloud's `buildpacks` and `Cloud Build` to automatically build container images from your source code without having to install Docker on your machine or set up buildpacks or Cloud Build. That is, the single command described above does what would otherwise require the `gcloud builds submit` and the `gcloud run deploy` commands.

If you have provided Dockerfile(which we did in this repository) then Cloud Build will use it to build container images vs relying on the buildpacks to automatically detect and build container images. To learn more about buildpacks check out  [documentation](https://cloud.google.com/docs/buildpacks/overview).

Review Cloud Build logs in the  [Console](https://console.cloud.google.com/cloud-build/builds).

Review created Docker image in  [Artifact Registry](https://console.cloud.google.com/artifacts).

Open `cloud-run-source-deploy/devai-api` and review vulnerabilities that were automatically detected. Check ones that have fixes available and see how it can be fixed based on the description.



Review Cloud Run instance details in the  [Cloud Console](https://console.cloud.google.com/run).

Test endpoint by running curl command.

```
curl -X POST \
   -H "Content-Type: application/json" \
   -d '{"prompt": "Create HTML, CSS and JavaScript using React.js framework to implement Login page with username and password fields, validation and documentation. Provide complete implementation, do not omit anything."}' \
   $(gcloud run services list --filter="(devai-api)" --format="value(URL)")/generate
```

## Forge platform

[Forge](https://developer.atlassian.com/platform/forge/) is a platform that allows developers to build apps that integrate with Atlassian products, such as Jira, Confluence, Compass and Bitbucket.


#### Install Forge CLI

Run the commands below in the terminal.

Download Node Version Manager ( [nvm](https://github.com/nvm-sh/nvm)) and make it available on the path in the current terminal session.

```
cd ~/github/genai-for-developers

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash


export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" # This loads nvm bash_completion
```

Install nvm. 

Select the latest Node.js LTS release by running the following in the terminal:

```
nvm install --lts
nvm use --lts
```

Install the Forge CLI globally by running:

```
npm install -g @forge/cli
```

For this lab, we will use  [environment variables](https://developer.atlassian.com/platform/forge/getting-started/#using-environment-variables-to-login) to login.


#### Setup JIRA project

**Use your personal account to create/view JIRA projects.**

Review your existing JIRA projects:  [https://admin.atlassian.com/](https://admin.atlassian.com/) 

Create a new JIRA project using your personal account.

Go to  [https://team.atlassian.com/your-work](https://team.atlassian.com/your-work) and select "JIRA Software" - "Try it now". Follow the prompts to complete project/site creation.

Select JIRA Software.
Create a new project.


## Atlassian API token



Create or use an existing Atlassian API token to log in to the CLI. 

The CLI uses your token when running commands.

1. Go to  [https://id.atlassian.com/manage/api-tokens](https://id.atlassian.com/manage/api-tokens).
2. Click **Create API token**.
3. Enter a label to describe your API token. For example, forge-api-token.
4. Click **Create**.
5. Click **Copy to clipboard** and close the dialog.

Run command below in the Cloud Workstations terminal.

Log in to the Forge CLI to start using Forge commands.

Set your JIRA/FORGE email address. Replace with your email address.

```
export FORGE_EMAIL=your-email
```

Set Forge API token. Replace with your JIRA API token.

```
export FORGE_API_TOKEN=your-jira-api-token
```

Test forge cli by running the command below. Answer "`No`" when asked to collect analytics.

```
forge settings set usage-analytics false
```

Check if you are logged in.

```
forge whoami
```

Sample output.

```console
Logged in as John Green (johngreen@email.com)
Account ID: 123090:aaabbcc-076a-455c-99d0-d1aavvccdd
```

#### Create Forge application

Check that you are in the "`~/github/genai-for-developers`" folder.

Run command to create a Forge application.

```
forge create
```

Use following values when prompted:

* App name: `devai-jira-ui-qwiklabs`
* Select a category: `UI Kit`
* Select a product: `Jira`
* Select a template: `jira-issue-panel`

Change into the application folder.

```
cd devai-jira-ui-qwiklabs/
```

Run deployment command.

```
forge deploy
```

Sample output:

```console
Deploying your app to the development environment.
Press Ctrl+C to cancel.

Running forge lint...
No issues found.

✔ Deploying devai-jira-ui-qwiklabs to development...

ℹ Packaging app files
ℹ Uploading app
ℹ Validating manifest
ℹ Snapshotting functions
ℹ Deploying to environment

✔ Deployed

Deployed devai-jira-ui-qwiklabs to the development environment.
```

Install application.

```
forge install
```

Use following values when prompted:

* Select a product: `Jira`
* Enter the site URL: `your-domain.atlassian.net`

Sample output:

```console
Select the product your app uses.

? Select a product: Jira

Enter your site. For example, your-domain.atlassian.net

? Enter the site URL: genai-for-developers.atlassian.net

Installing your app onto an Atlassian site.
Press Ctrl+C to cancel.

? Do you want to continue? Yes

✔ Install complete!

Your app in the development environment is now installed in Jira on genai-for-developers.atlassian.net
```

Open your JIRA site and create a new JIRA task with following description:

```
Create HTML, CSS and JavaScript using React.js framework to implement Login page with username and password fields, validation and documentation. Provide complete implementation, do not omit anything.
```

When you open the task, you will see the "`devai-jira-ui-qwiklabs`" button.

Click the button and review changes in the UI.

View forge backend logs.

```
forge logs
```

#### Atlassian Developer Console

You can also view and manage deployed apps in  [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/).

Review logs - switch to `Development` environment,


### Review Forge application manifest and source code

Open the "`devai-jira-ui-qwiklabs/manifest.yml`" file and use Gemini Code Assist to explain it.


Review explanation.


Open following files and ask Gemini Code Assist to explain them:

* `devai-jira-ui-qwiklabs/src/frontend/index.jsx`
* `devai-jira-ui-qwiklabs/src/resolvers/index.js`



### Update Forge app with DevAI API Cloud Run endpoint

Check if GCP PROJECT ID is set:

```
gcloud config get project
```

If not, set your GCP project using project id:

Example: `gcp-00-2c10937585bb`

```
gcloud config set project YOUR_GCP_PROJECT_ID
```

Set Cloud Run service url:

```
export DEVAI_API_URL=$(gcloud run services list --filter="(devai-api)" --format="value(URL)")

forge variables set DEVAI_API_URL $DEVAI_API_URL
```

Confirm by running command below:

```
forge variables list
```

Sample output


### Update Forge application manifest and code

These code snippets can be found in the repo under `sample-devai-jira-ui` folder.

Open manifest file in the editor: `devai-jira-ui-qwiklabs/manifest.yml`

Add lines below at the end of the file - replace Cloud Run endpoint with the one that you deployed.

```
permissions:
  scopes:
    - read:jira-work
    - write:jira-work
  external:
    fetch:
      client:
        - devai-api-gjerpi6qqq-uc.a.run.app/generate # replace with YOUR CLOUD RUN URL
```

Open resolvers/index file in the editor: `devai-jira-ui-qwiklabs/src/resolvers/index.js`

Add lines below after the existing `getText` function.

```
resolver.define('getApiKey', (req) => {
  return process.env.LLM_API_KEY;
});

resolver.define('getDevAIApiUrl', (req) => {
  return process.env.DEVAI_API_URL;
});
```

Open frontend/index file in the editor: `devai-jira-ui-qwiklabs/src/frontend/index.jsx`

Replace `index.jsx` with content below. Update link to your GitLab userid/repository.

There are two places where you need to update YOUR-GIT-USERID and YOUR-GIT-REPO.

Search for this line in the file and make the changes:

`https://gitlab.com/`**`YOUR-GIT-USERID/YOUR-GIT-REPO`**`/-/merge_requests`

```
import React from 'react';
import ForgeReconciler, { Text, Link, useProductContext } from '@forge/react';
import { requestJira } from '@forge/bridge';
import { invoke } from '@forge/bridge';
import api, { route, assumeTrustedRoute } from '@forge/api';

// const apiKey = await invoke("getApiKey")
const devAIApiUrl = await invoke("getDevAIApiUrl")


const App = () => {
  const context = useProductContext();

  const [description, setDescription] = React.useState();

  const fetchDescriptionForIssue = async () => {
    const issueId = context?.extension.issue.id;
  
    const res = await requestJira(`/rest/api/2/issue/${issueId}`);
    const data = await res.json();
    
    // const genAI = new GoogleGenerativeAI(apiKey);
    // const model = genAI.getGenerativeModel({ model: "gemini-pro"});
    // const prompt = `You are principal software engineer at Google and given requirements below to implement.\nPlease provide implementation details and documentation.\n\nREQUIREMENTS:\n\n${data.fields.description}`
    // const result = await model.generateContent(prompt);
    // const text = result.response.text();
    // const jsonText = JSON.stringify(text);

    const bodyGenerateData = `{"prompt": ${JSON.stringify(data.fields.description)}}`;

    const generateRes = await api.fetch(devAIApiUrl+'/generate',
      {
        body: bodyGenerateData,
        method: 'post',
        headers: { 'Content-Type': 'application/json' },
      }
    )


    const resData = await generateRes.text();
    const jsonText = JSON.stringify(resData);

    const bodyData = `{
      "body": ${jsonText}
    }`;

    console.log("bodyData", bodyData)
    // Add Gemini response as a comment on the JIRA issue
    await requestJira(`/rest/api/2/issue/${issueId}/comment`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: bodyData
    });
    // Add link to the GitLab merge request page as a comment
    await requestJira(`/rest/api/2/issue/${issueId}/comment`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: `{"body": "[GitLab Merge Request|https://gitlab.com/YOUR-GIT-USERID/YOUR-GIT-REPO/-/merge_requests]"}`
    });


    return "Response will be added as a comment. Please refresh in a few moments.";
  };

  React.useEffect(() => {
    if (context) {
      fetchDescriptionForIssue().then(setDescription);
    }
  }, [context]);

  return (
    <>
      <Text>{description}</Text>
      <Link href='https://gitlab.com/YOUR-GIT-USERID/YOUR-GIT-REPO/-/merge_requests' openNewTab={true}>GitLab Merge Request</Link>
    </>
  );
};

ForgeReconciler.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### Redeploy Forge application

Deploy updated application:

```
forge deploy
```

Sample output:

```console
ℹ Uploading app
ℹ Validating manifest
ℹ Snapshotting functions
ℹ Deploying to environment

✔ Deployed

Deployed devai-jira-ui-qwiklabs to the development environment.

We've detected new scopes or egress URLs in your app.
Run forge install --upgrade and restart your tunnel to put them into effect.
```

Install updated application:

```
forge install --upgrade
```

Sample output:

```console
Upgrading your app on the Atlassian site.

Your app will be upgraded with the following additional scopes:
- read:jira-work
- write:jira-work

Your app will exchange data with the following urls:
- devai-api-7su2ctuqpq-uc.a.run.app

? Do you want to continue? Yes

✔ Upgrade complete!

Your app in the development environment is now the latest in Jira on genai-for-developers.atlassian.net.
```

### Test Forge application

Open existing or create a new JIRA task in your JIRA project.

You will need to remove the previous panel if it was added already.

Click "`...`" and select remove from the menu. After that, you can click on the button again.

### Check Jira comments 

Once you get back a response from DEVAI API, two comments will be added on the JIRA issue.

* GitLab merge request
* Gemini user story implementation details

Toggle between "`History`" and "`Comments`" tabs to refresh the view.


### Enable GitLab Merge Request creation

Open file `devai-api/app/routes.py` and uncomment lines below in the `generate_handler` method:

```
print(f"{response.text}\n")

    # resp_text = response.candidates[0].content.parts[0].text

    # pr_prompt = f"""Create GitLab merge request using provided details below.
    # Create new files, commit them and push them to opened merge request.
    # When creating new files, remove the lines that start with ``` before saving the files.

    # DETAILS: 
    # {resp_text}
    # """

    # print(pr_prompt)
    # agent.invoke(pr_prompt)
```

### Redeploy Cloud Run application

Check that you are in the right folder.

```
cd ~/github/genai-for-developers/devai-api
```

If you are using the same terminal session you might have all the environment variables still set.

Check it by running "`echo $GITLAB_REPOSITORY`" in the terminal.

Follow these steps to reset them if a new terminal session was opened.

Make sure to reset required environment variables before redeploying the application.

This command requires you to update your GitLab userid and repository name.

```
export GITLAB_REPOSITORY="USERID/REPOSITORY"
```

Set rest of the environment variables:

```
export GITLAB_URL="https://gitlab.com"
export GITLAB_BRANCH="devai"
export GITLAB_BASE_BRANCH="main"

export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

export LOCATION=us-central1
export REPO_NAME=devai-api
export SERVICE_NAME=devai-api
export PROJECT_ID=$(gcloud config get-value project)

export JIRA_USERNAME="YOUR-EMAIL"
export JIRA_INSTANCE_URL="https://YOUR-JIRA-PROJECT.atlassian.net"
export JIRA_PROJECT_KEY="YOUR-JIRA-PROJECT-KEY"
```

The GitLab toolkit will be using the "`devai`" branch to push the changes for merge request.

Verify that you created that branch already.

#### Deploy application to Cloud Run.

```
gcloud run deploy "$SERVICE_NAME" \
  --source=. \
  --region="$LOCATION" \
  --allow-unauthenticated \
  --service-account vertex-client \
  --set-env-vars PROJECT_ID="$PROJECT_ID" \
  --set-env-vars LOCATION="$LOCATION" \
  --set-env-vars GITLAB_URL="$GITLAB_URL" \
  --set-env-vars GITLAB_REPOSITORY="$GITLAB_REPOSITORY" \
  --set-env-vars GITLAB_BRANCH="$GITLAB_BRANCH" \
  --set-env-vars GITLAB_BASE_BRANCH="$GITLAB_BASE_BRANCH" \
  --set-env-vars JIRA_USERNAME="$JIRA_USERNAME" \
  --set-env-vars JIRA_INSTANCE_URL="$JIRA_INSTANCE_URL" \
  --set-env-vars JIRA_PROJECT_KEY="$JIRA_PROJECT_KEY" \
  --set-env-vars JIRA_CLOUD="$JIRA_CLOUD" \
  --set-env-vars LANGCHAIN_TRACING_V2="$LANGCHAIN_TRACING_V2" \
  --update-secrets="LANGCHAIN_API_KEY=LANGCHAIN_API_KEY:latest" \
  --update-secrets="GITLAB_PERSONAL_ACCESS_TOKEN=GITLAB_PERSONAL_ACCESS_TOKEN:latest" \
  --update-secrets="JIRA_API_TOKEN=JIRA_API_TOKEN:latest" \
  --min-instances=1 \
  --max-instances=3
```

### Verify end to end integration

Kick off the process from the JIRA task by clicking the button again and verify output in GitLab repository, under Merge request section, and LangSmith.

#### GitLab Merge request details.

Open GitLab repository and review created merge request.

#### LangSmith LLM traces

Open  [LangSmith portal](https://smith.langchain.com/) and review LLM trace for JIRA issue creation call.

Sample LangSmith LLM trace.

#### Re-running the integration
GitLab Toolkit does not create new branches and you would need to manually do the following things if you want to re-run the process.

* Close merge request in GitLab
* Delete the existing "`devai`" branch in GitLab repository and then create a new one.

### (OPTIONAL SECTION) Push your changes to GitHub repo

Go to  [GitHub](https://gitlab.com/projects/new) website and create a new repository to push changes for this lab to your personal repository.

Go back to Cloud Workstations instance and set Git user name and email in the terminal. 

Update the values before running the commands.

```
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
```

#### Generate SSH key and add it in the GitHub repository.

Update your email before running the commands.

Do not enter passphrase and hit enter multiple times to complete key generation.

```
ssh-keygen -t ed25519 -C "your-email-address"
```

```
eval "$(ssh-agent -s)"

ssh-add ~/.ssh/id_ed25519

cat ~/.ssh/id_ed25519.pub
```

#### Add generated public key to your GitHub account.

Open  [https://github.com/settings/keys](https://github.com/settings/keys) and click "`New SSH key`".

For the key name use "`qwiklabs-key`" and copy/paste the output from the last command.

Go back to the terminal, commit and push changes. 

```
cd ~/github/genai-for-developers

git remote rm origin
```

Set remote origin using the repository that was created above.

Replace with your repository url.

```
git remote add origin git@github.com:YOUR-GITHUB-USERID/YOUR-GITHUB-REPO.git
```

Add, commit and push the changes.

```
git add .

git commit -m "lab changes"

git push -u origin main
```


## Congratulations!



Congratulations, you finished the lab!

### What we've covered:

* How to deploy Cloud Run applications to integrate with Gemini APIs.
* How to create and deploy Atlassian Forge app for JIRA.
* How to use LangChain ReAct Agents for GitLab tasks automation.
* How to review LLM traces in LangSmith.

### What's next:

* More hands-on sessions are coming!

### Clean up

To avoid incurring charges to your Google Cloud account for the resources used in this tutorial, either delete the project that contains the resources, or keep the project and delete the individual resources.

### Deleting the project

The easiest way to eliminate billing is to delete the project that you created for the tutorial.

©2024 Google LLC All rights reserved. Google and the Google logo are trademarks of Google LLC. All other company and product names may be trademarks of the respective companies with which they are associated.