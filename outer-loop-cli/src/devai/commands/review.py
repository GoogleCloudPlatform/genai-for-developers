# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import click
from devai.util.file_processor import format_files_as_string
from vertexai.generative_models import GenerativeModel, ChatSession

# Uncomment after configuring JIRA and GitLab env variables - see README.md for details

# from devai.commands.jira import create_jira_issue
# from devai.commands.gitlab import create_gitlab_issue_comment

parameters = {
    "max_output_tokens": 2048,
    "temperature": 0.2
}

@click.command(name='code')
@click.option('-c', '--context', required=False, type=str, default="")
def code(context):
    #click.echo('code')
    
    source='''
CODE:
{}

'''
    qry='''
INSTRUCTIONS:
You are an experienced software architect renowned for your ability to identify code quality issues, optimization opportunities, and adherence to best practices. Conduct a thorough code review of the provided codebase with the following focus:

Key Areas

Efficiency: Identify performance bottlenecks, redundant operations, or areas where algorithms and data structures could be improved for enhanced speed and resource usage.
Maintainability: Assess code readability, modularity, and the ease of future changes. Look for overly complex logic, tight coupling, or lack of proper code organization.
Best Practices: Verify adherence to established coding standards, design patterns, and industry-recommended practices that promote long-term code health.
Security: Scrutinize the code for potential vulnerabilities like improper input validation, susceptibility to injection attacks, or weaknesses in data handling.
Output Guidance

Structure:  Organize your findings by class and method names. This provides clear context for the issues and aids in refactoring. 

Tone: Frame your findings as constructive suggestions or open-ended questions. This encourages collaboration and avoids a purely critical tone. Examples:

"Could we explore an alternative algorithm here to potentially improve performance?"
"Would refactoring this logic into smaller functions enhance readability and maintainability?"
Specificity:  Provide detailed explanations for each issue. This helps the original developer understand the reasoning and implement effective solutions.

Prioritization: If possible, indicate the severity or potential impact of each issue (e.g., critical, high, medium, low). This helps prioritize fixes.

No Issues:  If your review uncovers no significant areas for improvement, state "No major issues found. The code appears well-structured and adheres to good practices."
'''

    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = GenerativeModel("gemini-1.0-pro")
    code_chat = code_chat_model.start_chat()
    code_chat.send_message(qry)
    response = code_chat.send_message(source)

    click.echo(f"Response from Model: {response.text}")

    #create_jira_issue("Code Review Results", response.text)
    # create_gitlab_issue_comment(response.text)


@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def performance(context):
    #click.echo('performance')
    
    source='''
CODE:
{}

'''
    qry='''
INSTRUCTIONS:
You are a seasoned application performance tuning expert with deep knowledge of Java's nuances. Conduct a meticulous code review focused on identifying performance pitfalls and optimization opportunities within the codebase. Pay close attention to:

Performance Bottlenecks:

Inefficient Operations: Pinpoint constructs known to be slow in the language, such as excessive string concatenation, unnecessary object creation, or suboptimal loop structures.
I/O-bound Operations: Examine file access, database queries, and network communication calls that could introduce latency.
Algorithmic Complexity: Analyze algorithms used for time and space complexity. Look for potential improvements using more efficient data structures or algorithms.
Memory Management:

Memory Leaks: Identify objects that are no longer referenced but not garbage collected, leading to gradual memory consumption.
Memory Bloat: Look for unnecessary object allocations, the use of overly large data structures, or the retention of data beyond its useful life.
Concurrency:

Race Conditions: Hunt for scenarios where multiple threads access shared data without proper synchronization, leading to unpredictable results.
Deadlocks: Detect situations where threads hold locks on resources while waiting for each other, causing the application to hang.
Output Guidance:

Structure:  Organize your findings by class and method names. This provides clear context for the issues and aids in refactoring. 

Tone: Frame your findings as constructive suggestions or open-ended questions. This encourages collaboration and avoids a purely critical tone. Examples:

"Could we explore an alternative algorithm here to potentially improve performance?"
"Would refactoring this logic into smaller functions enhance readability and maintainability?"
Specificity:  Provide detailed explanations for each issue. This helps the original developer understand the reasoning and implement effective solutions.

Prioritization: If possible, indicate the severity or potential impact of each issue (e.g., critical, high, medium, low). This helps prioritize fixes.

No Issues:  If your review uncovers no significant areas for improvement, state "No major issues found. The code appears well-structured and adheres to good practices."
'''
    # Load files as text into source variable
    source=source.format(format_files_as_string(context))

    code_chat_model = GenerativeModel("gemini-1.0-pro")
    code_chat = code_chat_model.start_chat()
    code_chat.send_message(qry)
    response = code_chat.send_message(source)

    click.echo(f"Response from Model: {response.text}")

    # create_jira_issue("Performance Review Results", response.text)
    # create_gitlab_issue_comment(response.text)

@click.command()
@click.option('-c', '--context', required=False, type=str, default="")
def security(context):
    #click.echo('simple security')

    source='''
CODE: 
{}
'''
    qry='''
    INSTRUCTIONS:
You are a seasoned security expert with a keen eye for identifying vulnerabilities in web applications. Conduct a thorough security review of the attached codebase, focusing on the following critical areas:

Vulnerability Identification

Insecure Cookies: Check for cookies lacking proper security flags (HttpOnly, Secure), sensitive data in cookies, or inadequate expiration settings.
Insecure Session Management: Examine session generation, storage, transmission, timeout mechanisms, and potential for session hijacking or fixation.
SQL Injection: Scrutinize all database interactions for lack of input sanitization or parameterized queries that could allow malicious SQL code execution.
Cross-Site Scripting (XSS): Inspect input handling, output encoding, and content filtering to prevent the injection of malicious scripts into user-facing pages.
Other Common Vulnerabilities: Keep an eye out for potential vulnerabilities listed in the OWASP Top 10 (https://owasp.org/Top10/), such as improper access control, misconfigurations, and sensitive data exposure.
Report Guidance

Structure:  Organize your findings by class and method names. This provides clear context for the issues and aids in refactoring. 
Tone: Frame your findings as constructive suggestions or open-ended questions. This encourages collaboration and avoids a purely critical tone. Examples:

"Could we explore an alternative algorithm here to potentially improve performance?"
"Would refactoring this logic into smaller functions enhance readability and maintainability?"
Specificity:  Provide detailed explanations for each issue. This helps the original developer understand the reasoning and implement effective solutions.

Prioritization: If possible, indicate the severity or potential impact of each issue (e.g., critical, high, medium, low). This helps prioritize fixes.

No Issues:  If your review uncovers no significant areas for improvement, state "No major issues found. The code appears well-structured and adheres to good practices."
'''
    # Load files as text into source variable
    source=source.format(format_files_as_string(context))
    
    code_chat_model = GenerativeModel("gemini-1.0-pro")
    code_chat = code_chat_model.start_chat()
    code_chat.send_message(qry)
    response = code_chat.send_message(source)

    click.echo(f"Response from Model: {response.text}")

    # create_jira_issue("Security Review Results", response.text)
    # create_gitlab_issue_comment(response.text)


@click.group()
def review():
    pass

review.add_command(code)
review.add_command(performance)
review.add_command(security)