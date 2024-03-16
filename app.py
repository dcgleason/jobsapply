from fastapi import FastAPI, BackgroundTasks, APIRouter
from pydantic import BaseModel, EmailStr, Field
import requests
import threading
from linkedin import Linkedin
# Assuming linkedin_scraper.py contains the Linkedin class with the linkJobApply method
# from linkedin_scraper import Linkedin

import requests
import logging
from fastapi import HTTPException
from openai import OpenAI

from typing import List, Optional
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dotenv import load_dotenv
import os
load_dotenv() # Load environment variables from a .env file

import openai

#client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import httpx
from schemas import ApplyDetails



from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field




class OpenAIResponseModel(BaseModel):
    answers: str





app = FastAPI()


class GPT4Request(BaseModel):
    question: str
    question_type: str = "text"
    options: Optional[List[str]] = None

class GPT4Response(BaseModel):
    answers: str

@app.get("/")
def home():
    return {"message": "HOME"}

@app.post("/apply")
async def apply_jobs(apply_details: ApplyDetails, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_linkedin_application, apply_details)
    return {"message": "Application process started in the background."}

async def run_linkedin_application(apply_details: ApplyDetails):
    linkedin_app = Linkedin(apply_details=apply_details, userInfo=apply_details.userInfo)
    logs = await linkedin_app.linkJobApply()
    return logs

class GPT4Request(BaseModel):
    question: str
    question_type: str = "text"
    options: Optional[List[str]] = None
    userInfo: str

class GPT4Response(BaseModel):
    answers: str

@app.post("/ask-gpt4/", response_model=GPT4Response)
def ask_gpt4(request: GPT4Request):
    # Your OpenAI API key should be loaded from environment variables
    client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
            
    # Constructing the prompt for OpenAI API
    prompt = generate_prompt(request.question, request.question_type, request.options)

    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that helps fill out forms for job applications based on user input."},
                {"role": "user", "content": f"{request.userInfo}\n\n{prompt}"}  # Include userInfo in the prompt
            ]
        )
        answer = completion.choices[0].message.content
        return GPT4Response(answers=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_prompt(question: str, question_type: str, options: Optional[List[str]] = None) -> str:
    """
    Generate a prompt for GPT-4 based on the question, its type, and optional options.
    """
    prompt = f"Statement: {question}\nType: {question_type}\n"

    if question_type == "string":
        prompt += "Please provide a concise and relevant answer to the statement based on the user's information.\n"
    elif question_type == "choice":
        if options:
            options_text = "Options:\n" + "\n".join([f"{opt}" for opt in options]) + "\n"
            prompt += options_text
            prompt += "Please select the option that best fits the given statement by providing the exact option text. The response should only contain the selected option text, without any additional characters or explanations. If none of the options are suitable, respond with 'None'.\n"
        else:
            raise ValueError("Options must be provided for question type 'choice'.")
    else:
        raise ValueError(f"Unsupported question type: {question_type}")

    prompt += "Answer:"
    return prompt
# Ensure you have `uvicorn` installed to run FastAPI apps
# Run the app with: uvicorn app:app --reload

