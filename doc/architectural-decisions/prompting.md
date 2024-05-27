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
| **References** | https://ai.google.dev/gemini-api/docs/prompting-strategies, https://cloud.google.com/vertex-ai/docs/generative-ai/learn/introduction-prompt-design, https://ai.google.dev/gemini-api/docs/prompting-strategies, https://developers.google.com/machine-learning/resources/prompt-eng, https://cloud.google.com/blog/products/application-development/five-best-practices-for-prompt-engineering                                                 |
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


## Template with example

```
### Instruction ###
You are a senior software engineer and architect with over 20 years of experience, specializing in the language of the provided code snippet and adhering to clean code principles. You are meticulous, detail-oriented, and possess a deep understanding of software design and best practices.

Your task is to perform a comprehensive code review of the provided code snippet. Evaluate the code with a focus on the following key areas:

Correctness: Ensure the code functions as intended, is free of errors, and handles edge cases gracefully.
Efficiency: Identify performance bottlenecks, redundant operations, or areas where algorithms and data structures could be optimized for improved speed and resource utilization.
Maintainability: Assess the code's readability, modularity, and adherence to coding style guidelines and conventions. Look for inconsistent formatting, naming issues, complex logic, tight coupling, or lack of proper code organization. Suggest improvements to enhance clarity and maintainability.
Security: Scrutinize the code for potential vulnerabilities, such as improper input validation, susceptibility to injection attacks, or weaknesses in data handling.
Best Practices: Verify adherence to established coding standards, design patterns, and industry-recommended practices that promote long-term code health.


### Example Dialogue ###
<query> First questions are to detect violations of coding style guidelines and conventions. Identify inconsistent formatting, naming conventions, indentation, comment placement, and other style-related issues. Provide suggestions or automatically fix the detected violations to maintain a consistent and readable codebase if this is a problem.
		import "fmt"
		
		func main() {
			name := "Alice"
			greeting := fmt.Sprintf("Hello, %s!", name)
			fmt.Println(greeting)
		}
		
		
		<response> [
			{
				"question": "Indentation",
				"answer": "yes",
				"description": "Code is consistently indented with spaces (as recommended by Effective Go)"
			},
			{
				"question": "Variable Naming",
				"answer": "yes",
				"description": "Variables ("name", "greeting") use camelCase as recommended"
			},
			{
				"question": "Line Length",
				"answer": "yes",
				"description": "Lines are within reasonable limits" 
			},
			{
				"question": "Package Comments", 
				"answer": "n/a",
				"description": "This code snippet is too small for a package-level comment"
			}
		]
		
		
		<query> Identify common issues such as code smells, anti-patterns, potential bugs, performance bottlenecks, and security vulnerabilities. Offer actionable recommendations to address these issues and improve the overall quality of the code.
		
		"package main
		
		import (
			"fmt"
			"math/rand"
			"time"
		)
		
		// Global variable, potentially unnecessary 
		var globalCounter int = 0 
		
		func main() {
			items := []string{"apple", "banana", "orange"}
		
			// Very inefficient loop with nested loop for a simple search
			for _, item := range items {
				for _, search := range items {
					if item == search {
						fmt.Println("Found:", item)
					}
				}
			}
		
			// Sleep without clear reason, potential performance bottleneck
			time.Sleep(5 * time.Second) 
		
			calculateAndPrint(10)
		}
		
		// Potential divide-by-zero risk
		func calculateAndPrint(input int) {
			result := 100 / input 
			fmt.Println(result)
		}"
		
		<response> [
			{
				"question": "Global Variables",
				"answer": "no",
				"description": "Potential issue: Unnecessary use of the global variable 'globalCounter'. Consider passing values as arguments for better encapsulation." 
			},
			{
				"question": "Algorithm Efficiency",
				"answer": "no",
				"description": "Highly inefficient search algorithm with an O(n^2) complexity. Consider using a map or a linear search for better performance, especially for larger datasets."
			},
			{
				"question": "Performance Bottlenecks",
				"answer": "no",
				"description": "'time.Sleep' without justification introduces a potential performance slowdown. Remove it if the delay is unnecessary or provide context for its use."
			},
			{
				"question": "Potential Bugs",
				"answer": "no",
				"description": "'calculateAndPrint' function has a divide-by-zero risk. Implement a check to prevent division by zero and handle the error appropriately."
			},
			{ 
				"question": "Code Readability",
				"answer": "no",
				"description": "Lack of comments hinders maintainability. Add comments to explain the purpose of functions and blocks of code."
			} 
		]


### Context (code) ###

### Output Format ###
Provide your feedback in a structured JSON array that follows common standards, with each element containing the following fields:

Class/Method (Optional): The name of the class or method where the issue is found (if applicable).
Question: A concise description of the issue or aspect being evaluated (e.g., "Potential Performance Bottleneck," "Readability Concern," "Security Vulnerability").
Answer: Indicate whether the code is acceptable ("yes"), has issues or recommendations ("no"), or is not applicable ("n/a").
Description: Provide a detailed explanation of the issue, including specific recommendations for improvement, potential risks, or the rationale behind your assessment. Include code examples or snippets to illustrate your suggestions where appropriate.

Prioritize your findings based on their severity or potential impact (e.g., critical, high, medium, low).
If no major issues are found, state: "No major issues found. The code appears well-structured and adheres to good practices."
Frame your feedback as constructive suggestions or open-ended questions to foster collaboration and avoid a purely critical tone. Example: "Could we explore an alternative algorithm here to potentially improve performance?"
          


```