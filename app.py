from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from linkedin import Linkedin  # Ensure this import path is correct for your project structure

app = FastAPI()

class ApplicationData(BaseModel):
    email: str
    password: str
    additional_questions_path: str

@app.get("/")
def read_root():
    return {"message": "HOME"}

@app.post("/apply")
def apply_jobs(application_data: ApplicationData):
    try:
        # Initialize and run the Linkedin bot
        bot = Linkedin(
            email=application_data.email, 
            password=application_data.password, 
            additional_questions_path=application_data.additional_questions_path
        )
        result = bot.linkJobApply()  # Ensure this method returns some result or status
        return {"message": "Application process completed.", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
