import Resolver from '@forge/resolver';
import { fetch } from '@forge/api';

const resolver = new Resolver();

resolver.define('createGitLabMR', async (req) => {
  const { prompt } = req.payload || {};

  if (!prompt || typeof prompt !== 'string') {
    throw new Error('Prompt is required and must be a string');
  }

  const devAIApiUrl = process.env.DEVAI_API_URL;
  const devAIApiKey = process.env.DEVAI_API_KEY;

  if (!devAIApiUrl) {
    throw new Error('DEVAI_API_URL environment variable is not configured');
  }
  if (!devAIApiKey) {
    throw new Error('DEVAI_API_KEY environment variable is not configured');
  }

  const baseUrl = devAIApiUrl.endsWith('/') ? devAIApiUrl.slice(0, -1) : devAIApiUrl;
  const response = await fetch(`${baseUrl}/create-gitlab-mr`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-devai-api-key': devAIApiKey,
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to create GitLab MR (${response.status}): ${errorText}`);
  }

  return await response.text();
});

export const handler = resolver.getDefinitions();
