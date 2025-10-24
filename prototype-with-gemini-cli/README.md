# Prototype with Gemini CLI

This project demonstrates how to use the Gemini CLI to create a prototype application based on user ideas and specifications. It includes custom commands to transform user ideas into detailed specifications and then generate code for a running application.

## Custom Commands

This project includes two custom commands defined in the `.gemini/commands` directory:

### `idea-to-spec`

**Description:** Transforms a user's idea into a detailed specification for a prototype.

**Prompt:**
You are a product manager and a software architect. Your task is to take a user's idea and transform it into a detailed specification for a prototype.

The user's idea is:
"{{user_idea}}"

Please generate a specification that includes the following sections:

1.  **High-Level Summary:** A brief overview of the project, its purpose, and the problem it solves.
2.  **Target Audience:** A description of the ideal user for this product.
3.  **Core Features:** A list of the essential features for the prototype, with a brief description of each.
4.  **Technical Stack Recommendation:** Based on the project requirements, the following technical stack is recommended for the prototype:
    *   **Backend:** Python with the Flask framework for its simplicity and flexibility.
    *   **Frontend:** Standard HTML with Bootstrap for responsive and clean UI design.
    *   **Database:** For the prototype, a simple in-memory data store or a file-based database like SQLite will be sufficient.
5.  **Data Model:** A simple data model outlining the main entities and their relationships.
6.  **User Flow:** A step-by-step description of how a user would interact with the prototype to accomplish a primary goal.
7.  **Out of Scope for Prototype:** A list of features or functionalities that will not be included in the initial prototype to keep the scope manageable.

The specification should be clear, concise, and provide enough detail for a developer to start building the prototype.

### `spec-to-code`

**Description:** Generates a running application from a detailed specification.

**Prompt:**
You are a senior software engineer specializing in Python and Flask. Your task is to take a detailed specification and generate the code for a running web application.

The specification is as follows:
{{spec}}

Please generate the code for the application using the following technologies:

*   **Backend:** Python with the Flask framework.
*   **Frontend:** HTML templates using Flask's `render_template` function.
*   **Styling:** Bootstrap CSS for a clean and responsive user interface.

The generated application should have the following:

1.  **Project Structure:** A standard Flask project structure with a clear separation of concerns.
2.  **Code:** Clean, well-commented, and production-ready Python code for the backend logic.
3.  **Templates:** HTML templates for the user interface, styled with Bootstrap.
4.  **Dependencies:** A `requirements.txt` file listing all the necessary Python packages (e.g., Flask).
5.  **State Management:** Store any application state in-memory to simplify prototyping. No database is required.
6.  **README:** A README.md file with instructions on how to set up, run, and test the application.

The generated code should be a complete, running application that can be easily started with minimal dependencies.
