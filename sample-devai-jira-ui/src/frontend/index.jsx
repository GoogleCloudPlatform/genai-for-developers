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
    );

    const resData = await generateRes.text();
    const jsonText = JSON.stringify(resData);

    const bodyData = `{
      "body": ${jsonText}
    }`;

    await requestJira(`/rest/api/2/issue/${issueId}/comment`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: bodyData
    });

    await requestJira(`/rest/api/2/issue/${issueId}/comment`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: `{"body": "[GitLab Merge Request|https://gitlab.com/gitrey/qwiklabs-test/-/merge_requests]"}`
    });

   
    return "DevAI API response will be added as a comment. Please refresh in a few moments.";
  };

  React.useEffect(() => {
    if (context) {
      fetchDescriptionForIssue().then(setDescription);
    }
  }, [context]);

  return (
    <>
      <Text>{description}</Text>
      <Link href='https://gitlab.com/gitrey/qwiklabs-test/-/merge_requests' openNewTab={true}>GitLab Merge Request</Link>
    </>
  );
};

ForgeReconciler.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);