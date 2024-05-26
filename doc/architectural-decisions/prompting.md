# Prompt Engineering

| Field          | Description                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------- |
| **Date**       | 26th May 2024                                                                       |
| **Status**     | Proposed                        |
| **Context**    | Decide on the best structure to use for the prompts in `devai` to make them more robust and meet best practices to provide the most useful responses.                                              |
| **Decision**   | 4 core sections (Instructions, Context, Output format and Example Dialogue [OPTIONAL])             |
| **Rationale**  | It seemed the simplest structure based on many examples and best practices guides.            |
| **Consequences** | A consistent approach to creating prompts to be used for existing and new features in `devai` which should simplify creation and troubleshooting. The prompts will need to be reviewed as more is learnt about prompt engineering and the LLM's evolve. |
| **Participants** | robedwards@                                                          | 
| **References** | https://ai.google.dev/gemini-api/docs/prompting-strategies                                                 |
| **Notes**      | N/A                        |


Prompt engineering is the method of creating and refining input text or instructions, known as prompts, to effectively communicate with and guide AI models, particularly large language models (LLMs), to generate desired responses. It involves understanding the model's strengths and weaknesses, providing clear and specific instructions, utilizing contextual information, and iterating through different prompt variations to achieve optimal results.

## Prompt engineering is crucial for several reasons:

* It improves the performance of AI models by providing clear instructions and context, leading to more accurate and relevant outputs.
* It helps reduce biases and harmful responses by carefully controlling the input and guiding the AI's focus.
* It increases control and predictability over the AI's behavior, ensuring consistent and desired outcomes.
* It enhances the user experience by making interactions with AI models more intuitive and satisfying.

## Best Practices for Prompt Engineering

 * Understand the Model: Know the model's strengths, weaknesses, and limitations to craft effective prompts and avoid errors.
 * Be Specific: Tailor prompts to your desired outcome, providing clear instructions and avoiding ambiguity.
 * Use Context: Include relevant information, examples, or personas in prompts to help the model understand your request better.
 * Provide Examples: Give the model examples of desired input-output pairs to guide its responses.
 * Experiment and Iterate: Try different prompt variations, keywords, and structures to discover what works best.
 * Chain-of-Thought Prompting: Break down complex problems into smaller steps and prompt the model to provide reasoning for each step.

## Prompt Structure for `devai`

The prompt structure to be used for `devai` is  

### Instruction ### 
Clearly state the task, such as "Review the following code for potential errors and optimizations."

### Context (code) ### 
Code snippet or file to be reviewed passed.
 
### Output Format ### 
Specify the type of feedback expected, e.g., "List potential errors, suggest optimizations, and provide an overall assessment."


## Example Prompts for Application Development

 * Text Summarization: "Summarize the main points of this article in three sentences."
 * Code Generation: "Write a Python function to calculate the factorial of a number."
 * Image Generation: "Generate an image of a cat sitting on a chair."
 * Translation: "Translate the following English text to French: 'Hello, how are you?'"
 * Question Answering: "What are the benefits of using renewable energy sources?"



### Code Review Example

Here's an example prompt designed for code review, incorporating persona, task, context, and format:

Persona: You are a senior software engineer with expertise in Python and a deep understanding of clean code principles. You are meticulous, detail-oriented, and have a knack for identifying potential issues and optimizations in code.

Task: Thoroughly review the provided Python code snippet for the following:

 * Correctness: Ensure the code functions as intended, without errors or unexpected behavior.
 * Efficiency: Identify potential performance bottlenecks or areas where the code could be optimized for speed or resource usage.
 * Readability: Assess the code's clarity and adherence to best practices, suggesting improvements to make it more maintainable.
 * Security: Look for potential vulnerabilities or weaknesses that could be exploited.

Context:

Python
```
def calculate_discount(price, discount_percentage):
    if discount_percentage < 0 or discount_percentage > 100:
        raise ValueError("Discount percentage must be between 0 and 100")
    discount_amount = price * (discount_percentage / 100)
    discounted_price = price - discount_amount
    return discounted_price
```

Format:

Provide your feedback in the following structured format:

 * Overall Assessment: A brief summary of your overall impression of the code's quality.
 * Potential Issues: A list of any errors, bugs, or potential problems you identified.
 * Optimization Suggestions: Specific recommendations for improving the code's efficiency or performance.
 * Readability Enhancements: Suggestions for improving the code's clarity, structure, or adherence to best practices.
 * Security Concerns: Any potential security risks or vulnerabilities you found.


