# GenAI agent for generating JIRA user stories using Slack

## Overview

In this lab, you will create a GenAI Agent, connect it to the Cloud Run application and integrate the agent into the Slack workspace.

![Slack - JIRA - Gemini Integration](../../../images/devai-api-slack.png "Slack - JIRA - Gemini Integration")

### What you will learn

There are several main parts to the lab:

* Deploy Cloud Run application to integrate with Gemini and JIRA APIs
* Create and deploy Vertex AI Agent
* Integrate Agent into Slack


## Setup and Requirements

### Cloud Project setup

Sign-in to the  [Google Cloud Console](http://console.cloud.google.com) and create a new project or reuse an existing one. If you don't already have a Gmail or Google Workspace account, you must  [create one](https://accounts.google.com/SignUp).

## Clone the repo

Open Google Cloud Console and activate Cloud Shell by clicking on the icon to the right of the search bar.


In the opened terminal, run following commands

```
git clone https://github.com/GoogleCloudPlatform/genai-for-developers.git

cd genai-for-developers
```

Click "Open Editor"
Using the "`File / Open Folder`" menu item, open "`genai-for-developers`".
Open a new terminal.


## Create Service Account


Create a new service account and keys.

You will use this service account to make API calls to Vertex AI Gemini API from Cloud Run application.

Configure project details using your GCP project details.

Example: `gcp-00-2c10937585bb`

```
gcloud config set project YOUR_GCP_PROJECT_ID
```

Create service account and grant roles.

```
export LOCATION=us-central1
export PROJECT_ID=$(gcloud config get-value project)
export SERVICE_ACCOUNT_NAME='vertex-client'
export DISPLAY_NAME='Vertex Client'
export KEY_FILE_NAME='vertex-client-key'

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

### Enable Gemini Code Assist

Click on the "Gemini" icon, in the bottom right corner, click "`Sign-in`" and "`Select Google Cloud project`".

From the popup window, select your GCP project.

Open file "`devai-api/app/routes.py`" and then right click anywhere in the file and select "`Gemini Code Assist > Explain this"` from the context menu.

Review Gemini's explanation for the selected file.

## Setup JIRA

Follow this tutorial to enable integrations with [JIRA](../setup-jira.md).

## Deploy Devai-API to Cloud Run


Check that you are in the right folder.

```
cd ~/genai-for-developers/devai-api
```

For this lab, we follow best practices and use  [Secret Manager](https://cloud.google.com/run/docs/configuring/services/secrets) to store and reference the Access Token and LangChain API Key values in Cloud Run.

Set environment variables using the values from the JIRA setup tutorial above.

```
export JIRA_API_TOKEN=your-jira-token
export JIRA_USERNAME="YOUR-EMAIL"
export JIRA_INSTANCE_URL="https://YOUR-JIRA-PROJECT.atlassian.net"
export JIRA_PROJECT_KEY="YOUR-JIRA-PROJECT-KEY"
export JIRA_CLOUD=true
```

Set these environment variable without replacing the values.
```
export GITLAB_PERSONAL_ACCESS_TOKEN=your-gitlab-token
export GITLAB_URL="https://gitlab.com"
export GITLAB_BRANCH="devai"
export GITLAB_BASE_BRANCH="main"
export GITLAB_REPOSITORY="GITLAB-USERID/GITLAB-REPO"

export LANGCHAIN_API_KEY=your-langchain-key
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
```

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
gcloud run deploy devai-api \
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
  --set-env-vars LANGCHAIN_TRACING_V2="$LANGCHAIN_TRACING_V2" \
  --update-secrets="LANGCHAIN_API_KEY=LANGCHAIN_API_KEY:latest" \
  --update-secrets="GITLAB_PERSONAL_ACCESS_TOKEN=GITLAB_PERSONAL_ACCESS_TOKEN:latest" \
  --update-secrets="JIRA_API_TOKEN=JIRA_API_TOKEN:latest" \
  --min-instances=1 \
  --max-instances=3
```

Answer `Y` to create Artifact Registry Docker  repository.

```
Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in 
region [us-central1] will be created.

Do you want to continue (Y/n)?  y
```

Ask Gemini to explain the command.

## Test API
Test endpoint by running curl command.

```
curl -X POST \
   -H "Content-Type: application/json" \
   -d '{"prompt": "Create a functional login page using HTML for structure, CSS for styling, and JavaScript for client-side validation and interactivity."}' \
   $(gcloud  run services list --filter="(devai-api)" --format="value(URL)")/create-jira-issue
```

Review output in JIRA.

## Vertex AI Agent Builder

Search and open "Agent Builder" in the Cloud Console.

Activate APIs and create a new Agent app.
Type "Agent" for Display name and click "Agree & Create".

Set Goal:

```
Help user with JIRA user stories creation
```

Set Instructions:

```
- Greet the users, then ask how you can help them today.
- Summarize the user's request and ask them to confirm that you understood correctly.
  - If necessary, seek clarifying details.
- Thank the user for their business and say goodbye.
```

Click "Save".


Test the Agent using emulator chat on the right side by asking a test question.

### Tool configuration

Open Tools menu and create a new Tool.


Select `OpenAPI` from the Type dropdown.

Set Tool Name:

```
jira-project-stories
```

Set Description:

```
Creates JIRA user stories
```

Set Schema (YAML) - replace YOUR CLOUD RUN URL.

```
openapi: 3.0.0
info:
 title: CR API
 version: 1.0.0
 description: >-
   This is the OpenAPI specification of a service.
servers:
 - url: 'https://YOUR CLOUD RUN URL'
paths:
 /create-jira-issue:
   post:
     summary: Request impl
     operationId: create-jira-issue
     requestBody:
       description: Request impl
       required: true
       content:
         application/json:
           schema:
             $ref: '#/components/schemas/Prompt'
     responses:
       '200':
         description: Generated
         content:
           application/json:
             schema:
               type: string
 /generate:
   post:
     summary: Request impl
     operationId: generate
     requestBody:
       description: Request impl
       required: true
       content:
         application/json:
           schema:
             $ref: '#/components/schemas/Prompt'
     responses:
       '200':
         description: Generated
         content:
           application/json:
             schema:
               type: string

 /test:
   get:
     summary: Request impl
     operationId: test
     responses:
       '200':
         description: Generated
         content:
           application/json:
             schema:
               type: string                    
components:
 schemas:
   Prompt:
     type: object
     required:
       - prompt
     properties:
       prompt:
         type: string
```

Save the Tool configuration.

### Agent configuration

Return to Agent configuration and update instructions to use the tool.

Add instructions to use new tool:

```
- Use ${TOOL: jira-project-stories} to help the user create new JIRE user stories.
```

Switch to Examples tab and add new example:



Set Display Name:

```
jira-project-flow
```

Using menu at the bottom, model the conversation between user and agent.
Using the `+` icon next ti chat prompt, you can select `Agent response` and `User input` to create an example conversation.

```
Agent response: How can I help you today?
User input: I need to craete new JIRA user story
Agent reponse: What are the requirements?
User input: Create a functional login page using HTML for structure, CSS for styling, and JavaScript for client-side validation and interactivity.
Tool invocation: jira-project-stories, action "create-jira-issue"
Agent reponse: Link to your JIRA project
User input: Thank you
Agent response: Can I help you with anything else?
User input: No, thank you
```

Tool invocation configuration:
Tool name:
```
jira-project-stories
```

Action name:
```
create-jira-issue
```

Tool input:
```
{
    "prompt": "Create a functional login page using HTML for structure, CSS for styling, and JavaScript for client-side validation and interactivity."
}
```
Tool output:
```
Link to your JIRA project
```

Click Save and Cancel. Return to the Agent emulator and test the flow.


Review  [Best Practices](https://cloud.google.com/dialogflow/vertex/docs/concept/best-practices) for Vertex AI Agents


### Slack Integration

Open the Integrations menu and click "Connect" on the Slack tile.

Open the link and create a new Slack app at  [https://api.slack.com/apps](https://api.slack.com/apps) 

Select "From an app manifest" option.

Pick a workspace to develop your app.

Switch to YAML and paste this manifest:

```
display_information:
  name: Agent
  description: Agent
  background_color: "#1148b8"
features:
  app_home:
    home_tab_enabled: false
    messages_tab_enabled: true
    messages_tab_read_only_enabled: false
  bot_user:
    display_name: Agent
    always_online: true
oauth_config:
  scopes:
    bot:
      - app_mentions:read
      - chat:write
      - im:history
      - im:read
      - im:write
      - incoming-webhook
settings:
  event_subscriptions:
    request_url: https://dialogflow-slack-4vnhuutqka-uc.a.run.app
    bot_events:
      - app_mention
      - message.im
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

Click "Create".

Install to Workspace.

Select "#general" channel and click "Allow".

Under "Basic Information / App Credentials" - copy "Signing Secret"  and set it in Slack integration for "Signing Secret" field.

Open "OAuth & Permissions" and copy "Bot User OAuth Token" and set it in Slack integration for "Access Token" field.


Set the required fields and click "Start".

Agent's "**Access Token**" value is **"Bot User OAUth Token" from Slack**.

Agent's "**Signing Token**" value is **"Signing Secret" from Slack.**



Copy "Webhook URL" and return to Slack app configuration.

Open the "Event Subscriptions" section and paste the url.


Save the changes.

## Test Agent in Slack

Open "Slack" and add an agent by typing "@Agent".

Ask the agent create several JIRA user stories.


## Prebuilt Agents

Explore prebuilt Agents from the menu on the left.

Select one of the agents and deploy it. Explore Agent's setup, instructions and tools.

## Congratulations!

Congratulations, you finished the lab!

### What we've covered:

* How to deploy Cloud Run application to integrate with Gemini APIs
* How to create and deploy Vertex AI Agent that can help with JIRA user stories creation
* How to add Slack integration for the Agent

### What's next:

* Review  [Best Practices](https://cloud.google.com/dialogflow/vertex/docs/concept/best-practices) for Vertex AI Agents

### Clean up

To avoid incurring charges to your Google Cloud account for the resources used in this tutorial, either delete the project that contains the resources, or keep the project and delete the individual resources.

### Deleting the project

The easiest way to eliminate billing is to delete the project that you created for the tutorial.

©2024 Google LLC All rights reserved. Google and the Google logo are trademarks of Google LLC. All other company and product names may be trademarks of the respective companies with which they are associated.