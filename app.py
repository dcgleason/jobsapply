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

from typing import List, Optional
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dotenv import load_dotenv
import os
from schemas import ApplyDetails


from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

load_dotenv() # Load environment variables from a .env file



class OpenAIResponseModel(BaseModel):
    answers: str





app = FastAPI()

# Initialize your APIRouter
router = APIRouter()

app.include_router(router)

# Define your request and response models
class GPT4Request(BaseModel):
    question: str
    question_type: str
    options: Optional[List[str]] = None

class GPT4Response(BaseModel):
    answers: str


@app.get("/")
def home():
    return {"message": "HOME"}

@app.post("/apply")
def apply_jobs(apply_details: ApplyDetails, background_tasks: BackgroundTasks):
    # Pass the entire ApplyDetails instance, which includes the configuration
    background_tasks.add_task(run_linkedin_application, apply_details)
    return {"message": "Application process initiated. Running in background."}

def run_linkedin_application(apply_details: ApplyDetails):
    # No need to call model_dump() or dict() anymore
    # Directly pass apply_details object which now includes user-configured settings
    linkedin_app = Linkedin(apply_details=apply_details)
    linkedin_app.linkJobApply()

# Define your route
@app.post("/ask-gpt4/", response_model=GPT4Response)
async def ask_gpt4(request: GPT4Request):
    # Assuming you have your OpenAI API key stored in an environment variable
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured.")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-4-0125-preview",  
        "prompt": generate_prompt(request.question, request.question_type, request.options),
        "temperature": 0.7,
        "max_tokens": 150,
        "n": 1,
        "stop": None,
    }
    
    response = requests.post("https://api.openai.com/v1/completions", json=data, headers=headers)
    
    if response.status_code == 200:
        answer = response.json()['choices'][0]['text'].strip()
        return GPT4Response(answers=answer)
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch response from OpenAI.")

def generate_prompt(question: str, question_type: str, options: Optional[List[str]] = None) -> str:
    """
    Generate a prompt for GPT-4 based on the question, its type, and optional options.
    """
    prompt = f"Question: {question}\nType: {question_type}\n"
    if options:
        options_text = '\n'.join([f"Option {index + 1}: {option}" for index, option in enumerate(options)])
        prompt += f"Options:\n{options_text}\nAnswer:"
    else:
        prompt += "Answer:"
    return prompt

# Ensure you have `uvicorn` installed to run FastAPI apps
# Run the app with: uvicorn app:app --reload

