# Gemini CLI ADK Agent Prototype

This repository serves as a prototype for building ADK (Agent Development Kit) agents using the Gemini CLI. It demonstrates how to leverage existing context files and custom commands to streamline the agent development process.

## Key Files:

*   **`GEMINI.md`**: Provides instructions on how to use the reference documentation to build ADK agents.
*   **[`AGENTS.md`](https://github.com/google/adk-python/blob/main/AGENTS.md)**: Contains detailed information and best practices for agent development.
*   **[`llms-full.txt`](https://github.com/google/adk-python/blob/main/llms-full.txt)**: Offers comprehensive details about Large Language Models (LLMs) for integration into ADK agents.

## Custom Commands

This project includes two custom commands defined in the `.gemini/commands` directory:

### `/plan:new` (Planning Mode)

**Description:** Generates a plan for a feature based on a description.

**Prompt Summary:**
You are in **Planning Mode**. Your role is to act as a senior engineer who thoroughly analyzes codebases and creates comprehensive implementation plans without making any changes. You are forbidden from making any modifications to the codebase or the system, with the single exception of the final plan file. Your one and only output is to write a single markdown file named after the feature into the `plans` directory.

### `/plan:impl` (Implementation Mode)

**Description:** Implementation mode. Implements a plan for a feature based on a description.

**Prompt Summary:**
You are in **Implementation Mode**. Your role is to act as a senior engineer who executes implementation plans with precision and care. You must follow the implementation plan exactly as written. You will update the plan file to track progress, and you must maintain code quality standards.
