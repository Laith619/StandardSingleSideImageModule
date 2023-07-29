import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field
import openai
import os
import json
import re

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # get the API key from the environment variable

class ProductInput(BaseModel):
    """Inputs for analyse_product"""
    content: str = Field(description="Content for Amazon Aplus Content")

app = FastAPI()

# Define a function to read a prompt from a file
def read_prompt_from_file(filename):
    try:
        # Attempt to open the file and read its content
        with open(filename, 'r') as file:
            content = file.read()
            # Remove special characters
            cleaned_content = re.sub('[^a-zA-Z0-9 \n.]', '', content)
            return cleaned_content
    except FileNotFoundError:
        # Print an error message if the file is not found
        print(f"File {filename} not found.")
        return None

# read the rules from file
rules_content = read_prompt_from_file('rules.txt')

def analyse_product_function(product_input: ProductInput):
    content = product_input.content

    query = f"Please Create high converting, interesting to read Amazon Aplus Content Standard Image Sidebar Module using the following information: {content} "

    system_message = read_prompt_from_file('Aplus.txt')

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": "Here is a product listing:"},
        {"role": "user", "content": content},
        {"role": "user", "content": "Please Create Amazon A+ Content using the following information."}
    ]

    # Log the messages that are being sent
    print("Sending the following messages to OpenAI:")
    for message in messages:
        print(f"Role: {message['role']}, Content: {message['content']}")

    function_descriptions = [
    {
        "name": "Create_Amazon_Aplus_Content",
        "description": "create Amazon Aplus Content Standard Single Side Image Module.",
        "parameters": {
            "type": "object",
            "properties": {
                "Rules": {
                    "type": "string",
                    "description": "ensure that the following rules are followed for: " + (rules_content if rules_content else "No rules provided.")
                },  
                "Headline": {
                    "type": "string",
                    "description": "Create a headline for the module no longer than 160 characters. the headline is a blend of creativity strategic keyword usage, and clear understanding of the product's unique selling proposition"
                },                        
                "body": {
                    "type": "string",
                    "description": "Create a body for the module no longer than 1000 characters. The body should be a compelling blend of detailed product features and benefits, and brand story, all woven together with SEO-optimized language and a clear call-to-action. It's designed to provide comprehensive product information in an engaging way to convert potential customers into buyers"
                },
                "imageALT": {
                    "type": "string",
                    "description": "Create image alt text that is maximum of 100 characters."
                }    
            },
            "required": ["Headline", "body", "imageALT"]
        }
    }
]

   
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        functions=function_descriptions,
        function_call="auto"
    )

    # Extract the content from the response
    assistant_message = response['choices'][0]['message']
    function_call = assistant_message['function_call']
    arguments_json = function_call['arguments']

    # Convert the JSON string to a Python dictionary
    arguments_dict = json.loads(arguments_json)

    # Extract the individual variables
    headline = arguments_dict['Headline']
    body = arguments_dict['body']
    imageALT = arguments_dict['imageALT']

    print(f"Headline: {headline}")
    print(f"body: {body}")
    print(f"imageAlt: {imageALT}")

    return {
        "Headline": headline,
        "Body": body,
        "imageALT": imageALT
    }


@app.post("/")
def analyse_product_endpoint(product_input: ProductInput):
    return analyse_product_function(product_input)
