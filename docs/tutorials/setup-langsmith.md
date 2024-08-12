## LLM tracing 

To see detailed debug information, follow steps below to enable LangSmith integration.

### LangSmith LLM tracing configuration

Create a LangSmith account and generate a Service API key in the Settings section. https://docs.smith.langchain.com/ 

Set environment variables required for LangSmith integration. Replace Service API key before running the commands.

```
export LANGCHAIN_API_KEY=langsmith-service-api-key
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
```

To avoid exposing sensitive information in the terminal, the best practice is to use read -s this is a secure way to set environment variables without value showing up in the console’s command history. After running it, you have to paste the value and hit enter.
