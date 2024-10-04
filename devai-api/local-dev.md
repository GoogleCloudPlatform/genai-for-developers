## Running DEVAI-API locally

### Set GCP env vars
```sh
export PROJECT_ID=YOUR-GCP-PROJECT
export LOCATION=us-central1
```

### Set JIRA env vars
```sh
export JIRA_API_TOKEN=YOUR_JIRA_API_TOKEN
export JIRA_USERNAME="YOUR_EMAIL"
export JIRA_INSTANCE_URL="https://YOUR-JIRA-PROJECT.atlassian.net"
export JIRA_PROJECT_KEY="YOUR-JIRA-PROJECT-KEY"
export JIRA_CLOUD=true
```

### Set GitLab env vars
```sh
export GITLAB_BRANCH="main"
export GITLAB_URL="https://gitlab.com"
export GITLAB_REPOSITORY="GITLAB_USERID/GITLAB_REPOSITORY"
export GITLAB_BRANCH="devai"
export GITLAB_BASE_BRANCH="main"
export GITLAB_PERSONAL_ACCESS_TOKEN=YOUR_GITLAB_PAT
```

### Set LangSmith env vars
```sh
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY=YOUR_LANGSMITH_SERVICE_KEY
```

### Enable venv
```sh
cd devai-api
python3 -m venv venv-api
. venv-api/bin/activate
```

### Install dependencies
```sh
pip install -r requirements.txt 
```

### Start the app
```sh
python run_app.py
```

### Test JIRA user story creation
```sh
curl -X POST -H "Content-Type: application/json" -d '{"prompt": "Create a webpage to manage team off-site sessions. Session schema: id, time, topic, speaker. Provide HTML, JavaScript and CSS. Add backend API using FASTAPI framework."}' http://localhost:8080/create-jira-issue
```

### Test GitLab merge request creation
```sh
curl -X POST -H "Content-Type: application/json" -d '{"prompt": "Create a webpage to manage team off-site sessions. Session schema: id, time, topic, speaker. Provide HTML, JavaScript and CSS. Add backend API using FASTAPI framework."}' http://localhost:8080/generate
```

### Cloud Run
[Cloud Run deployment steps](./README.md)