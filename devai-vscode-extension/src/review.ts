/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */ 

import * as vscode from 'vscode';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

const CODE_LABEL = 'Here is the code:';
const REVIEW_LABEL = 'Here is the review:';

const GCP_PROJECT_ID = "genai-cicd";
const REVIEW_PROMPT_SM = "CUSTOM_REVIEW_PROMPT/versions/latest";

const PROMPT = `
Reviewing code for Your Coding Style guide compliance.


1) Check that python-json-logger library is used for logging.
2) Check that all methods have detailed python docstrings.
3) Check for Your copyright header


Provide short report with findings.
Show this link to developer to read about internal logging practices: https://internal.confluence.com/team/logging.
`;


async function readSecret(secretName: string): Promise<string | null> {
  try {
    // Create the Secret Manager client.
    const client = new SecretManagerServiceClient();

    // Build the resource name of the secret.
    const name = client.secretPath(GCP_PROJECT_ID, secretName);

    // Access the secret version.
    const [version] = await client.accessSecretVersion({ name });

    // Return the secret payload using optional chaining.
    return version.payload?.data?.toString() ?? null;
  } catch (error) {
    console.error('Error accessing secret:', error);
    return null;
  }
}

export async function generateReview() {
  vscode.window.showInformationMessage('Generating code review...');
  const modelName = vscode.workspace.getConfiguration().get<string>('google.gemini.textModel', 'models/gemini-1.5-pro');

  // Get API Key from local user configuration
  const apiKey = vscode.workspace.getConfiguration().get<string>('google.gemini.apiKey');
  if (!apiKey) {
    vscode.window.showErrorMessage('API key not configured. Check your settings.');
    return;
  }

  const genai = new GoogleGenerativeAI(apiKey);
  const model = genai.getGenerativeModel({model: modelName});

  // Text selection
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    console.debug('Abandon: no open text editor.');
    return;
  }

  const selection = editor.selection;
  const selectedCode = editor.document.getText(selection);

  var DEVAI_REVIEW_PROMPT = await readSecret(REVIEW_PROMPT_SM);

  if (DEVAI_REVIEW_PROMPT === null) {
    // DEVAI_REVIEW_PROMPT is null, so assign the value of PROMPT to it
    DEVAI_REVIEW_PROMPT = PROMPT;
  }
  // Build the full prompt using the template.
  const fullPrompt = `${DEVAI_REVIEW_PROMPT}
    ${CODE_LABEL}
    ${selectedCode}
    ${REVIEW_LABEL}
    `;

  const result = await model.generateContent(fullPrompt);
  const response = await result.response;
  const comment = response.text();  

  // Insert before selection
  editor.edit((editBuilder) => {
    // Copy the indent from the first line of the selection.
    const trimmed = selectedCode.trimStart();
    const padding = selectedCode.substring(0, selectedCode.length - trimmed.length);

    // TODO(you!): Support other comment styles.
    const commentPrefix = '# ';
    let pyComment = comment.split('\n').map((l: string) => `${padding}${commentPrefix}${l}`).join('\r');
    if (pyComment.search(/\n$/) === -1) {
      // Add a final newline if necessary.
      pyComment += "\n";
    }
    let reviewIntro = padding + commentPrefix + "Devai Code review: (generated)\n";
    editBuilder.insert(selection.start, reviewIntro);
    editBuilder.insert(selection.start, pyComment);
  });
}
