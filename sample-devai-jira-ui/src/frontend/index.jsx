import React from 'react';
import ForgeReconciler, { Text, Link, useProductContext } from '@forge/react';
import { requestJira, invoke } from '@forge/bridge';

const App = () => {
  const context = useProductContext();

  const [description, setDescription] = React.useState();

  const fetchDescriptionForIssue = async () => {
    const issueId = context?.extension.issue.id;

    const res = await requestJira(`/rest/api/2/issue/${issueId}`);
    const data = await res.json();

    if (!data.fields?.description) {
      return "Error: The issue description is empty.";
    }

    await invoke('createGitLabMR', { prompt: data.fields.description });

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
      fetchDescriptionForIssue()
        .then(setDescription)
        .catch((err) => {
          setDescription(`Error creating merge request: ${err.message}`);
        });
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
