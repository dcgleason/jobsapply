from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr, constr
import threading
# Assuming linkedin_scraper.py contains the Linkedin class with the linkJobApply method
from linkedin_scraper import Linkedin

app = FastAPI()

class ApplyModel(BaseModel):
    email: EmailStr
    phone_country_code: constr(regex=r'^\+\d{1,3}$')
    mobile_phone_number: constr(regex=r'^\d{10,15}$')
    has_technical_experience: bool
    has_teaching_experience: bool
    is_us_citizen: bool
    has_bachelors_degree: bool
    years_experience_servicenow: int

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
    # Initialize the LinkedIn application logic with any necessary details from apply_details.
    # For this example, we're not passing anything to Linkedin(), but you might want to customize this.
    linkedin_app = Linkedin()
    linkedin_app.linkJobApply()

# Ensure you have `uvicorn` installed to run FastAPI apps
# Run the app with: uvicorn app:app --reload
