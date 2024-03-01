from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
import requests
import threading
from linkedin import Linkedin
# Assuming linkedin_scraper.py contains the Linkedin class with the linkJobApply method
# from linkedin_scraper import Linkedin

app = FastAPI()

class ApplyModel(BaseModel):
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

class OpenAIResponseModel(BaseModel):
    answers: list

@app.get("/")
def home():
    return {"message": "HOME"}

@app.post("/apply")
def apply_jobs(apply_details: ApplyModel, background_tasks: BackgroundTasks):
    # Here, you might want to use the apply_details for something relevant to your LinkedIn logic.
    # For simplicity, we're just initiating the LinkedIn application process in the background.
    background_tasks.add_task(run_linkedin_application, apply_details)
    return {"message": "Application process initiated. Running in background."}
def run_linkedin_application(apply_details: ApplyModel):
    # Convert Pydantic model to dict using model_dump
    apply_details_dict = apply_details.model_dump()
    linkedin_app = Linkedin(apply_details=apply_details_dict)
    linkedin_app.linkJobApply()



@app.post("/ask-gpt4/")
async def ask_gpt4(question: str):
    response = requests.post(
        "https://api.openai.com/v1/engines/davinci-codex/completions",
        headers={
            "Authorization": f"Bearer {your_openai_api_key}",  # Replace with your OpenAI API Key
            "Content-Type": "application/json",
        },
        json={
            "prompt": question,
            "max_tokens": 150
        },
    )
    if response.status_code == 200:
        return OpenAIResponseModel(answers=response.json()["choices"][0]["text"])
    else:
        return {"error": "Failed to get a response from OpenAI GPT-4"}

# Ensure you have `uvicorn` installed to run FastAPI apps
# Run the app with: uvicorn app:app --reload

