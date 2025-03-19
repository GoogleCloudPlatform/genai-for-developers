## GitHub Setup

This example demonstrates integration with GitHub to automatically open Pull Requests with new changes.


### GitHub command configuration

#### Create new GitHub application
Create and register a Github app using these [steps](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app).

Grant following repository permissions to the new application:

- Commit statuses (read only)
- Contents (read and write)
- Issues (read and write)
- Metadata (read only)
- Pull requests (read and write)

#### Grant access to the repository
Use the [GitHub  App settings](https://github.com/settings/installations) to grant access to the repository.

#### Generate new private key for the application

Open [GitHub Apps](https://github.com/settings/apps) and generate a private key for your application.


### Set environment variables required for GitHub integration.

- GITHUB_APP_ID - Application ID from your app's general settings
- GITHUB_APP_PRIVATE_KEY - The location of your app's private key .pem file, or the full text of that file as a string.
- GITHUB_REPOSITORY - The name of the Github repository you want your app to act upon. Must follow the format {userid}/{repository-name}.

Example:
```
export GITHUB_APP_ID="1022112"
export GITHUB_APP_PRIVATE_KEY="/project/app-name-app.YYYY-MM-DD.private-key.pem"
export GITHUB_REPOSITORY="gitrey/genai-for-developers"
```

### Enable GitHub integration in the code for DEVAI CLI command

Open `document.py` file:
```
~/genai-for-developers/devai-cli/src/devai/commands/document.py
```

Find and uncomment lines below

Line to import method
```
# from devai.commands.github_cmd import create_github_pr
```

Code to open Pull Request in the `@click.command(name='readme')`
```
#    if file and branch:
#        try:
#            create_github_pr(branch, {
#                file: response.text,
#                })
#        except Exception as e:
#            print(f"Failed to create pull request: {e}")
```

Run documentation command:

```
export PROJECT_ID=$(gcloud config get-value project)
export LOCATION=us-central1

cd ~/genai-for-developers/devai-cli

devai document readme -c ../sample-app/src/main/ -f "sample-app/README.md" -b "feature/docs-update"
```

Review console output and check for new pull request in the GitHub repository that was used for this integration.



