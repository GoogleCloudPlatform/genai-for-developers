## GitLab Setup

This example demonstrates integration with GitLab to automatically comment on the GitLab issue with code review findings.


### GitLab command configuration

Open GitLab and create a Project Access Token under “`Settings / Access Tokens`” in the GitLab repository that you will use for this integration.

Copy and store the Access Token value to be used in the next steps.

Use following details:

- Token name: devai-cli
- Role: Maintainer
- Scope: api

### Set environment variables required for GitLab integration.

This command requires you to update your GitLab Access Token.
```
export GITLAB_PERSONAL_ACCESS_TOKEN=gitlab-access-token
```

This command requires you to update your GitLab userid and repository name.
```
export GITLAB_REPOSITORY="USERID/REPOSITORY"
```

Set rest of the environment variables:
```
export GITLAB_URL="https://gitlab.com"
export GITLAB_BRANCH="devai"
export GITLAB_BASE_BRANCH="main"
```


Open the GitLab website and create a new GitLab issue in your project with the title `CICD AI Insights`.

### Enable GitLab command in the code

Open `review.py` file:
```
~/genai-for-developers/devai-cli/src/devai/commands/review.py
```

Find and uncomment line numbers below

Line to import GitLab command
```
# from devai.commands.gitlab import create_gitlab_issue_comment
```

Method to comment on GitLab issue in the `@click.command(name='code')`
```
# create_gitlab_issue_comment(response.text)
```

Re-run code review command:

```
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1

devai review code -c ~/genai-for-developers/sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
```

Review console output and check for new comments on the issue in the GitLab repository that used for this integration.



