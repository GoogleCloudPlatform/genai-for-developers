## DEVAI CLI - Image review

This example demonstrates ways to integrate LLM models into a custom command line utility for use by developers both locally and part of CICD pipeline to automate image review.

### CLI Setup steps

Follow this tutorial to setup DEVAI CLI - [setup-cli](../setup-cli.md).


### Image review command:

Update the path to the image in the cloned repository:
```
devai review image \
  -f "~/genai-for-developers/images/code-review-github.png" \
  -p "Review and summarize this diagram"  
```

### Sample output:
---
This diagram outlines a code review automation workflow utilizing Gemini, GitHub, JIRA, and other Google Cloud components.

**Here is a breakdown of the process:**

1. **Code Commit:** Happy GCP Users commit new code to a GitHub repository.
2. **Code Review Request:** A GitHub action, triggered by the commit, uses a custom prompt and the 'devai cli' to send the codebase to Vertex AI's Gemini Pro model for review.
3. **Gemini Review:** Gemini analyzes the code for performance, refactoring opportunities, and any other custom criteria specified in the prompt. It then sends its findings back. 
4. **Jira Issue Creation:**  Based on Gemini's response, the GitHub action automatically generates a new Jira issue detailing the review findings. This issue facilitates tracking and addressing the identified areas for improvement.

**Additional components:**

* **LangSmith:** Potentially used for analyzing and understanding the LLM (Gemini) behavior, though its exact role isn't explicitly defined in the diagram.
* **React Agent & LLM Traces:**  These likely represent components within the system responsible for interacting with Gemini and collecting data about its decision-making process.

**In summary:** This workflow automates the code review process, leveraging the power of Gemini's GenAI capabilities to identify potential issues and streamline developer workflows. By integrating with GitHub and JIRA, it ensures seamless incorporation of the AI-powered insights into existing development processes.

---

### Input Image:
![Code Review](../../../images/code-review-github.png "Code Review")
