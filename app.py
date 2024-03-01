from fastapi import FastAPI, BackgroundTasks
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

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

load_dotenv()  

class LinkedinCredentials(BaseModel):
    linkedin_email: EmailStr
    linkedin_password: str

class LinkedinConfig(BaseModel):
    credentials: LinkedinCredentials
    headless: bool
    chromeProfilePath: Optional[str] = None
    location: List[str]
    keywords: List[str]
    experienceLevels: List[str]
    datePosted: List[str]
    jobType: List[str]
    remote: List[str]
    salary: List[str]
    sort: List[str]
    blacklistCompanies: List[str] = []
    blackListTitles: List[str] = []
    followCompanies: bool
    preferredCv: int
    outputSkippedQuestions: bool
    useAiAutocomplete: bool
    onlyApplyCompanies: List[str] = []
    onlyApplyTitles: List[str] = []
    blockHiringMember: List[str] = []
    onlyApplyHiringMember: List[str] = []
    onlyApplyMaxApplications: List[str] = []
    onlyApplyMinApplications: List[str] = []
    onlyApplyJobDescription: List[str] = []
    blockJobDescription: List[str] = []
    onlyApplyMimEmployee: List[str] = []
    onlyApplyLinkedinRecommending: bool
    onlyApplySkilledBages: bool
    saveBeforeApply: bool
    messageToHiringManager: Optional[str] = None
    listNonEasyApplyJobsUrl: bool
    defaultRadioOption: int
    answerAllCheckboxes: Optional[bool] = None
    outputFileType: List[str]

class ApplyDetails(BaseModel):
    email: EmailStr
    phone_country_code: str = Field(..., min_length=1, max_length=4)
    mobile_phone_number: str = Field(..., min_length=5, max_length=15)
    has_technical_experience: bool
    has_teaching_experience: bool
    is_us_citizen: bool
    has_bachelors_degree: bool
    years_experience_servicenow: int
    favorite_technology: str
    reason_for_applying: str
    config: LinkedinConfig  # Use this to pass configuration dynamically





class OpenAIResponseModel(BaseModel):
    answers: str



app = FastAPI()




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



@app.post("/ask-gpt4/")
async def ask_gpt4(question: str, question_type: str, options: list = None):
    """
    Send a question to the OpenAI GPT-4 model specifically tailored for form completion.
    - `question`: The prompt or question to be answered.
    - `question_type`: The type of the question ("string", "radio", "select").
    - `options`: The options for "select" or "radio" type questions.
    """

    bearer_token = os.getenv("OPENAI_KEY")
    prompt = f"We're filling out a form and need to answer the following question accurately and succinctly: '{question}'. This is a {question_type} question."
    if options:
        prompt += f" The options are: {', '.join([f'{idx+1}. {opt}' for idx, opt in enumerate(options)])}. Provide your answer in numerical form to indicate the chosen option."

    response = requests.post(
        "https://api.openai.com/v1/completions",
        headers={
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4-turbo-preview",  # Specify the model here
            "prompt": prompt,
            "max_tokens": 50,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": ["\n"]
        },
    )
    if response.status_code == 200:
        answer = response.json()["choices"][0]["text"].strip()
        # Post-process the answer based on the question type if necessary
        if question_type in ["radio", "select"] and options:
            # Ensure the answer is a valid option index
            try:
                answer_idx = int(answer) - 1
                if answer_idx < 0 or answer_idx >= len(options):
                    raise ValueError("Invalid option number")
                return OpenAIResponseModel(answers=options[answer_idx])
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid answer format for the question type")
        return OpenAIResponseModel(answers=answer)
    else:
        raise HTTPException(status_code=500, detail="Failed to get a response from OpenAI GPT-4")

# Ensure you have `uvicorn` installed to run FastAPI apps
# Run the app with: uvicorn app:app --reload

