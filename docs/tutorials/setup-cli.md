## DEVAI CLI

This example demonstrates ways to integrate LLM models into a custom command line utility for use by developers both locally and in automation processes such as CICD pipelines.

### Clone the repository
Open terminal and clone the repository.

```
git clone https://github.com/GoogleCloudPlatform/genai-for-developers.git
```

### Run DEVAI CLI locally

Obtain GCP user access credentials via a web flow. CLI will use these credentials to authenticate and make API calls.
```
gcloud auth application-default login
```

Set GCP project and location.
```
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1
```

Go back to the terminal and run commands below to install devai locally.
```
pip3 install devai-cli
```

The cli was installed but it's not in the PATH.

```
WARNING: The script devai is installed in '/home/student_00_478dfeb8df15/.local/bin' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
```

Run the command below to update the PATH environment variable. Replace with your user’s home folder name. For example: student_00_478dfeb8df15

```
export PATH=$PATH:/home/YOUR-USER-HOME-FOLDER/.local/bin
```


Run devai cli command to perform code review locally. Review cli output.
```
cd ~/genai-for-developers

devai review code -c ./sample-app/src/main/java/anthos/samples/bankofanthos/balancereader

```

Open review command and review the code:

```
devai-cli/src/devai/commands/review.py
```

### DevAI CLI Development
In this section you will be making changes to devai cli. 
To start, set up python virtualenv, install requirements and run the sample command.

```
cd ~/genai-for-developers/devai-cli
python3 -m venv venv
. venv/bin/activate
pip3 install -r src/requirements.txt
pip3 install --editable ./src
devai echo
```

Re-run code review command to check that everything is working fine:

```
devai review code -c ~/genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
```

### Explore devai cli commands


#### Code review command
```
devai review code -c ~/genai-for-developers/sample-app/src/main/java
```


#### Performance review command
```
devai review performance -c ~/genai-for-developers/sample-app/src/main/java
```


#### Security review command
```
devai review security -c ~/genai-for-developers/sample-app/src/main/java
```

#### Test coverage review command
```
devai review testcoverage -c ~/genai-for-developers/sample-app/src
```



#### Blockers review commands
```
devai review blockers -c ~/genai-for-developers/sample-app/pom.xml
devai review blockers -c ~/genai-for-developers/sample-app/setup.md
```

#### Image/Diagram review and summarization:

```
devai review image \
  -f ~/genai-for-developers/images/extension-diagram.png \
  -p "Review and summarize this diagram"
```

#### Image diff analysis:

```
devai review imgdiff \
  -c ~/genai-for-developers/images/devai-api.png \
  -t ~/genai-for-developers/images/devai-api-slack.png  
```

#### Documentation generation command:

```
devai document readme -c ~/genai-for-developers/sample-app/src/main/
```

## Integrations

Take a look at other tutorials to enable integrations with [JIRA](./setup-jira.md), [GitLab](./setup-gitlab.md) and [LangSmith](./setup-langsmith.md).







