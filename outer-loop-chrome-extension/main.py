import os
import json
import functions_framework

import google.cloud.logging

import vertexai
from vertexai.language_models import TextGenerationModel

PROJECT_ID = os.environ.get('GCP_PROJECT', '-')
LOCATION = os.environ.get('GCP_REGION', '-')
client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()
log_name = "devai-cloudfunction-log"
logger = client.logger(log_name)


@functions_framework.http
def devai(request):
    logger.log(f"Received a request for Code Review")

    # Parse the request body
    request_json = request.get_json(silent=True)

    # Extract the data from the request body
    if request_json and 'data' in request_json:
        user_data = request_json['data']
        logger.log(f"Received data from user: {user_data}")
    else:
        user_data = "NO SOURCE PROVIDED"
        logger.log(user_data)

    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = TextGenerationModel.from_pretrained("text-bison")
    
    prompt = f'''
    You are and expert software developer reviewing code. 
    Review the code below and provide a review in HTML format.

    EXAMPLE INPUT:def average(x, y):
    return x - y

result = average(a, b)
print(f"The average of a and b is: result")
    
    EXAMPLE OUTPUT: <h1>Code Review</h1>
<ul>
<li>The code is poorly formatted.
<li>The code is incorrect. The `average()` function should return the average of the two numbers, not the difference.
<li>The code is inefficient. The `average()` function can be written more efficiently using the following code: ``` def average(x, y): return (x + y) / 2 ```
</ul>    

    Review the following code twice and respond with any suggestions or better code examples: {user_data}
'''

    parameters = {
        "temperature": 1.0,
        "max_output_tokens": 256,
        "top_p": 1.0,
        "top_k": 40
    }
    prompt_response = model.predict(prompt, **parameters)
    clean_response = prompt_response.text.replace(
        "```html", "").replace("```", "")
    logger.log("PaLM Text Bison Model response: {clean_response}")

    # Format the response
    data = {}
    data['data'] = []
    data['data'].append({"details": clean_response})
    return json.dumps(data), 200, {'Content-Type': 'application/json'}
