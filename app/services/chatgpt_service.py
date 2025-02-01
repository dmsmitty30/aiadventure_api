from openai import OpenAI
from pydantic import BaseModel
import os
import re
import asyncio
from dotenv import load_dotenv

load_dotenv()  # Load the .env file

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

def regexp_extract(string,pattern):
    match = re.search(pattern, string)
    if match:
        return match.group(1)

def clean_option(text):
    return re.sub(r"\s*###OPTION###\s*", "", text).strip()

def null_to_empty_string(value):
    return "" if value is None else value

class Story(BaseModel):
    title: str
    synopsis: str
    text: str
    options: list[str]

class StoryNode(BaseModel):
    text: str 
    options: list[str]



def developerMessage(message:str):
    return {"role":"developer", "content":message}
def userMessage(message:str):
    return {"role":"user", "content":message}
def assistantMessage(message:str):
    return {"role":"assistant", "content":message}

# Set the OpenAI API key

async def askOpenAI(prompt):
    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}])
    content = response.choices[0].message.content
    print("RAW CONTENT/n--------"+content+"/n---------")
    return content

async def askOpenAI_structured(context:dict, userPrompt:str, responseSchema):

    messages=context
    messages.append(userPrompt)

    print(messages)
    schema = {"new": Story, "node": StoryNode}


    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,        
        response_format=schema[responseSchema],
    )

    response = completion.choices[0].message.content
    return response




