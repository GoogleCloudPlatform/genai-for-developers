# DevAI CLI Demo Guide

This guide will walk you through setting up and using the DevAI CLI tool, from initial setup to running all available commands.

## Prerequisites

1. Python 3.11 or higher
2. Git
3. Google Cloud Platform (GCP) account with:
   - Vertex AI API enabled
   - Secret Manager API enabled
   - A service account with appropriate permissions

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/googlecloudplatform/genai-for-developers.git
cd genai-for-developers
```

2. Set up Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the DevAI CLI:
```bash
cd devai-cli/src
pip install -r requirements.txt
pip install --editable .
cd ../..
```

4. Set up GCP credentials (choose one method):

Method 1 - Using gcloud CLI (Recommended for local development):
```bash
# Install gcloud CLI if you haven't already
# https://cloud.google.com/sdk/docs/install

# Login and set up application default credentials
gcloud auth application-default login
```

Method 2 - Using service account key:
```bash
# Create a service account key file from GCP Console
# Save it as service-account-key.json in the devai-cli directory
export GOOGLE_APPLICATION_CREDENTIALS="service-account-key.json"
```

Note: Method 1 (gcloud auth) is recommended for local development as it's more secure and easier to manage. Method 2 (service account key) is typically used in CI/CD environments or when you need to share credentials with other services.

5. Set required environment variables:
```bash
export PROJECT_ID="your-gcp-project-id"
export LOCATION="us-central1"  # Required for most commands
export REGION="us-central1"    # Required for GitLab integration
```

Note: While `LOCATION` is the primary environment variable used by most commands, `REGION` is specifically required for GitLab integration. For simplicity, you can set both to the same value.

## Running the Demo

### 1. Health Check
First, let's verify everything is set up correctly:

```bash
devai healthcheck
```
This should return a successful response from Vertex AI.

### 2. Code Review Commands

#### Basic Code Review
Review a single file:
```bash
devai review code -c sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
```

Review with different output formats:
```bash
# JSON output
devai review code -c sample-app/src/main/java/anthos/samples/bankofanthos/balancereader -o json

# Table output
devai review code -c sample-app/src/main/java/anthos/samples/bankofanthos/balancereader -o table
```

#### Performance Review
Review code for performance issues:
```bash
devai review performance -c sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
```

#### Security Review
Review code for security issues:
```bash
devai review security -c sample-app/src/main/java/anthos/samples/bankofanthos/balancereader
```

#### Compliance Review
Review code against compliance standards:
```bash
devai review compliance -c sample-app/k8s
```

#### Test Coverage Review
Review test coverage:
```bash
devai review testcoverage -c sample-app/src
```

#### Blockers Review
Review for potential blockers:
```bash
devai review blockers -c sample-app/pom.xml
```

### 3. Image and Video Analysis

#### Image Review
Review an image:
```bash
devai review image -c images/extension-diagram.png -p "Describe this architecture diagram"
```

#### Image Comparison
Compare two images:
```bash
devai review imgdiff -c images/extension-diagram.png -c images/code-review-github.png
```

#### Video Review
Review a video:
```bash
# Note: No sample video files are included in the repository
# You'll need to provide your own video file path
devai review video -c path/to/your/video.mp4 -p "Describe this video"
```

### 4. Documentation Commands

#### README Review
Review a README file:
```bash
# Review the main project README
devai document readme -c README.md

# Review the sample app README
devai document readme -c sample-app/README.md

# Review the CLI README
devai document readme -c devai-cli/README.md
```

#### Documentation Review
Review documentation:
```bash
# Review all tutorials
devai document docs -c docs/tutorials

# Review specific tutorial
devai document docs -c docs/tutorials/setup-cli.md
```

### 5. Release Notes

Generate release notes:
```bash
devai release notes -t v1.0.0
```

Generate user notes:
```bash
devai release usernotes -t v1.0.0
```

## Advanced Usage

### Using Custom Prompts

The CLI supports custom prompts through Google Secret Manager. To set up a custom prompt:

1. Create a secret in Google Secret Manager:
```bash
gcloud secrets create review_query --replication-policy="automatic"
gcloud secrets versions add review_query --data-file=prompt.txt
```

2. The CLI will automatically use this prompt for code reviews.

### Integration with CI/CD

The CLI can be integrated into CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: DevAI Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install DevAI CLI
        run: |
          cd devai-cli/src
          pip install -r requirements.txt
          pip install --editable .
      - name: Run Code Review
        run: devai review code -c ${{ github.workspace }}
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_SA_KEY }}
          PROJECT_ID: ${{ secrets.PROJECT_ID }}
```

## Troubleshooting

1. If you get authentication errors:
   - Verify your service account key is correctly set up
   - Check that the PROJECT_ID environment variable is set
   - Ensure the Vertex AI API is enabled in your GCP project

2. If commands fail with "Secret not found":
   - Verify the secret exists in Google Secret Manager
   - Check that your service account has access to Secret Manager

3. For image/video analysis errors:
   - Ensure the file paths are correct
   - Check that the files are in supported formats
   - Verify file permissions

## Additional Resources

- [DevAI CLI Documentation](../docs/devai-cli.md)
- [GCP Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Google Secret Manager Documentation](https://cloud.google.com/secret-manager/docs) 