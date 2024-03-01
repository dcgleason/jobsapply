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
import openai

import httpx
from schemas import ApplyDetails



from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

load_dotenv() # Load environment variables from a .env file



class OpenAIResponseModel(BaseModel):
    answers: str





app = FastAPI()

# Initialize your APIRouter
router = APIRouter()

# Define your route
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

class GPT4Request(BaseModel):
    question: str
    question_type: str = "text"
    options: Optional[List[str]] = None

class GPT4Response(BaseModel):
    answers: str

@app.post("/ask-gpt4/", response_model=GPT4Response)
async def ask_gpt4(request: GPT4Request):
    # Your OpenAI API key should be loaded from environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured.")
    
    openai.api_key = OPENAI_API_KEY

    # Constructing the prompt for OpenAI API
    prompt = generate_prompt(request.question, request.question_type, request.options)

    try:
        response = openai.Completion.create(
            engine="gpt-4",  # Update this to the GPT-4 model you have access to
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            top_p=1,
            n=1,
            stop=None,
            logprobs=None,
        )
        # Extracting the text from the response
        answer = response.choices[0].text.strip()
        return GPT4Response(answers=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_prompt(question: str, question_type: str, options: Optional[List[str]] = None) -> str:
    """
    Generate a prompt for GPT-4 based on the question, its type, and optional options.
    """
    prompt = f"Question: {question}\nType: {question_type}\n"
    if options:
        options_text = "Options:\n" + "\n".join([f"{idx+1}. {opt}" for idx, opt in enumerate(options)]) + "\nAnswer:"
        prompt += options_text
    else:
        prompt += "Answer:"
    return prompt
# Ensure you have `uvicorn` installed to run FastAPI apps
# Run the app with: uvicorn app:app --reload

