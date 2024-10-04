## JIRA Setup

This example demonstrates integration with JIRA to automatically open new issues with code review findings.

### Create new JIRA project
Use your personal account to create/view JIRA projects.

Review your existing JIRA projects: https://admin.atlassian.com/

Create a new JIRA project using your personal account.

Go to https://team.atlassian.com/your-work and click and then select. 
After that select "JIRA Software" - "Try it now". Follow the prompts to complete project/site creation.



Select JIRA Software.



Create a new project.



### JIRA API token
Create or use an existing Atlassian API token to log in to the CLI.

The CLI uses your token when running commands.

Go to https://id.atlassian.com/manage/api-tokens.
Click Create API token.
Enter a label to describe your API token. For example, forge-api-token.
Click Create.
Click Copy to clipboard and close the dialog.

Set environment variables required for JIRA integration (replace the values before running the commands).

```
export JIRA_API_TOKEN=your-token-value
export JIRA_USERNAME="email that you used to register with JIRA"
export JIRA_INSTANCE_URL="https://YOUR-PROJECT.atlassian.net"
export JIRA_PROJECT_KEY="JIRA project key"
export JIRA_CLOUD=true
```

### Enable JIRA command in the code

Open review.py file:

```
~/genai-for-developers/devai-cli/src/devai/commands/review.py
```

Find and uncomment line below this one:
```
# Uncomment after configuring JIRA and GitLab env variables - see README.md for details
```

Import JIRA command at the top of the file
```
# from devai.commands.jira import create_jira_issue
```

Method to create JIRA issue in the code method `@click.command(name='code')`
```
#create_jira_issue("Code Review Results", response.text)
```

Re-run code review command:

```
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1

devai review code -c ~/genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
```

Review console output and check for new issue in your JIRA project.






