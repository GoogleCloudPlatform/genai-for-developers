# Chrome Extension

This application demonstrates a simple GenAI CodeReview browser extension.

Follow the steps below to install the service and extension.

## Environment variables required

Insert your Project_ID and execute the following lines.

```bash
export GCP_PROJECT='<Your GCP Project Id>'  # Change this
export GCP_REGION='us-central1'  
```

Execute the following command to deploy the function

   ```bash

   gcloud functions deploy devai \
   --gen2 \
   --runtime=python311 \
   --region=$GCP_REGION \
   --source=. \
   --entry-point=devai \
   --trigger-http \
   --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION \
   --allow-unauthenticated \
   --memory=512MB
   ```

## Test the Cloud Function

Since this Cloud Function is deployed with a HTTP trigger, you can directly invoke it. Sample calls are shown below:

```bash
curl https://$GCP_REGION-$GCP_PROJECT.cloudfunctions.net/devai
```

## Test the Chrome Extension locally

Modify the `$GCP_PROJECT` and `$GCP_REGION` values in the `index.html` and `script.js` files with the appropriate.

Install the Chrome Extension:

1. From Chrome Browser, go to `Settings --> Extensions --> Manage Extensions`
2. Ensure the `Developer Mode`` is ON i.e. selected.
3. Click on `Load unpacked` button and point to the folder of the extension.
